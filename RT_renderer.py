# renderer class

import RT_utility as rtu
import numpy as np
from PIL import Image as im
import math
import RT_pbar
import multiprocessing as mp
import time
from enum import Enum
from RT_utility import RenderType

_worker_camera = None
_worker_integrator = None
_worker_scene = None
_worker_sqrt_spp = None

def init_worker(camera, integrator, scene, sqrt_spp=None):
    global _worker_camera
    global _worker_integrator
    global _worker_scene
    global _worker_sqrt_spp

    _worker_camera = camera
    _worker_integrator = integrator
    _worker_scene = scene
    _worker_sqrt_spp = sqrt_spp

def generate_tiles(width, height, tile_size):
    tiles = []
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            x1 = min(x + tile_size, width)
            y1 = min(y + tile_size, height)
            tiles.append((x, x1, y, y1))
    return tiles

def compute_tile(tile):
    x0, x1, y0, y1 = tile

    width  = x1 - x0
    height = y1 - y0

    tile_data = np.zeros((height, width,3), dtype=np.float32)

    for j in range(y0, y1):
        for i in range(x0, x1):

            r = g = b = 0.0

            for spp in range(_worker_camera.samples_per_pixel):
                ray = _worker_camera.get_ray(i, j)
                sample = _worker_integrator.compute_scattering(
                    ray, _worker_scene, _worker_camera.max_depth
                )
                r += sample.r()
                g += sample.g()
                b += sample.b()


            tile_data[j - y0, i - x0, 0] = r
            tile_data[j - y0, i - x0, 1] = g
            tile_data[j - y0, i - x0, 2] = b

    return (x0, y0, tile_data)


def compute_tile_jittered(tile):
    x0, x1, y0, y1 = tile

    width  = x1 - x0
    height = y1 - y0

    tile_data = np.zeros((height, width, 3), dtype=np.float32)

    for j in range(y0, y1):
        for i in range(x0, x1):
            r = g = b = 0.0
            for s_j in range(_worker_sqrt_spp):
                for s_i in range(_worker_sqrt_spp):
                    ray = _worker_camera.get_jittered_ray(i, j, s_i, s_j)
                    sample = _worker_integrator.compute_scattering(
                        ray, _worker_scene, _worker_camera.max_depth
                    )
                    r += sample.r()
                    g += sample.g()
                    b += sample.b()

            tile_data[j - y0, i - x0, 0] = r
            tile_data[j - y0, i - x0, 1] = g
            tile_data[j - y0, i - x0, 2] = b

    return (x0, y0, tile_data)


class Renderer():

    def __init__(self, cCamera, iIntegrator, sScene) -> None:
        self.camera = cCamera
        self.integrator = iIntegrator
        self.scene = sScene
        pass


    # def render(self):
    #     # gather lights to the light list
    #     self.scene.find_lights()
    #     renderbar = RT_pbar.start_animated_marker(self.camera.img_width * self.camera.img_height)
    #     k = 0
    #     with mp.Pool(mp.cpu_count(),
    #                  initializer=init_worker,
    #                  initargs=(self.camera, self.integrator, self.scene)) as pool:
    #         for j, row in pool.imap_unordered(render_row,range(self.camera.img_height),chunksize=2):
    #             for i, pixel_color in enumerate(row):
    #                 self.camera.write_to_film(i, j, pixel_color)
    #             k += self.camera.img_width
    #             renderbar.update(k)
    #     renderbar.finish()
        
    def _get_compute_function(self,t:RenderType):
        if t == RenderType.JITTERED:
            sqrt_spp = int(math.sqrt(self.camera.samples_per_pixel))
            return sqrt_spp, compute_tile_jittered
        return None,compute_tile
    
    def render(self,type:RenderType = RenderType.NORMAL):
        # gather lights to the light list
        self.scene.find_lights()
        tile_size = self._compute_adaptive_tile_size(self.camera.img_width,self.camera.img_height,self.camera.samples_per_pixel)
        tiles = generate_tiles(
            self.camera.img_width,
            self.camera.img_height,
            tile_size
        )
        chunksize = max(4, min(16, len(tiles) // (mp.cpu_count() * 4)))
        # chunksize= 4
        k = -1
        sqrt,func = self._get_compute_function(type)
        print(f"Innitilizing with \nNumber of processor: {mp.cpu_count()}\nTile size: {tile_size}\nChunk size:{chunksize}")
        with mp.Pool(mp.cpu_count(),
                     initializer=init_worker,
                     initargs=(self.camera, self.integrator, self.scene,sqrt)) as pool:
            renderbar = RT_pbar.start_animated_marker(len(tiles))
            renderbar.update(1)
            for x0, y0, tile_data in pool.imap_unordered(func,tiles,chunksize=chunksize):
                self.camera.write_tile_to_film(x0, y0, tile_data)
                k+=1
                renderbar.update(k)
        renderbar.finish()

    def _compute_adaptive_tile_size(self, width, height, spp):
        cpu = mp.cpu_count()
        workload_factor = math.sqrt(spp)

        MIN_TILE_MULTIPLIER = 8
        target_tiles = int(cpu * 6 / max(1, workload_factor / 5))
        target_tiles = max(cpu * MIN_TILE_MULTIPLIER, target_tiles) 

        total_pixels = width * height
        tile_area    = total_pixels / target_tiles
        tile_size    = int(math.sqrt(tile_area))

        tile_size = max(16, min(128, tile_size))

        return tile_size

    def write_img2png(self, strPng_filename):
        png_film = self.camera.film * 255
        data = im.fromarray(png_film.astype(np.uint8))
        data.save(strPng_filename)


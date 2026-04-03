import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_light as rtl
import RT_texture as rtt
import RT_transformer as rttr
import psutil, os

# p = psutil.Process(os.getpid())
# p.nice(psutil.HIGH_PRIORITY_CLASS)

def createRoom(world):
    concreat_tex = rtt.ConcreteTexture(rtu.Color(1,1,1),2)
    concreat_mat = rtm.TextureColor(concreat_tex)
    white = rtm.Lambertian(rtu.Color(1,0.91,0.75))
    laminat_tex = rtt.ImageTexture("textures/laminate.jpg")
    laminat_mat = rtm.TextureColor(laminat_tex)

    #---- floor ----
    world.add_object(
        rto.Quad(
            rtu.Vec3(-100, 0 , -100),       # origin (shifted so center stays same)
            rtu.Vec3(200, 0, 0),           # width
            rtu.Vec3(0, 0, 200),           # depth
            laminat_mat
        )
    )

#     #---- right wall ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(-100, 0, -100),   # bottom-left
        rtu.Vec3(200, 0, 0),     # width (X)
        rtu.Vec3(0, 100, 0),     # height (Y)
        white
    )
)
# #     #---- left wall ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(-100, 0, 100),
        rtu.Vec3(200, 0, 0),
        rtu.Vec3(0, 100, 0),
        white
        )
    )

#     #---- back wall ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(60, 0, -100),
        rtu.Vec3(0, 0, 200),
        rtu.Vec3(0, 100, 0),
        white
        )
    )

    # # #---- top wall ----
    world.add_object(
        rto.Quad(
            rtu.Vec3(-100, 100 , -100),       # origin (shifted so center stays same)
            rtu.Vec3(200, 0, 0),           # width
            rtu.Vec3(0, 0, 200),           # depth
            white
        )
    )

    wall_y_min = 0
    wall_y_max = 100

    window_y_min = 15
    window_y_max = 47

    window_z_min = -36
    window_z_max = 80

    x = -50


    #---- bottom window part ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(x, wall_y_min, -100),
        rtu.Vec3(0, 0, 200),
        rtu.Vec3(0, window_y_min, 0),
        white
        )
    )

    #---- top window part ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(x, window_y_max, -100),  
        rtu.Vec3(0, 0, 200),              
        rtu.Vec3(0, wall_y_max - window_y_max, 0), 
        white
        )
    )
    
    #---- right window part ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(x, window_y_min, -100),   # start at left side
        rtu.Vec3(0, 0, window_z_min - (-100)),  # width in Z
        rtu.Vec3(0, window_y_max - window_y_min, 0),  # height
        white
        )
    )
    #---- left window part ----
    world.add_object(
    rto.Quad(
        rtu.Vec3(x, window_y_min, window_z_max),  # start at right side of window
        rtu.Vec3(0, 0, 100 - window_z_max),       # remaining width
        rtu.Vec3(0, window_y_max - window_y_min, 0),
        white
        )
    )
    

def renderRoom():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 1920
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 256
    main_camera.max_depth = 5
    main_camera.vertical_fov = 75
    main_camera.look_from = rtu.Vec3(-27, 21, -43)
    main_camera.look_at = rtu.Vec3(23,10,7)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)
    
    defocus_angle = 0
    focus_distance = (main_camera.look_at - main_camera.look_from).len()
    main_camera.init_camera(defocus_angle, focus_distance)

    sun_light = rtl.Diffuse_light(rtu.Color(1.0 , 0.94, 0.81),1,0.08,0.18)
    #---- Texture ----
    tex_checker_bw = rtt.ImageTexture("textures/blueprint.jpg")

    #---- Material ----
    mat_tex_checker_bw = rtm.TextureColor(tex_checker_bw)
    lambertian_black_mat = rtm.Lambertian(rtu.Color(0,0,0))
    metal_mat = rtm.Metal(rtu.Color(0,0,0),0.1)


    world = rts.Scene()
    
    #---- Plate ----
    world.add_object(
        rto.Quad(
            rtu.Vec3(-500, -0.5 , -500),       # origin (shifted so center stays same)
            rtu.Vec3(1000, 0, 0),           # width
            rtu.Vec3(0, 0, 1000),           # depth
            mat_tex_checker_bw
        )
    )
    createRoom(world)
    sofa = rttr.MeshTranformer.obj_mtl_to_mesh("model/sofa/tinker.obj",lambertian_black_mat,rtu.Vec3(50,0,-10))
    sofa.set_transform(35,rtu.Vec3(0,-90,0))
    world.add_object(sofa)

    table = rttr.MeshTranformer.obj_mtl_to_mesh("model/coffee_table/tinker.obj",metal_mat,rtu.Vec3(0,0,-10))
    table.set_transform(20,rtu.Vec3(0,90,0))
    world.add_object(table)

    flower = rttr.MeshTranformer.obj_mtl_to_mesh("model/flower_vase/tinker.obj",lambertian_black_mat,rtu.Vec3(0,11,-15))
    flower.set_transform(5)
    world.add_object(flower) 

    tv = rttr.MeshTranformer.obj_mtl_to_mesh("model/tv/tinker.obj",lambertian_black_mat,rtu.Vec3(-10,0,30))
    tv.set_transform(23,rtu.Vec3(0,180,0))
    world.add_object(tv) 

    sun = rto.Sphere(rtu.Vec3(-200,100,-10),5,sun_light)
    world.add_object(sun)

    intg = rti.Integrator(bSkyBG=False,roulette=True)

    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render(type=rtu.RenderType.JITTERED)
    renderer.write_img2png('test_1024_82.png')  



def renderCity():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 3840  
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 1
    main_camera.max_depth = 5
    main_camera.look_from = rtu.Vec3(4, 3.5, -4)
    main_camera.look_at = rtu.Vec3(0.2, 0.5, 0.2)
    main_camera.vertical_fov = 60
    main_camera.vec_up = rtu.Vec3(0, 1, 0)
    defocus_angle = 0
    focus_distance = (main_camera.look_at - main_camera.look_from).len()
    main_camera.init_camera(defocus_angle, focus_distance)

    tex_checker_bw = rtt.CheckerTexture(0.32, rtu.Color(0,0, 0), rtu.Color(0.8, 0.8, 0.8))
    tex_checker_bw = rtt.ImageTexture("textures/conc.jpg")
    tex_grass = rtt.ImageTexture("textures/grass.png")


    mat_tex_checker_bw = rtm.TextureColor(tex_checker_bw)
    mat_tex_grass = rtm.TextureColor(tex_grass)

    mat_green = rtm.Lambertian(rtu.Color(0, 1, 0))  # +Y
    mat_blue  = rtm.Lambertian(rtu.Color(0, 0, 1))  # +Z

    light = rtl.Diffuse_light(rtu.Color(0.2, 0.2, 0.2))

    bulb_mat = rtl.Diffuse_light(
        rtu.Color(1.0, 0.90, 0.70),
        intensity=5.0,
        linear=0.12,
        quadratic=0.35,
    )

    spot_mat = rtl.SpotLight(
        rtu.Color(1.0, 0.95, 0.78),
        direction=rtu.Vec3(0.0, -1.0, 0.0),
        inner_deg = 22.0,
        outer_deg = 42.0,
        intensity=0.9,
        linear=0.001,
        quadratic=0.002
    )

    sph_left = rto.Sphere(rtu.Vec3(-1.0,0.0,-1),  0.5, mat_tex_checker_bw)
    building = rttr.MeshTranformer.obj_mtl_to_mesh("model/building/tinker.obj",rtm.Lambertian(rtu.Color(1,1,1)),rtu.Vec3(0,-0.6,1.5))
    building.set_transform(1.2,rtu.Vec3(0,90,0))
    building2 = rttr.MeshTranformer.obj_mtl_to_mesh("model/mhoo/tinker.obj",rtm.Lambertian(rtu.Color(1,1,1)),rtu.Vec3(0,-0.6,-0.5))
    building2.set_transform(0.8,rtu.Vec3(0,180,0))
    car4 = rttr.MeshTranformer.obj_mtl_to_mesh("model/car/tinker.obj",rtm.Lambertian(rtu.Color(1,1,1)),rtu.Vec3(2.1,-0.5,0.5))
    car4.set_transform(0.4,rtu.Vec3(0,-90,0))
    street_light2 = rttr.MeshTranformer.obj_mtl_to_mesh("model/street_with_light/tinker.obj",rtm.Phong(rtu.Color(1,1,1), 0.8, 0.2, 8),rtu.Vec3(2.0,-0.5,1.2))
    street_light2.set_transform(1,rtu.Vec3(0,180,0))
    street_light3 = rttr.MeshTranformer.obj_mtl_to_mesh("model/street_with_light/tinker.obj",rtm.Phong(rtu.Color(1,1,1), 0.8, 0.2, 8),rtu.Vec3(2.0,-0.5,-0.54))
    street_light3.set_transform(1,rtu.Vec3(0,180,0))
    street_light4 = rttr.MeshTranformer.obj_mtl_to_mesh("model/street_with_light/tinker.obj",rtm.Phong(rtu.Color(1,1,1), 0.8, 0.2, 8),rtu.Vec3(2.0,-0.5,-2.6))
    street_light4.set_transform(1,rtu.Vec3(0,180,0))
   
    world = rts.Scene()
    world.add_object(
        rto.Quad(
            rtu.Vec3(-2, -0.5, -1.5),  # origin (shifted so center stays same)
            rtu.Vec3(4, 0, 0),           # width
            rtu.Vec3(0, 0, 3.8),           # depth
            mat_tex_checker_bw
        )
    )
    world.add_object(building)
    world.add_object(building2)
    world.add_object(car4)
    world.add_object(street_light2)
    world.add_object(street_light3)
    lamp_pos2 = rtu.Vec3(2.5,1.3,0.45)
    
    world.add_object(rto.Sphere(lamp_pos2 + rtu.Vec3(0.142, -0.3, 0.0), 0.025, spot_mat)) ################ try new feature
    
    intg = rti.Integrator(bSkyBG=False,roulette=True)
    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render(type=rtu.RenderType.JITTERED)
    renderer.write_img2png('test.png')    


if __name__ == "__main__":
    renderCity()
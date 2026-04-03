import RT_utility as rtu

class AABB:
    def __init__(self, min_v, max_v):
        self.min = min_v
        self.max = max_v

    def hit(self, ray, interval):
            t_min = float(interval.min_val)
            t_max = float(interval.max_val)

            for axis in range(3):
                direction = float(ray.getDirection()[axis])
                origin = float(ray.getOrigin()[axis])
                
                if abs(direction) < 1e-8:
                    if origin < float(self.min[axis]) or origin > float(self.max[axis]):
                        return False
                    continue
                invD = 1.0 / direction
                t0 = (float(self.min[axis]) - origin) * invD
                t1 = (float(self.max[axis]) - origin) * invD

                if invD < 0.0:
                    t0, t1 = t1, t0
                if t0 > t_min: t_min = t0
                if t1 < t_max: t_max = t1

                if t_max <= t_min:
                    return False

            interval.min_val = t_min
            interval.max_val = t_max
            return True
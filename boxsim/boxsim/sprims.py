"""
Computing sensory primitives from raw data.
"""

import toolbox
import robots

def enforce_bounds(data, bounds):
    return tuple(min(bi_max, max(bi_min, d_i)) for di, (bi_min, bi_max) in zip(data, bounds))

def isobarycenter(bounds):
    return tuple((b+a)/2.0 for a, b in bounds)

sprims = {}

def create_sprim(cfg):
    sensory_class = sprims[cfg.sprimitive.name]
    sensory_prim = sensory_class(cfg)
    if cfg.sprimitive.uniformize:
        sensory_prim = Uniformize(sensory_prim)
    return sensory_prim

class SensoryPrimitive(object):

    def __init__(self, cfg):
        pass

    def process_context(self, context):
        """Define s_feats and s_bounds here"""
        raise NotImplementedError

    def process_sensors(self, context):
        """Process sensory data and return effect"""
        raise NotImplementedError


class Uniformize(SensoryPrimitive):

    def __init__(self, sensory_prim):
        self.sensory_prim = sensory_prim

    def process_context(self, context):
        self.sensory_prim.process_context(context)
        self.s_feats = self.sensory_prim.s_feats
        self.s_bounds = tuple((0.0, 1.0) for _ in self.sensory_prim.s_bounds)

    def _sim2uni(self, effect):
        return tuple((e_i - s_min)/(s_max - s_min) for e_i, (s_min, s_max) in zip(effect, self.sensory_prim.s_bounds))

    def process_sensors(self, sensors_data):
        effect = self.sensory_prim.process_sensors(sensors_data)
        return self._sim2uni(effect)


class EndPos(SensoryPrimitive):

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name

    def process_context(self, context):
        self.s_feats = (0, 1, 2,)
        self.s_bounds = tuple(context['geobounds']) + ((0.0, 1.0),)

    def process_sensors(self, sensors_data):
        pos_array = sensors_data[self.object_name + '_pos']
        pos_a = pos_array[0]
        pos_b = pos_array[-1]
        collision = 0.0 if pos_a == pos_b else 1.0

        return tuple(pos_b) + (collision,)

sprims['endpos'] = EndPos


class MaxVel(SensoryPrimitive):

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name

    def process_context(self, context):
        self.s_feats = (0, 1)
        self.s_bounds = ((0.0, 800.0),) + ((0.0, 1.0),)

    def process_sensors(self, sensors_data):
        vel_array = sensors_data[self.object_name + '_vel']
        max_vel = max(toolbox.norm(v_i) for v_i in vel_array)
        collision = 0.0 if max_vel == 0.0 else 1.0

        return (max_vel, collision,)

sprims['maxvel'] = MaxVel


class Collisions(SensoryPrimitive):

    def __init__(self, cfg):
        self.setA = cfg.sprimitive.setA
        self.setB = cfg.sprimitive.setB

    def process_context(self, context):
        self.s_feats = (0, 1, 2, 3, 4)
        self.s_bounds =  tuple(context['geobounds']) + ((-800.0, 800.0), (-800.0, 800.0)) + ((0.0, 1.0),)

    def process_sensors(self, sensors_data):
        collisions = sensors_data['_collisions']
        for collision in collisions:
            nameA = collision[0]
            nameB = collision[1]
            if nameA in  self.setA:
                if nameB in self.setB:
                    return tuple(collision[2]) + tuple(collision[3]) + (1.0,)
            if nameB in self.setA:
                if nameA in self.setB:
                    return tuple(collision[2]) + (-collision[3][0], -collision[3][1]) + (1.0,)

        return isobarycenter(self.s_bounds)[:4] + (0.0,)

sprims['collisions'] = Collisions


def filter_collisions(collisions, setA, setB):
    """ Filter collision that involve object from set A and B,
        and put them in the same order (object from set A first)
    """
    filtered = []
    for collision in collisions:
        nameA = collision[0]
        nameB = collision[1]
        if nameA in setA and nameB in setB:
            filtered.append(collision)
        elif nameB in setA and nameA in setB:
            filtered.append((collision[1], collision[0], collision[2], (-collision[3][0], -collision[3][1])))

    return filtered

class Hear(SensoryPrimitive):
    """If ball1 collides with wallW and wallN and wallE, then produces a sound"""

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name
        self.s_feats = (0, 1, 2)
        self.s_bounds = 3*((0.0, 1.0),)

    def process_context(self, context):
        self.geobounds = context['geobounds']

    def process_sensors(self, sensors_data):
        collisions = sensors_data['_collisions']
        collisions = filter_collisions(collisions, ['wallW', 'wallS', 'wallE'], [self.object_name])
        print collisions
        if len(collisions) < 3:
            return (0.5, 0.5, 0.0)
        else:
            return (self._transform(c) for c in collision[:3])

    def _transform(self, collision):
        """Transform a collision with a wall into a number between 0 and 1"""
        if collision[0] == 'wallW' or collision[0] == 'wallE':
            y = collision[2][1]
            min_y, max_y = self.geobounds[1]
            return 1.0*(y - min_y)/(max_y - min_y)
        else:
            assert collision[0] == 'wallS'
            x = collision[2][0]
            min_x, max_x = self.geobounds[0]
            return 1.0*(x - min_x)/(max_x - min_x)

sprims['hear'] = Hear

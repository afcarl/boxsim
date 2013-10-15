"""
Computing sensory primitives from raw data.
"""

def enforce_bounds(data, bounds):
    return tuple(min(bi_max, max(bi_min, d_i)) for di, (bi_min, bi_max) in zip(data, bounds))


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
        self.s_bounds = tuple((0.0, 1.0) for i in range(self.sensory_prim.s_bounds))

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
        collision = 1.0 if pos_a == pos_b else 0.0

        return tuple(pos_b) + (collision,)

sprims['endpos'] = EndPos

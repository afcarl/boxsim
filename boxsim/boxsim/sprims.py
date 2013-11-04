"""
Computing sensory primitives from raw data.
"""
from __future__ import division

import math

import toolbox
import robots

from .color import Color

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

    def required_channels(self):
        """Defines used channels for this sensory primitive"""
        raise NotImplementedError

    def process_context(self, context):
        """Define s_feats, s_bounds and s_fixed here"""
        raise NotImplementedError

    def process_sensors(self, context):
        """Process sensory data and return effect"""
        raise NotImplementedError


class Uniformize(SensoryPrimitive):

    def __init__(self, sensory_prim):
        self.sensory_prim = sensory_prim

    def required_channels(self):
        return self.sensory_prim.required_channels()

    def process_context(self, context):
        self.sensory_prim.process_context(context)
        self.s_feats  = self.sensory_prim.s_feats
        self.s_bounds = tuple((0.0, 1.0) for _ in self.sensory_prim.s_bounds)
        self.s_fixed  = self.sensory_prim.s_fixed

    def _sim2uni(self, effect):
        return tuple((e_i - s_min)/(s_max - s_min) for e_i, (s_min, s_max) in zip(effect, self.sensory_prim.s_bounds))

    def process_sensors(self, sensors_data):
        effect = self.sensory_prim.process_sensors(sensors_data)
        return self._sim2uni(effect)


class EndPos(SensoryPrimitive):

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name
        self.res = cfg.sprimitive.res

    def required_channels(self):
        return (self.object_name + '_pos',)


    def process_context(self, context):
        self.s_feats = (0, 1, 2,)
        self.s_bounds = tuple(context['geobounds']) + ((0.0, 1.0),)
        self.s_fixed = (None, None, 1.0)

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
        self.s_fixed = (None, 1.0)

    def required_channels(self):
        return (self.object_name + '_vel',)

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

    def required_channels(self):
        return ('_collisions',)

    def process_context(self, context):
        self.s_feats = (0, 1, 2, 3, 4)
        self.s_bounds = tuple(context['geobounds']) + ((-800.0, 800.0), (-800.0, 800.0)) + ((0.0, 1.0),)
        self.s_fixed = (None, None, None, None, 1.0)

    def process_sensors(self, sensors_data):
        collisions = sensors_data['_collisions']
        for collision in collisions:
            nameA = collision[0]
            nameB = collision[1]
            if nameA in self.setA:
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
        self.vocalizer = robots.VowelModel()
        self.s_feats = (0, 1, 2)
        self.s_bounds = self.vocalizer.s_bounds + ((0.0, 1.0),)
        self.s_fixed = (None, None, 1.0)

    def required_channels(self):
        return ('_collisions',)

    def process_context(self, context):
        self.geobounds = context['geobounds']

    def process_sensors(self, sensors_data):
        collisions = sensors_data['_collisions']
        collisions = filter_collisions(collisions, ['wallW', 'wallS', 'wallE'], [self.object_name])
        if len(collisions) < 3:
            mouth = (0.5, 0.5, 0.5)
            suffix = (0.0,)
        else:
            mouth = tuple(self._transform(c) for c in collisions[:3])
            suffix = (1.0,)
        assert all(0 <= m_i <= 1 for m_i in mouth), "{} is not within bounds".format(collisions[:3])
        perceive = self.vocalizer.execute_order(mouth) + suffix
        return perceive

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

def vector2angle(v):
    return math.atan2(v[1], v[0])

class Haptic(SensoryPrimitive):
    """Return the angle and intensity of the strongest interaction with the arm tip and an object"""

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name
        self.s_feats = (0, 1, 2)
        self.s_fixed = (None, None, 1.0)

    def required_channels(self):
        return ('_collisions',)

    def process_context(self, context):
        self.geobounds = context['geobounds']
        x_range = self.geobounds[0][1] - self.geobounds[0][0]
        y_range = self.geobounds[1][1] - self.geobounds[1][0]
        self.s_bounds = ((-math.pi, math.pi), (0.0, 3*toolbox.norm((x_range, y_range))), (0.0, 1.0))

    def process_sensors(self, sensors_data):
        collisions = sensors_data['_collisions']
        collisions = filter_collisions(collisions, ['arm.tip'], [self.object_name])
        if len(collisions) == 0:
            return (0.0, 0.0, 0.0)
        else:
            interaction = collisions[0][3]
            for c in collisions:
                if toolbox.norm(c[3]) > toolbox.norm(interaction):
                    interaction = c[3]
            angle = vector2angle(interaction)
            norm = toolbox.norm(interaction)
            print norm

            return (angle, norm, 1.0)

sprims['haptic'] = Haptic

color_upleft = Color(255, 0, 0)
color_upright = Color(255, 255, 0)
color_lowleft = Color(0, 0, 255)
color_lowright = Color(0, 255, 255)
int_to_float_const = 1.0 / 255.0

class Visual(SensoryPrimitive):
    """The balls light up the tile it enters. Return the average light and color"""

    def __init__(self, cfg):
        self.object_name = cfg.sprimitive.object_name
        self.s_feats = (0, 1, 2, 3)
        self.s_bounds = ((0.0, 1.0),)*4
        self.s_fixed = (None, None, None, 1.0)

    def required_channels(self):
        return (self.object_name + '_pos',)

    def process_context(self, context):
        self.geobounds = context['geobounds']

    def process_sensors(self, sensors_data):
        
        x_min, x_max = self.geobounds[0]
        y_min, y_max = self.geobounds[1]
        
        pos_list = sensors_data[self.object_name + '_pos']
        gamma = 0.99
        sum_gamma = 0.0
        red, green, blue = 0.0, 0.0, 0.0
        for pos in reversed(pos_list):
            c = self.bilinear_interpolate_color(color_upleft, color_upright, color_lowleft, color_lowright,
                (pos[0] - x_min) / (x_max - x_min), (pos[1] - y_min) / (y_max - y_min))
            red += c.red * gamma
            blue += c.blue * gamma
            green += c.green * gamma
            sum_gamma += gamma
            gamma *= gamma
        return (red / 255 / sum_gamma, green / 255 / sum_gamma, blue / 255 / sum_gamma, 0.0)
        
    def interpolate_color(self, color_1, color_2, fraction):
        fraction = max(min(fraction, 1.0), 0.0)
        
        delta_red = (color_2.red * int_to_float_const) - (color_1.red * int_to_float_const)
        delta_green = (color_2.green * int_to_float_const) - (color_1.green * int_to_float_const)
        delta_blue = (color_2.blue * int_to_float_const) - (color_1.blue * int_to_float_const)
        
        red = (color_1.red * int_to_float_const) + (delta_red * fraction)
        green = (color_1.green * int_to_float_const) + (delta_green * fraction)
        blue = (color_1.blue * int_to_float_const) + (delta_blue * fraction)
        
        red = max(min(red, 1.0), 0.0)
        green = max(min(green, 1.0), 0.0)
        blue = max(min(blue, 1.0), 0.0)
        
        return Color(red * 255, green * 255, blue * 255)
        
    def bilinear_interpolate_color(self, color_00, color_10, color_01, color_11, x, y):
        return self.interpolate_color(self.interpolate_color(color_00, color_10, x), self.interpolate_color(color_01, color_11, x), y)

sprims['visual'] = Visual

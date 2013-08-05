 # Test if the Python client is compatible with the Java server
from __future__ import division
import numbers, sys
import math

import treedict

from toolbox import gfx

import boxcom

prefixcolor = gfx.purple

defaultcfg = treedict.TreeDict()

defaultcfg.arm_lengths = None
defaultcfg.arm_lengths_desc = 'list of link lenghts of the arm'

defaultcfg.angle_limit = None
defaultcfg.angle_limit_desc = 'the angle limit of the joint in radians. Will be applied symetrically.'

defaultcfg.max_speed = None
defaultcfg.max_speed_desc = 'the maximum rotational speed of the motor, in rad/s.'

defaultcfg.base_pos = None
defaultcfg.base_pos_desc = 'position of the base of the arm'

defaultcfg.toy_order = []
defaultcfg.toy_order = 'the order of toy, for the sensor feedback; list of the name of the nodes of cfg.toys'

defaultcfg.toys_desc = 'node for toys to be defined'

# defaultcfg.toy_pos = None
# defaultcfg.toy_pos_desc = 'position of the toy'
#
# defaultcfg.toy_size = None
# defaultcfg.toy_size_desc = 'size of the toy'
#
# defaultcfg.toy_type = None
# defaultcfg.toy_type_desc = 'type of toy amongst ball or cube'
#
# defaultcfg.toy_friction    = None
# defaultcfg.toy_restitution = None
# defaultcfg.toy_density     = None

defaultcfg.sensors = 'toy'
defaultcfg.sensors_desc = 'return of the sensor, either position of the arm <arm> or toy <toy>'

defaultcfg.visu = False
defaultcfg.visu_desc = 'if True, visualization is activated, and simulation happen at a real-time pace'

defaultcfg.verbose = True
defaultcfg.verbose_desc = ''

defaultcfg.steps = None
defaultcfg.steps_desc = 'duration (in s) of each trial'

class FilterSim(object):

    def __init__(self, sim, s_feats = None, s_bounds_factor = None):
        self.sim = sim
        self.cfg = sim.cfg

        self.m_feats  = sim.m_feats
        self.s_feats  = tuple(s_feats) if s_feats is not None else sim.s_feats
        self._s_feats_validity = [s_i in self.s_feats for s_i in self.sim.s_feats]
        self.m_bounds = sim.m_bounds

        self.s_bounds_factor = s_bounds_factor
        self.s_bounds = self._compute_s_bounds()

    def _compute_s_bounds(self):

        filtered_s_bounds = tuple(b for b, v in zip(self.sim.s_bounds, self._s_feats_validity) if v)
        if self.s_bounds_factor is None:
            return filtered_s_bounds
        else:
            assert len(self.s_feats) == len(self.s_bounds_factor)
            s_bounds = []
            for (s_min, s_max), (f_min, f_max) in zip(filtered_s_bounds, self.s_bounds_factor):
                sf_min = s_max - f_min*(s_max-s_min)
                sf_max = s_min + f_max*(s_max-s_min)
                assert sf_min <= sf_max
                s_bounds.append((sf_min, sf_max))
            return tuple(s_bounds)

    def execute_order(self, order, verbose = False):
        effect = self.sim.execute_order(order, verbose = False)
        effect = self._filtered_effect(effect)
        if verbose or self.cfg.verbose:
            print("{}sim{}: ({}) -> ({}){}".format(prefixcolor, gfx.end,
                                                 ", ".join("{}{:+3.2f}{}".format(gfx.cyan, o_i, gfx.end) for o_i in uni_order),
                                                 ", ".join("{}{:+3.2f}{}".format(gfx.green, e_i, gfx.end) for e_i in uni_effect), '\033[K'))
        return effect

    def _filtered_effect(self, effect):
        return tuple(e_i for e_i, v_i in zip(effect, self._s_feats_validity) if v_i)

    def close(self):
        return self.sim.close()




class UniformizeSim(object):
    """Uniformize the bounds of the order and effect feature between 0.0 and 1.0"""

    def __init__(self, sim):
        self.sim = sim
        self.cfg = sim.cfg

        self.m_feats = sim.m_feats
        self.s_feats = sim.s_feats

        self.m_bounds = len(sim.m_bounds)*((0.0, 1.0),)
        self.s_bounds = len(sim.s_bounds)*((0.0, 1.0),)

    def _uni2sim(self, order):
        return tuple(e_i*(b_max - b_min) + b_min for e_i, (b_min, b_max) in zip(order, self.sim.m_bounds))

    def _sim2uni(self, effect):
        return tuple((e_i - s_min)/(s_max - s_min) for e_i, (s_min, s_max) in zip(effect, self.sim.s_bounds))

    def execute_order(self, uni_order, verbose = False):
        order = self._uni2sim(uni_order)
        effect = self.sim.execute_order(order, verbose = False)
        uni_effect = self._sim2uni(effect)
        if verbose or self.cfg.verbose:
            print("{}sim{}: ({}) -> ({}){}".format(prefixcolor, gfx.end,
                                                 ", ".join("{}{:+3.2f}{}".format(gfx.cyan, o_i, gfx.end) for o_i in uni_order),
                                                 ", ".join("{}{:+3.2f}{}".format(gfx.green, e_i, gfx.end) for e_i in uni_effect), '\033[K'))

        return uni_effect

    def close(self):
        return self.sim.close()


class BoxSimBase(object):

    def __init__(self, cfg, port = 0):

        self.cfg = cfg
        self.cfg.update(defaultcfg, overwrite = False)
        self._check_cfg(cfg)

        self.armsize  = len(self.cfg.arm_lengths)

    @staticmethod
    def _check_cfg(cfg):
        """Check and format config"""
        assert all(isinstance(e, numbers.Number) for e in cfg.arm_lengths)
        assert all(isinstance(e, numbers.Number) for e in cfg.base_pos)
        assert isinstance(cfg.steps, numbers.Number)
        assert isinstance(cfg.angle_limit, numbers.Number) and cfg.angle_limit >= 0.0
        assert isinstance(cfg.max_speed, numbers.Number) and cfg.max_speed >= 0.0

        assert cfg.toy_order is not None

        for toyname in cfg.toy_order:
            toy = cfg.toys[toyname]
            assert isinstance(toy.type, str)
            assert all(isinstance(e, numbers.Number) for e in toy.pos)
            assert isinstance(toy.friction, numbers.Number)
            assert isinstance(toy.restitution, numbers.Number)
            assert isinstance(toy.density, numbers.Number)

        assert isinstance(cfg.sensors, str)

        assert isinstance(cfg.verbose, bool)
        assert isinstance(cfg.visu, bool)

    def _execute_raw(self, order):
        assert len(order) == 3*self.armsize
        order = [float(oi) for oi in order]

        init_pose   = order[:self.armsize]
        target_pose = order[self.armsize:2*self.armsize]
        max_vel     = order[2*self.armsize:3*self.armsize]

        flat_order = []
        for t_i, v_i in zip(target_pose, max_vel):
            assert v_i >= -0.00001
            v_i = max(0.0, v_i)
            flat_order += [t_i, v_i]

        return self._boxcom.send_order(init_pose, flat_order, self.cfg.steps, self.conf)

    def _make_conf(self):
        self.conf = ( [self.armsize]
                    + list(self.cfg.arm_lengths)
                    + [self.cfg.angle_limit,
                       int(self.cfg.base_pos[0]), int(self.cfg.base_pos[1]),
                       len(self.cfg.toy_order),
                      ])

        for toyname in self.cfg.toy_order:
            toy = self.cfg.toys[toyname]
            toy_type_int = {'ball': 0, 'cube': 1}[toy.type]

            self.conf += [toy_type_int,
                          int(toy.pos[0]),  int(toy.pos[1]),
                          float(toy.width),
                          float(toy.friction),
                          float(toy.restitution),
                          float(toy.density)]
        return self.conf

    def _send_conf(self, conf_vector):
        self._boxcom = boxcom.BoxCom(self, self.cfg)
        self._geo_bounds = self._boxcom.send_conf(conf_vector)

    def close(self):
        self._boxcom.close()


    ## Sensory features extraction functions ##

def _extract_sfeat(result, s_feats, absolute = True):
    s_value = tuple(result[1][s_i] for s_i in s_feats)
    if not absolute:
        s_value = tuple(s_vi - result[0][s_i] for s_vi, s_i in zip(s_value, s_feats))
    return s_value

def _arm_pos(self, result, absolute = True):
    toy_n = len(self.cfg.toy_order)
    return _extract_sfeat(result, (-3 - 2*toy_n, -2 - 2*toy_n), absolute = absolute)

def _toy_pos(self, result, absolute = True):
    toy_n = len(self.cfg.toy_order)
    toy_pos = tuple()
    for i in range(toy_n, 0, -1):
        toy_pos += _extract_sfeat(result, (-2*i, -2*i+1), absolute = absolute)
        toy_displacement = _extract_sfeat(result, (-2*i, -2*i+1), absolute = False)
        if toy_displacement == (0., 0.):
            toy_pos += ((0.0),)
        else:
            toy_pos += ((1.0),)
    return toy_pos

def _armtoys_pos(self, result, absolute = True):
    return _arm_pos(self, result, absolute = absolute) + _toy_pos(self, result, absolute = absolute)

def _joint_pos(self, result, absolute = True):
    s_feats = []
    for i in range(self.armsize):
        s_feats.append(3*i)
        s_feats.append(3*i+1)
    return _extract_sfeat(result, s_feats, absolute = absolute)

def _joint_angle(self, result, absolute = True):
    s_feats = [3*i+2 for i in range(self.armsize)]
    return _extract_sfeat(result, s_feats, absolute = absolute)

def _fullarm_sensors(self, result, absolute = True):
    return _joint_pos(self, result, absolute = absolute) + _joint_angle(self, result, absolute = absolute)


    ## Motor order conversion functions ##

def _goto(self, order):
    assert len(order) == self.armsize
    init_pos = tuple(0.0 for _ in order)
    vels     = tuple(self.cfg.max_speed for _ in order)
    return init_pos + tuple(order) + vels

def _common_velocity(self, order):
    assert len(order) == 2*self.armsize + 1
    return tuple(order) + (self.armsize - 1)*(order[-1],)

def _full_motor(self, order):
    assert len(order) == 3*self.armsize
    return order

    ## Class ##

class BoxSim(BoxSimBase):

    def __init__(self, cfg, port = 0):

        BoxSimBase.__init__(self, cfg, port = port)

        conf_vector = self._make_conf()
        self._send_conf(conf_vector)

        toy_n = len(self.cfg.toy_order)
        sensors_dict = {'arm'     : ((0, 1),                        self._geo_bounds,                                         _arm_pos),
                        'toy'     : (tuple(range(3*toy_n)),        (self._geo_bounds + ((0., 1.),))*toy_n,                    _toy_pos),
                        'joints'  : (tuple(range(2*self.armsize)),  self.armsize*self._geo_bounds,                            _joint_pos),
                        'angles'  : (tuple(range(  self.armsize)),  self.armsize*((-math.pi, math.pi),),                      _joint_angle),
                        'fullarm' : (tuple(range(3*self.armsize)),  self.armsize*(self._geo_bounds + ((-math.pi, math.pi),)), _fullarm_sensors),
                       }
        sensors_dict['armtoys'] = (sensors_dict['arm'][0]+sensors_dict['toy'][0],
                                   sensors_dict['arm'][1]+sensors_dict['toy'][1],
                                   _armtoys_pos
                                  )

        jb = ((-self.cfg.angle_limit, self.cfg.angle_limit),)
        motors_dict = {'goto'           : (tuple(range(-self.armsize, 0)),       self.armsize*jb,                                            _goto),
                       'commonvelocity' : (tuple(range(-2*self.armsize-1, 0)), 2*self.armsize*jb +              ((0., self.cfg.max_speed),), _common_velocity),
                       'fullmotor'      : (tuple(range(-3*self.armsize, 0)),   2*self.armsize*jb + self.armsize*((0., self.cfg.max_speed),), _full_motor),
                      }

        self.s_feats, self.s_bounds, self.s_f = sensors_dict[cfg.sensors]
        self.m_feats, self.m_bounds, self.m_f =  motors_dict[cfg.motors]

    def execute_order(self, order, verbose = True):

        order = [float(oi) for oi in order]
        long_order = self.m_f(self, order)
        if self.cfg.verbose:
            print('{}sim{}: ({}) -> ...\r'.format(prefixcolor, gfx.end,
                                                  ', '.join('{}{:+3.2f}{}'.format(gfx.cyan, o_i, gfx.end) for o_i in long_order))),
            sys.stdout.flush()

        result = self._execute_raw(long_order)
        effect = self.s_f(self, result)
        assert len(effect) == len(self.s_feats)

        if self.cfg.verbose and verbose:
            print('{}sim{}: ({}) -> ({}){}'.format(prefixcolor, gfx.end,
                                                   ', '.join('{}{:+3.2f}{}'.format(gfx.cyan, o_i, gfx.end) for o_i in long_order),
                                                   ', '.join('{}{:+3.0f}{}'.format(gfx.green, e_i, gfx.end) for e_i in effect), '\033[K'))
        return effect


import treedict
import random

from . import boxcom
from . import sprims
from . import mprims

defaultcfg = treedict.TreeDict()

defaultcfg.arm.lenghts = None
defaultcfg.arm.lengths_desc = 'list of link lenghts of the arm'

defaultcfg.arm.limits = None
defaultcfg.arm.limits_desc = 'the angle limit of the joint in radians. Will be applied symetrically.'

defaultcfg.arm.self_collisions = None
defaultcfg.arm.self_collisions = 'if True the arm links and tip collide with each other.'

defaultcfg.arm.max_speed = None
defaultcfg.arm.max_speed_desc = 'the maximum rotational speed of the motor, in rad/s.'

defaultcfg.arm.base_pos = None
defaultcfg.arm.base_pos_desc = 'position of the base of the arm'

defaultcfg.toy_order = []
defaultcfg.toy_order = 'the order of toy, for the sensor feedback; list of the name of the nodes of cfg.toys'

defaultcfg.toys = []
defaultcfg.toys_desc = 'node for toys to be defined'

defaultcfg.steps = None
defaultcfg.steps_desc = 'duration (in s) of each trial'

defaultcfg.sim = treedict.TreeDict()
defaultcfg.steps_desc = 'configuration for sim side-effects'


class Simulation(object):
    """"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.sensory_prim = sprims.create_sprim(self.cfg)
        self.motor_prim = mprims.create_mprim(self.cfg)

        self.conf_vector = self._make_conf()
        self._boxabs = boxcom.BoxAbstraction(self.conf_vector, cfg.com)

        self.sensory_prim.process_context(self._boxabs.context)
        self.motor_prim.process_context(self._boxabs.context)


    @property
    def s_feats(self):
        return self.sensory_prim.s_feats

    @property
    def s_bounds(self):
        return self.sensory_prim.s_bounds

    @property
    def s_fixed(self):
        return self.sensory_prim.s_fixed

    @property
    def m_feats(self):
        return self.motor_prim.m_feats

    @property
    def m_bounds(self):
        return self.motor_prim.m_bounds

    @property
    def real_s_bounds(self):
        return self.sensory_prim.real_s_bounds

    @property
    def s_units(self):
        return self.sensory_prim.units()

    def apply_noise(self, order, noise_level):
        return tuple(min(mi_max, max(mi_min, mi + random.gauss(0.0, noise_level)))  for (mi_min, mi_max), mi in zip(self.m_bounds, order))


    def execute_order(self, order):
        noisy_order = self.apply_noise(order, self.cfg.arm.noise)
        motor_cmd   = self.motor_prim.process_order(noisy_order)
        featdict = self._boxabs.execute_order(motor_cmd, self.cfg.steps)
        try:
            effect = self.sensory_prim.process_sensors(featdict)
        except Exception as e:
            print(order)
            raise e
        if not all(b_min <= e_i <= b_max for e_i, (b_min, b_max) in zip(effect, self.s_bounds)):
            if self.sensory_prim.sensory_prim.object_name == 'arm.tip': # HACKY HACK !
                return effect
            else:
                assert(all(b_min <= e_i <= b_max for e_i, (b_min, b_max) in zip(effect, self.s_bounds))), "{} not inside {}".format(effect, self.s_bounds)
        return effect

    def _make_conf(self):
        self.conf = []
        self.conf.append(self.cfg.arm.lengths)
        self.conf.append(self.cfg.arm.limits)
        self.conf.append(self.cfg.arm.base_pos)
        self.conf.append(self.cfg.arm.self_collisions)

        toys = []
        for toyname, toy in self.cfg.toys.iteritems(recursive=False, branch_mode='only'):

            toys.append([toyname,
                         toy.type,
                         toy.pos,
                         toy.width,
                         toy.friction,
                         toy.restitution,
                         toy.density,
                         toy.linear_damping,
                         toy.angular_damping])
        self.conf.append(toys)

        self.conf.append(self.sensory_prim.required_channels())

        return self.conf

    def close(self):
        return self._boxabs.close()

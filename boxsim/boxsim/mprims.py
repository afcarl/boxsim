"""
Computing motor primitives from high-level orders.
"""

def enforce_bounds(data, bounds):
    return tuple(min(bi_max, max(bi_min, d_i)) for di, (bi_min, bi_max) in zip(data, bounds))


mprims = {}

def create_mprim(cfg):
    motor_class = mprims[cfg.mprimitive.name]
    motor_prim = motor_class(cfg)
    if cfg.mprimitive.uniformize:
        motor_prim = Uniformize(motor_prim)
    return motor_prim


class MotorPrimitive(object):

    def __init__(self, cfg):
        pass

    def process_context(self, context):
        """Define m_feats and m_bounds here"""
        raise NotImplementedError

    def process_order(self, context):
        """Process order and translate it to simulation-ready motor command"""
        raise NotImplementedError


class Uniformize(MotorPrimitive):

    def __init__(self, motor_prim):
        self.motor_prim = motor_prim

    def process_context(self, context):
        self.motor_prim.process_context(context)
        self.m_feats = self.motor_prim.m_feats
        self.m_bounds = tuple((0.0, 1.0) for i in self.motor_prim.m_bounds)

    def _uni2sim(self, order):
        return tuple(e_i*(b_max - b_min) + b_min for e_i, (b_min, b_max) in zip(order, self.motor_prim.m_bounds))

    def process_order(self, order):
        sim_order = self._uni2sim(order)
        return self.motor_prim.process_order(sim_order)


class CommonVel(MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg
        self.size = len(self.cfg.arm.lengths)
        self.m_feats = tuple(range(-1, -2*self.size-2, -1))
        self.m_bounds = 2*self.size*(tuple(self.cfg.arm.limits),) + ((0.0, 1.0),)

    def process_context(self, context):
        pass

    def process_order(self, order):
        assert len(order) == 2*self.size+1
        start_pos = order[0:self.size]
        end_pos   = order[self.size:2*self.size]
        max_vel = order[-1]

        return (start_pos, end_pos, self.size*(max_vel,))

mprims['commonvel'] = CommonVel

import treedict

cfg = treedict.TreeDict()

cfg.arm.lengths   = (50.0,)*6
cfg.arm.limits    = (-2.0, 2.0)
cfg.arm.max_speed = 2.0
cfg.arm.base_pos  = (400, 80)

cfg.steps         = 12*60

cfg.com.visu        = False
cfg.com.verbose     = False
cfg.com.debug       = False
cfg.com.java_output = False

cfg.sprimitive.name        = 'endpos'
cfg.sprimitive.object_name = 'ball1'
cfg.sprimitive.uniformize  = True

cfg.mprimitive.name        = 'commonvel'
cfg.mprimitive.uniformize  = True

cfg.toys.ball.pos         = (550, 350)
cfg.toys.ball.width       = 40
cfg.toys.ball.type        = 'ball1'
cfg.toys.ball.friction    = 1.0
cfg.toys.ball.restitution = 0.7
cfg.toys.ball.density     = 1.0

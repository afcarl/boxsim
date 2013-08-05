import treedict

cfg = treedict.TreeDict()
cfg.steps       = 12*60
cfg.armsize     = 6
cfg.arm_lengths = (50.0,)*6
cfg.angle_limit = 2.0
cfg.max_speed   = 2.0
cfg.base_pos    = (400, 80)

cfg.visu        = False
cfg.verbose     = True
cfg.debug       = False
cfg.java_output = False

cfg.sensors = 'toy'
cfg.motors  = 'commonvelocity'

cfg.toys.ball.pos         = (550, 350)
cfg.toys.ball.width       = 40
cfg.toys.ball.type        = 'ball'
cfg.toys.ball.friction    = 1.0
cfg.toys.ball.restitution = 0.7
cfg.toys.ball.density     = 1.0

cfg.toy_order = ['ball']

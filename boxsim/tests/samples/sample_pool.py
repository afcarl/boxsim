import treedict
import boxsim

cfg = treedict.TreeDict()
cfg.steps       = 12*60
cfg.armsize     = 6
cfg.arm_lengths = (50.0,)*6
cfg.angle_limit = 2.0
cfg.max_speed   = 2.0
cfg.base_pos    = (400, 80)

cfg.visu        = True
cfg.verbose     = True
cfg.debug       = False
cfg.java_output = False

cfg.sensors = 'toy'
cfg.motors  = 'commonvelocity'

cfg.toys.ball1.pos         = (550, 350)
cfg.toys.ball1.width       = 40
cfg.toys.ball1.type        = 'ball'
cfg.toys.ball1.friction    = 1.0
cfg.toys.ball1.restitution = 0.7
cfg.toys.ball1.density     = 1.0

cfg.toys.ball2.pos         = (130, 670)
cfg.toys.ball2.width       = 40
cfg.toys.ball2.type        = 'ball'
cfg.toys.ball2.friction    = 1.0
cfg.toys.ball2.restitution = 0.7
cfg.toys.ball2.density     = 1.0

cfg.toys.ball3.pos         = (670, 670)
cfg.toys.ball3.width       = 40
cfg.toys.ball3.type        = 'ball'
cfg.toys.ball3.friction    = 1.0
cfg.toys.ball3.restitution = 0.7
cfg.toys.ball3.density     = 1.0

cfg.toys.ball4.pos         = (670, 130)
cfg.toys.ball4.width       = 40
cfg.toys.ball4.type        = 'ball'
cfg.toys.ball4.friction    = 1.0
cfg.toys.ball4.restitution = 0.7
cfg.toys.ball4.density     = 1.0


cfg.toys.cube1.pos         = (110, 150)
cfg.toys.cube1.width       = 40
cfg.toys.cube1.type        = 'cube'
cfg.toys.cube1.friction    = 1.0
cfg.toys.cube1.restitution = 0.7
cfg.toys.cube1.density     = 1.0

cfg.toys.cube2.pos         = (150, 110)
cfg.toys.cube2.width       = 40
cfg.toys.cube2.type        = 'cube'
cfg.toys.cube2.friction    = 1.0
cfg.toys.cube2.restitution = 0.7
cfg.toys.cube2.density     = 1.0



cfg.toy_order = ['ball1', 'ball2', 'ball3', 'cube1', 'cube2']

box = boxsim.UniformizeSim(boxsim.BoxSim(cfg))

#order = [random.uniform(bi_min, bi_max) for (bi_min, bi_max) in box.m_bounds]
order = [0.5] * 12 + [0.0]
print box.execute_order(order)

box.close()
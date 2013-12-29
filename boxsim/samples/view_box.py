import testenv
import boxsim
from common import cfg

cfg.arm.lengths    = (300.0/10,)*10
cfg.toys.ball1.pos = (550, 425)
cfg.arm.limits     = (-3.0, 3.0)
cfg.arm.self_collisions = False
cfg.arm.noise      = 0.01

box = boxsim.Simulation(cfg)

print(box.execute_order([0.5]*11 + [0.5]*3+[1.0]*8+[0.4]))

#print(box.execute_order([0.58]+[0.5]*19+[0.0]))

box.close()
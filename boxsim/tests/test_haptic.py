import testenv
import random

import boxsim
from common import cfg

cfg.com.visu = False

cfg.toys.ball1.friction       = 1.0
cfg.toys.ball1.restitution    = 1.0
cfg.toys.ball1.density        = 0.5
cfg.toys.ball1.linear_damping = 0.3

cfg.sprimitive.name = 'haptic'
cfg.sprimitive.object_name = 'ball1'

box = boxsim.Simulation(cfg)

max_norm = 0.0
for _ in range(10000):
    order = [random.random() for _ in range(13)]
    feedback = box.execute_order(order)
    max_norm = max(feedback[1], max_norm)
    print max_norm

box.close()
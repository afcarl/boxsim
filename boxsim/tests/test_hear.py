import testenv
import random
import sys

import boxsim
from common import cfg

cfg.com.visu = False

cfg.toys.ball1.friction       = 1.0
cfg.toys.ball1.restitution    = 1.0
cfg.toys.ball1.density        = 0.5
cfg.toys.ball1.linear_damping = 0.3

cfg.sprimitive.name = 'hear'
cfg.sprimitive.object_name = 'ball1'

box = boxsim.Simulation(cfg)

count = 0
for _ in range(10000):
    if _ % 10 == 0:
        print('{}/10000\r'.format(_)),
        sys.stdout.flush()
    order = [random.random() for _ in range(13)]
    feedback = box.execute_order(order)
    if feedback[2] != 0.0:
        count += 1


box.close()
print("{}/{}".format(count, 1000))
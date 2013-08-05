import testenv
import random

import boxsim
from common import cfg

cfg.motors = 'fullmotor'
box = boxsim.BoxSim(cfg)

#order = [random.uniform(bi_min, bi_max) for (bi_min, bi_max) in box.m_bounds]
order = 6*[0.0]+6*[0.2] + [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
print box.execute_order(order)

box.close()
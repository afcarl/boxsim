import testenv
import random

import boxsim
from common import cfg

box = boxsim.UniformizeSim(boxsim.BoxSim(cfg))

#order = [random.uniform(bi_min, bi_max) for (bi_min, bi_max) in box.m_bounds]
order = [0.69, -0.36, -0.19, -0.94, -0.07, -0.72, 0.65, -0.02, -0.36, 0.23, -0.75, -0.35, 0.91]
print box.execute_order(order)

box.close()
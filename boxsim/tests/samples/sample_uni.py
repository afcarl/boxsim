import testenv
import random

from common import cfg
import boxsim

cfg.visu    = False
cfg.debug   = False
cfg.verbose = True
box = boxsim.UniformizeSim(boxsim.BoxSim(cfg))

try:
    for _ in range(100):
        order = [random.uniform(0.0, 1.0) for _ in range(13)]
        print box.execute_order(order)
except Exception as e:
    print e
    box.close()
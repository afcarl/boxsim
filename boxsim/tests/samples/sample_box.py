import testenv
import boxsim
from common import cfg

box = boxsim.Simulation(cfg)

print box.execute_order([0.685, 0.581, 0.725, 0.271, 0.752, 0.425, 0.252, 0.756, 0.262, 0.083, 0.290, 0.712, 0.699])

box.close()
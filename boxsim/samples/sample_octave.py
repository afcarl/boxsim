import testenv
import boxsim
from common import cfg

cfg.com.visu = True

cfg.toys.ball1.friction       = 1.0
cfg.toys.ball1.restitution    = 1.0
cfg.toys.ball1.density        = 0.5
cfg.toys.ball1.linear_damping = 0.3

cfg.sprimitive.name = 'octave'
cfg.sprimitive.object_name = 'ball1'

box = boxsim.Simulation(cfg)

print(box.execute_order([0.685, 0.581, 0.725, 0.271, 0.752, 0.425, 0.252, 0.756, 0.262, 0.083, 0.290, 0.712, 0.699]))
print(box.execute_order([0.580, 0.641, 0.423, 0.792, 0.456, 0.523, 0.603, 0.284, 0.105, 0.187, 0.617, 0.271, 0.507]))
print(box.execute_order([0.685, 0.581, 0.725, 0.271, 0.752, 0.425, 0.252, 0.756, 0.262, 0.083, 0.290, 0.712, 0.000]))
print(box.execute_order([0.756, 0.505, 0.562, 0.552, 0.573, 0.457, 0.055, 0.161, 0.377, 0.401, 0.041, 0.432, 0.927]))
box.close()
import testenv
import boxsim
from common import cfg

cfg.toys.ball1.pos             = (550, 350)
cfg.toys.ball1.width           = 40
cfg.toys.ball1.type            = 'ball'
cfg.toys.ball1.friction        = 1.0
cfg.toys.ball1.restitution     = 0.7
cfg.toys.ball1.density         = 1.0
cfg.toys.ball1.linear_damping  = 0.3
cfg.toys.ball1.angular_damping = 0.1

cfg.toys.ball2.pos             = (300, 600)
cfg.toys.ball2.width           = 40
cfg.toys.ball2.type            = 'ball'
cfg.toys.ball2.friction        = 1.0
cfg.toys.ball2.restitution     = 0.7
cfg.toys.ball2.density         = 1.0
cfg.toys.ball2.linear_damping  = 0.3
cfg.toys.ball2.angular_damping = 0.1

cfg.sprimitive.object_name = 'ball2'

box = boxsim.Simulation(cfg)

box.execute_order([0.685, 0.581, 0.725, 0.271, 0.752, 0.425, 0.252, 0.756, 0.262, 0.083, 0.290, 0.712, 0.699])
box.execute_order([0.580, 0.641, 0.423, 0.792, 0.456, 0.523, 0.603, 0.284, 0.105, 0.187, 0.617, 0.271, 0.507])

box.close()
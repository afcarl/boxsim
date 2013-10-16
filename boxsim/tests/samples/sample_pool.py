import testenv
import boxsim
from common import cfg

cfg.toys.ball2.pos         = (200, 600)
cfg.toys.ball2.width       = 40
cfg.toys.ball2.type        = 'ball'
cfg.toys.ball2.friction    = 1.0
cfg.toys.ball2.restitution = 0.7
cfg.toys.ball2.density     = 1.0

cfg.sprimitive.object_name = 'ball2'

box = boxsim.Simulation(cfg)

box.execute_order([0.685, 0.581, 0.725, 0.271, 0.752, 0.425, 0.252, 0.756, 0.262, 0.083, 0.290, 0.712, 0.699])

box.execute_order([0.579843533548397, 0.6412767414026208, 0.42324035141176786, 0.7924499902163639, 0.4559997987480451, 0.5229572299341468, 0.6026852535872274, 0.28393988706497864, 0.10488446737970147, 0.187015368013434, 0.6166246699412306, 0.27077833538579243, 0.5065892864098486])

raw_input()
box.close()
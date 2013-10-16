import testenv
import random
import traceback

import boxsim
from common import cfg

def test_pool():
    """Test that uniformized sim produce coherent results"""
    check = True

    cfg.toys.ball2.pos         = (200, 600)
    cfg.toys.ball2.width       = 40
    cfg.toys.ball2.type        = 'ball'
    cfg.toys.ball2.friction    = 1.0
    cfg.toys.ball2.restitution = 0.7
    cfg.toys.ball2.density     = 1.0

    cfg.sprimitive.object_name = 'ball2'

    box = boxsim.Simulation(cfg)


    try:
        for _ in range(1000):
            order = [random.random() for _ in range(13)]
            pos = box.execute_order(order)
            if pos[2] == 1.0:
                print order
            if pos[2] == 0.0:
                check *= toy_pos == pos
            if pos[:2] == toy_pos[:2]:
                check *= toy_pos[2] == pos[2]
            check *= all(0 <= pos_i <= 1 for pos_i in pos)

    except Exception as e:
        traceback.print_exc()
        check = False

    box.close()

    return check


tests = [test_pool]

if __name__ == "__main__":
    print("\033[1m%s\033[0m" % (__file__,))
    for t in tests:
        print('%s %s' % ('\033[1;32mPASS\033[0m' if t() else
                         '\033[1;31mFAIL\033[0m', t.__doc__))

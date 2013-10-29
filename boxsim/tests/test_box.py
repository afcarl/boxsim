import testenv
import random
import traceback

import boxsim
from common import cfg

def test_unibox():
    """Test that uniformized sim produce coherent results"""
    check = True

    box = boxsim.Simulation(cfg)

    try:
        order = [0.5] * 12 + [0.0]
        toy_pos = box.execute_order(order)
        check *= toy_pos[2] == 0.0

        for _ in range(100):
            order = [random.random() for _ in range(13)]
            pos = box.execute_order(order)
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


tests = [test_unibox]

if __name__ == "__main__":
    print("\033[1m%s\033[0m" % (__file__,))
    for t in tests:
        print('%s %s' % ('\033[1;32mPASS\033[0m' if t() else
                         '\033[1;31mFAIL\033[0m', t.__doc__))

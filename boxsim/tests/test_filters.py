import testenv
import random
import traceback

import treedict
import boxsim
from common import cfg

class MockSim(object):

    def __init__(self):
        self.s_feats = range(10)
        self.s_bounds = tuple((i+0.0, i+1.0) for i in range(10))
        self.m_feats = range(-1, 0)
        self.m_bounds = ((0.0, 1.0),)
        self.cfg = treedict.TreeDict()
        self.cfg.verbose = False

    def execute_order(self, effect, **kwargs):
        return tuple(random.uniform(si_min, si_max) for si_min, si_max in self.s_bounds)

def test_filterbox1():
    """Test that filtered sim produces coherent attributes"""
    check = True

    sim = MockSim()
    fsim = boxsim.FilterSim(sim, s_feats = range(5))

    check *= fsim.s_feats == (0, 1, 2, 3, 4)
    check *= fsim.s_bounds == ((0.0, 1.0), (1.0, 2.0), (2.0, 3.0), (3.0, 4.0), (4.0, 5.0))

    return check

def test_filterbox2():
    """Test that filtered sim produces coherent results"""
    check = True

    sim = MockSim()
    fsim = boxsim.FilterSim(sim, s_feats = range(5))

    for i in range(1000):
        order = [random.random()]
        effect = fsim.execute_order(order)

        check *= len(effect) == 5 and all(i<= e_i <= i+1 for i, e_i in enumerate(effect))

    return check

def test_filterbox3():
    """Test that filtered sim produces coherent factored s_bounds"""
    check = True

    sim = MockSim()
    fsim = boxsim.FilterSim(sim, s_feats = range(2), s_bounds_factor = ((1.0, 2.0), (3.0, 1.0)))

    check *= fsim.s_feats == (0, 1)
    check *= fsim.s_bounds == ((0.0, 2.0), (-1.0, 2.0),)

    return check


tests = [test_filterbox1,
         test_filterbox2,
         test_filterbox3]

if __name__ == "__main__":
    print("\033[1m%s\033[0m" % (__file__,))
    for t in tests:
        print('%s %s' % ('\033[1;32mPASS\033[0m' if t() else
                         '\033[1;31mFAIL\033[0m', t.__doc__))
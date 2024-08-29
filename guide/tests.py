import unittest
from symbolic import is_reduced, simplify

class TestIsReduced(unittest.TestCase):
    def test_is_reduced(self):
        self.assertTrue(is_reduced("(0)"), f"ERR: (0) failed")
        self.assertTrue(is_reduced("(1)"), f"ERR: (1) failed")
        self.assertTrue(is_reduced("(x)"), f"ERR: (x) failed")
        self.assertTrue(is_reduced("(y)"), f"ERR: (y) failed")
        self.assertTrue(is_reduced("(x and y)"), f"ERR: (x and y) failed")
        self.assertTrue(is_reduced("(y and x)"), f"ERR: (y and x) failed")
        self.assertTrue(is_reduced("(y and x and z)"), f"ERR: (y and x and z) failed")
        self.assertTrue(is_reduced("(y or z)"), f"ERR: (y or z) failed")
        self.assertTrue(is_reduced("(y or x)"), f"ERR: (y or x) failed")
        self.assertTrue(is_reduced("(x or y)"), f"ERR: (x or y) failed")
        self.assertFalse(is_reduced("(y and x and z or y)"), f"ERR: (y and x and z or y) failed")
        self.assertFalse(is_reduced("(y and x or 1)"), f"ERR: (y and x or 1) failed")
        self.assertFalse(is_reduced("(x or 1)"), f"ERR: (x or 1) failed")
        self.assertFalse(is_reduced("(1 or x)"), f"ERR: (1 or x) failed")

class TestSimplificationEngine(unittest.TestCase):
    def test_simplify(self):        
        a = simplify(expr="x or 0", item_history=("", [], []))
        self.assertEqual(a, ('x', ['x'], ['Simplification Law']))

        a = simplify(expr="0 or x", item_history=("", [], []))
        self.assertEqual(a, ('x', ['x'], ['Simplification Law']))

        a = simplify(expr="x or 1", item_history=("", [], []))
        self.assertEqual(a, ('(1)', ['(1)'], ['Simplification Law']))

        a = simplify(expr="1 or x", item_history=("", [], []))
        self.assertEqual(a, ('(1)', ['(1)'], ['Simplification Law']))

        a = simplify(expr="x and 1", item_history=("", [], []))
        self.assertEqual(a, ('x', ['x'], ['Simplification Law']))

        a = simplify(expr="1 and x", item_history=("", [], []))
        self.assertEqual(a, ('x', ['x'], ['Simplification Law']))

        a = simplify(expr="x and 0", item_history=("", [], []))
        self.assertEqual(a, ('(0)', ['(0)'], ['Simplification Law']))

        a = simplify(expr="0 and x", item_history=("", [], []))
        self.assertEqual(a, ('(0)', ['(0)'], ['Simplification Law']))
        
        a = simplify(expr="(x and 1) or 0", item_history=("", [], []))
        res = ('x', ['(x and 1)', 'x'], ['Simplification Law', 'Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not 0", item_history=("", [], []))
        res = ('(1)', ['(1)'], ['Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not 1", item_history=("", [], []))
        res = ('(0)', ['(0)'], ['Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not not x", item_history=("", [], []))
        res = ('x', ['x'], ['Simplification Law (Double Negation)'])
        self.assertEqual(a, res)

if __name__ == '__main__':
    unittest.main()
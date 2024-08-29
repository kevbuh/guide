import unittest
from symbolic import is_reduced, simplify

class TestIsReduced(unittest.TestCase):
    def test_is_reduced(self):
        self.assertTrue(is_reduced("(0)"), f"ERR: (0) failed")
        self.assertTrue(is_reduced("(1)"), f"ERR: (1) failed")
        self.assertTrue(is_reduced("(a)"), f"ERR: (a) failed")
        self.assertTrue(is_reduced("(b)"), f"ERR: (b) failed")
        self.assertTrue(is_reduced("(a and b)"), f"ERR: (a and b) failed")
        self.assertTrue(is_reduced("(b and a)"), f"ERR: (b and a) failed")
        self.assertTrue(is_reduced("(b and a and c)"), f"ERR: (b and a and c) failed")
        self.assertTrue(is_reduced("(b or c)"), f"ERR: (b or c) failed")
        self.assertTrue(is_reduced("(b or a)"), f"ERR: (b or a) failed")
        self.assertTrue(is_reduced("(a or b)"), f"ERR: (a or b) failed")
        self.assertFalse(is_reduced("(b and a and c or b)"), f"ERR: (b and a and c or b) failed")
        self.assertFalse(is_reduced("(b and a or 1)"), f"ERR: (b and a or 1) failed")
        self.assertFalse(is_reduced("(a or 1)"), f"ERR: (a or 1) failed")
        self.assertFalse(is_reduced("(1 or a)"), f"ERR: (1 or a) failed")

class TestSimplificationEngine(unittest.TestCase):
    def test_simplify(self):        
        a = simplify(expr="a or 0", item_history=("", [], []))
        self.assertEqual(a, ('a', ['a'], ['Simplification Law']))

        a = simplify(expr="0 or a", item_history=("", [], []))
        self.assertEqual(a, ('a', ['a'], ['Simplification Law']))

        a = simplify(expr="a or 1", item_history=("", [], []))
        self.assertEqual(a, ('(1)', ['(1)'], ['Simplification Law']))

        a = simplify(expr="1 or a", item_history=("", [], []))
        self.assertEqual(a, ('(1)', ['(1)'], ['Simplification Law']))

        a = simplify(expr="a and 1", item_history=("", [], []))
        self.assertEqual(a, ('a', ['a'], ['Simplification Law']))

        a = simplify(expr="1 and a", item_history=("", [], []))
        self.assertEqual(a, ('a', ['a'], ['Simplification Law']))

        a = simplify(expr="a and 0", item_history=("", [], []))
        self.assertEqual(a, ('(0)', ['(0)'], ['Simplification Law']))

        a = simplify(expr="0 and a", item_history=("", [], []))
        self.assertEqual(a, ('(0)', ['(0)'], ['Simplification Law']))
        
        a = simplify(expr="(a and 1) or 0", item_history=("", [], []))
        res = ('a', ['(a and 1)', 'a'], ['Simplification Law', 'Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not 0", item_history=("", [], []))
        res = ('(1)', ['(1)'], ['Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not 1", item_history=("", [], []))
        res = ('(0)', ['(0)'], ['Simplification Law'])
        self.assertEqual(a, res)

        a = simplify(expr="not not a", item_history=("", [], []))
        res = ('a', ['a'], ['Simplification Law (Double Negation)'])
        self.assertEqual(a, res)

if __name__ == '__main__':
    unittest.main()
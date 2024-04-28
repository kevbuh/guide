import unittest
from symbolic import is_reduced

class TestIsReduced(unittest.TestCase):
    def test_is_reduced(self):
        self.assertTrue(is_reduced("(0)"), f"ERR: (0) failed")
        self.assertTrue(is_reduced("(1)"), f"ERR: (1) failed")
        self.assertTrue(is_reduced("(x)"), f"ERR: (x) failed")
        self.assertTrue(is_reduced("(y)"), f"ERR: (y) failed")
        self.assertTrue(is_reduced("(x and y)"), f"ERR: (x and y) failed")
        self.assertTrue(is_reduced("(y and x)"), f"ERR: (y and x) failed")
        self.assertTrue(is_reduced( "(y and x and z)"), f"ERR: (y and x and z) failed")
        self.assertTrue(is_reduced("(y or z)"), f"ERR: (y or z) failed")
        self.assertTrue(is_reduced("(y or x)"), f"ERR: (y or x) failed")
        self.assertTrue(is_reduced("(x or y)"), f"ERR: (x or y) failed")
        self.assertFalse(is_reduced("(y and x and z or y)"), f"ERR: (y and x and z or y) failed")
        self.assertFalse(is_reduced("(y and x or 1)"), f"ERR: (y and x or 1) failed")
        self.assertFalse(is_reduced("(x or 1)"), f"ERR: (x or 1) failed")
        self.assertFalse(is_reduced("(1 or x)"), f"ERR: (1 or x) failed")

if __name__ == '__main__':
    unittest.main()
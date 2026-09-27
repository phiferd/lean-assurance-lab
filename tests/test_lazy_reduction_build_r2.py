import unittest
from lib.lazy_reduction_build_r2 import corrected_driver

class DriverTests(unittest.TestCase):
    def test_preserves_cxx_driver_semantics_and_all_frozen_inputs(self):
        before=['/Library/Developer/CommandLineTools/usr/bin/clang','-std=c++20','src/main.cpp','-o','target']
        after=corrected_driver(before)
        self.assertEqual(after[0],'/Library/Developer/CommandLineTools/usr/bin/clang++')
        self.assertEqual(after[1:],before[1:])
        self.assertTrue(before[0].endswith('/clang'))

if __name__=='__main__': unittest.main()

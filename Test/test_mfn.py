from Processor import mfn
import unittest
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class mfnUnitTest(unittest.TestCase):

    def testMean(self):
        self.assertEqual(mfn.mean([1, 2, 3]), 2)

if __name__ == "__main__":
    unittest.main()

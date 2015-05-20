from Processor import processor
import unittest
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class processorUnitTest(unittest.TestCase):

    def testDRange(self):
        processor.drange(0, 2, 0.25)

if __name__ == "__main__":
    unittest.main()

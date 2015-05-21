from Processor import processor
import unittest
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class ProcessorUnitTest(unittest.TestCase):

    def runTest(self):
        self.testDRange()

    def testDRange(self):
        processor.f_range(0, 2, 0.25)


import unittest
import logging

from Testing import test_db, test_mfn, test_processor

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_db.DBUnitTest())
    suite.addTest(test_mfn.MfnUnitTest())
    suite.addTest(test_processor.ProcessorUnitTest())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = test_suite()
    runner.run(test_suite)

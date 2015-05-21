from Database import dbaccess as dba
from Database import dbupdate as dbu
from Database import dbapi
import unittest
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class DBUnitTest(unittest.TestCase):

    def runTest(self):
        self.testAccess()
        self.testAPI()
        self.testUpdate()

    def testAccess(self):
        num = dba.displaySpectraNum()
        logging.debug("Spectrum number is " + str(num))
        dba.getSpectrumFromID(4)
        dba.getSpectrumFromDoping('78K UD')

    def testAPI(self):
        self.assertEqual(dbapi.seriesToText([1, 2, 3]), "1,2,3")
        self.assertEqual(dbapi.textToSeries("1,2,3"), [1, 2, 3])

    def testUpdate(self):
        dbu.insertGap(5, 0.261, 10)
        dbu.removeGap(5)
        new_id = dbu.insertSpectrum(
            [2.12, 2.123, 5.643], [12.3, 1, 123], "78K UD")
        dbu.removeSpectrum(new_id)



from Processor import mfn
import unittest
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class MfnUnitTest(unittest.TestCase):

    def runTest(self) -> None:
        self.testMean()
        self.testStdDev()
        self.testBoxcar()
        self.testBoxcarSimple()
        self.testSample()
        self.testSimpleSample()
        self.testNormalize()
        self.testLinearRegression()
        self.testTranspose1D()

    def testMean(self) -> None:
        self.assertEqual(mfn.mean([1, 2, 3]), 2)
        self.assertEqual(mfn.mean([]), 0)

    def testStdDev(self) -> None:
        self.assertEqual(mfn.std_dev([1, 1, 1]), 0)
        self.assertEqual(mfn.std_dev([1, 2, 3]), 1)
        self.assertEqual(mfn.std_dev([1]), 0)

    def testBoxcar(self) -> None:
        self.assertEquals(
            mfn.boxcar([[1, 2, 3], [2, 3, 4], [3, 4, 5]], 3),
            [[2.0, 3.0, 4.0]])
        self.assertEquals(
            mfn.boxcar([[1, 2, 3], [2, 3, 4], [6, 5, 4], [3, 4, 5]], 3, [2]),
            [[1.5, 2.5, 3.5], [2.5, 3.5, 4.5]])
        self.assertEquals(
            mfn.boxcar([[1, 2, 3], [2, 3, 4], [6, 5, 4], [3, 4, 5]], 3, [0, 1, 2]),
            [[3.0, 4.0, 5.0]])

    def testBoxcarSimple(self) -> None:
        self.assertEquals(mfn.boxcar_simple([1, 2, 3, 4, 5], 3), [2, 3, 4])
        self.assertEquals(mfn.boxcar_simple([1, 3, 5, 7, 9], 3), [3, 5, 7])

    def testSample(self) -> None:
        self.assertEquals(
            mfn.sample([[1, 2, 3], [2, 3, 4], [3, 4, 5]], 3),
            [[2.0, 3.0, 4.0]])
        self.assertEquals(
            mfn.sample([[1, 2, 3], [2, 3, 4], [3, 4, 5],
                        [4, 5, 6], [5, 6, 7], [6, 7, 8]], 3),
            [[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
        self.assertEquals(
            mfn.sample([[1, 2, 3], [2, 3, 4], [3, 4, 5],
                        [4, 5, 6], [5, 6, 7], [6, 7, 8]], 3, [2]),
            [[1.5, 2.5, 3.5], [5.0, 6.0, 7.0]])
        self.assertEquals(
            mfn.sample([[1, 2, 3], [2, 3, 4], [3, 4, 5],
                        [4, 5, 6], [5, 6, 7], [6, 7, 8]], 3, [0, 1, 2]),
            [[5.0, 6.0, 7.0]])

    def testSimpleSample(self) -> None:
        self.assertEquals(mfn.sample_simple([1, 2, 3, 4, 5, 6], 3), [2.0, 5.0])

    def testNormalize(self) -> None:
        self.assertEqual(mfn.normalize([1, 1, 1, 1], 1), [0.25, 0.25, 0.25, 0.25])
        self.assertEqual(mfn.normalize([0, 0, 0, 0], 1), [0.0, 0.0, 0.0, 0.0])

    def testLinearRegression(self) -> None:
        self.assertEquals(mfn.linear_regression([1, 2, 3], [2, 3, 4]), (1, 1))
        self.assertEquals(mfn.linear_regression([1, 2, 3], [2, 4, 6]), (2, 0))

    def testTranspose1D(self) -> None:
        self.assertEquals(mfn.transpose1d([1, 2, 3]), [[1], [2], [3]])

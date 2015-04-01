#!/usr/bin/env python
import numpy as np

__author__ = 'Colin Tan'
__version__ = '2.3.5'


# calculate mean for a number list
def mean(numbers):
    if numbers:
        n, ave = len(numbers), 0
        ave = sum(numbers)
        ave /= float(n)
    else:
        ave = 0
    return ave


# calculate standard deviation for a number list
def stdev(numbers):
    from math import sqrt
    n, ave, std = len(numbers), mean(numbers), 0
    for a in numbers:
        std += (a - ave) ** 2
    if n > 1:
        std = sqrt(std / float(n - 1))
    else:
        std = sqrt(std / float(n))
    return std


# absolute value
def abs(num):
    if num < 0:
        return -num
    else:
        return num


# calculate boxcar average across a list of number lists with the odd
# width defined, and optional exclusion list of indices that the
# function skips but treat the skipped item as a position
def boxcar(numbers, width, exclusion=None):
    boxed = []
    for i in range((width - 1) / 2, len(numbers) - (width - 1) / 2):
        subbox = []
        for j in range(0, len(numbers[i])):
            subsubbox = []
            rg = range(i - (width - 1) / 2, i + 1 + (width - 1) / 2)
            for k in rg:
                if exclusion is None:
                    subsubbox.append(numbers[k][j])
                elif k not in exclusion:
                    subsubbox.append(numbers[k][j])
                elif set(rg).issubset(exclusion):
                    # if the whole width is excluded, skip
                    break
            subbox.append(mean(subsubbox))
        boxed.append(subbox)
    return boxed


# sample by averaging over a defined width of a list of number lists,
# with the width defined and optional exclusion list of indices that
# the function skips but treat the skipped item as a position
def sample(numbers, width, exclusion=None):
    averaged = []
    for i in range(0, len(numbers), width):
        subave = []
        for j in range(0, len(numbers[i])):
            subsubave = []
            rg = [x for x in range(i, i + width) if x < len(numbers)]
            for k in rg:
                if exclusion is None:
                    subsubave.append(numbers[k][j])
                elif k not in exclusion:
                    subsubave.append(numbers[k][j])
                elif set([x for
                          x in range(i, i + width)
                          if x < len(numbers)]).issubset(exclusion):
                    # if the whole width is excluded, skip
                    break
            subave.append(mean(subsubave))
        averaged.append(subave)
    return averaged


# calculate boxcar average for a number list
# with the odd width defined
def boxcar_simple(numbers, width):
    boxed = []
    for i in range((width - 1) / 2, len(numbers) - (width - 1) / 2):
        boxed.append(mean(numbers[i - (width - 1) / 2:
                                  i + 1 + (width - 1) / 2]))
    return boxed


# sample by averaging over a defined width
def sample_simple(numbers, width):
    averaged = []
    for i in range(0, len(numbers), width):
        averaged.append(mean(numbers[i:i + width]))
    return averaged


# normalize a number list, such that sum = const, with
# the ablilty to regard to only a portion of the data
def normalize(numbers, const, start=0, end=None):
    if end is None:
        end = len(numbers)
    sum = 0
    for i in range(start, end):
        sum += float(numbers[i])
    if sum is not 0.0:
        return [const * x / sum for x in numbers]
    else:
        return [0.0] * len(numbers)


# obtain gap size from one y series with the method of getting
# the double of the one-sided gap, which is determined by defined
# percentage of this side's plateau level, which is in turn
# approximated from the defined section from the series
def get_gap(yser, center_index, percent, start, end, search_dir='right'):
    threshold = mean(yser[start:end]) * percent
    diff = []
    if search_dir is 'right':
        for i in range(start, center_index, -1):
            diff.append(abs(yser[i] - threshold))
        return len(diff) - diff.index(min(diff))
    else:
        for i in range(start, center_index):
            diff.append(abs(yser[i] - threshold))
        return diff.index(min(diff)) + 1


# linear regression gap computation algorithm
def lin_gap(xser, yser, ci, percent, start, end, search_dir='right'):
    a, b = linear_regression(xser[start:end], yser[start:end])
    for i in range(0, len(yser)):
        yser[i] -= a * xser[i] + b
    return get_gap_peak(yser, percent, search_dir)


# get gap size from peak
def get_gap_peak(yser, percent, search_dir='right'):
    ymin = min(yser)
    ymin_index = yser.index(ymin)
    threshold = ymin * (1 - percent)
    diff = []
    if search_dir is 'right':
        for i in range(ymin_index, len(yser)):
            diff.append(abs(yser[i] - threshold))
        return diff.index(min(diff)) + 1
    else:
        for i in range(0, ymin_index):
            diff.append(abs(yser[i] - threshold))
        return len(diff) - diff.index(min(diff))


# linear regression algorithm
def linear_regression(x, y):
    length = len(x)
    sum_x = sum(x)
    sum_y = sum(y)

    sum_x_squared = sum(map(lambda a: a * a, x))
    sum_of_products = sum([x[i] * y[i] for i in range(length)])

    a = (sum_of_products - (sum_x *
                            sum_y) / length) / (sum_x_squared
                                                - ((sum_x ** 2) / length))
    b = (sum_y - a * sum_x) / length
    return a, b


# polynomial regression gap computation algorithm
# by computing fourth degree polynomial and taking
# second derivative to locate the gap
def poly_gap(xser, yser, gapmin, gapmax):
    # calculate polyfit, and convert it into 1D object
    z = np.poly1d(np.polyfit(xser, yser, 5))
    # take derivatives
    deriv3 = z.deriv().deriv().deriv()
    # find the peak of the third derivative
    root3 = deriv3.r
    return pick_root(root3.tolist())


# custom picking out roots
# smaller in real roots
# and single real root
def pick_root(roots):
    if len(roots) == 2:
        root1 = roots[0]
        root2 = roots[1]
        if root1.real < 0.0:
            if root2.imag == 0:
                return root2.real
        elif root2.real < 0.0:
            if root1.imag == 0:
                return root1.real
        elif root1.imag == 0 and root2.imag == 0:
            return min(root1.real, root2.real)
        elif root1.imag != 0:
            return root1.real
        else:
            return 0.0
    else:
        return 0.0

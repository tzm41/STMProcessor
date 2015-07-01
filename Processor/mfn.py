#!/usr/bin/env python3
import numpy as np

__author__ = 'Colin Tan'
__version__ = '2.5'


# calculate mean for a number list
def mean(numbers) -> float:
    if numbers:
        n, ave = len(numbers), 0
        ave = sum(numbers)
        ave /= float(n)
    else:
        ave = 0
    return ave


# calculate standard deviation for a number list
def std_dev(numbers) -> float:
    from math import sqrt
    n, ave, std = len(numbers), mean(numbers), 0
    for a in numbers:
        std += (a - ave) ** 2
    if n > 1:
        std = sqrt(std / float(n - 1))
    else:
        std = sqrt(std / float(n))
    return std


# calculate boxcar average across a list of number lists with the odd
# width defined, and optional exclusion list of indices that the
# function skips but treat the skipped item as a position
def boxcar(numbers, width, exclusion=None):
    boxed = []
    for i in range(int((width - 1) / 2), int(len(numbers) - (width - 1) / 2)):
        sub_box = []
        has_content = True
        for j in range(0, len(numbers[i])):
            sub_sub_box = []
            rg = range(int(i - (width - 1) / 2), int(i + 1 + (width - 1) / 2))
            for k in rg:
                if exclusion is None:
                    sub_sub_box.append(numbers[k][j])
                elif k not in exclusion:
                    sub_sub_box.append(numbers[k][j])
                elif set(rg).issubset(exclusion):
                    # if the whole width is excluded, skip
                    has_content = False
                    break
            if has_content is True:
                sub_box.append(mean(sub_sub_box))
        if has_content is True:
            boxed.append(sub_box)
    return boxed


# sample by averaging over a defined width of a list of number lists,
# with the width defined and optional exclusion list of indices that
# the function skips but treat the skipped item as a position
def sample(numbers, width, exclusion=None):
    averaged = []
    for i in range(0, len(numbers), width):
        sub_ave = []
        has_content = True
        for j in range(0, len(numbers[i])):
            sub_sub_ave = []
            rg = [x for x in range(i, i + width) if x < len(numbers)]
            for k in rg:
                if exclusion is None:
                    sub_sub_ave.append(numbers[k][j])
                elif k not in exclusion:
                    sub_sub_ave.append(numbers[k][j])
                elif set([x for
                          x in range(i, i + width)
                          if x < len(numbers)]).issubset(exclusion):
                    # if the whole width is excluded, skip
                    has_content = False
                    break
            if has_content is True:
                sub_ave.append(mean(sub_sub_ave))
        if has_content is True:
            averaged.append(sub_ave)
    return averaged


# calculate boxcar average for a number list
# with the odd width defined
def boxcar_simple(numbers, width) -> [float]:
    boxed = []
    for i in range(int((width - 1) / 2), int(len(numbers) - (width - 1) / 2)):
        boxed.append(mean(
            numbers[int(i - (width - 1) / 2):int(i + 1 + (width - 1) / 2)]))
    return boxed


# sample by averaging over a defined width
def sample_simple(numbers, width) -> [float]:
    averaged = []
    for i in range(0, len(numbers), width):
        averaged.append(mean(numbers[i:i + width]))
    return averaged


# normalize a number list, such that sum = const, with
# the ability to regard to only a portion of the data
def normalize(numbers, const, start=0, end=None) -> [float]:
    if end is None:
        end = len(numbers)
    total = 0
    for i in range(start, end):
        total += float(numbers[i])
    if total != 0.0:
        return [const * x / total for x in numbers]
    else:
        return [0.0] * len(numbers)


# obtain gap size from one y series with the method of getting
# the double of the one-sided gap, which is determined by defined
# percentage of this side's plateau level, which is in turn
# approximated from the defined section from the series
def get_gap(y_series, center_index, percent, start, end, search_dir='right') -> float:
    threshold = mean(y_series[start:end]) * percent
    diff = []
    if search_dir is 'right':
        for i in range(start, center_index, -1):
            diff.append(abs(y_series[i] - threshold))
        return len(diff) - diff.index(min(diff))
    else:
        for i in range(start, center_index):
            diff.append(abs(y_series[i] - threshold))
        return diff.index(min(diff)) + 1


# linear regression gap computation algorithm
def lin_gap(x_series, y_series, percent, start, end, search_dir='right') -> float:
    a, b = linear_regression(x_series[start:end], y_series[start:end])
    for i in range(0, len(y_series)):
        y_series[i] -= a * x_series[i] + b
    return get_gap_peak(y_series, percent, search_dir)


# get gap size from peak
def get_gap_peak(y_series, percent, search_dir='right') -> float:
    y_min = min(y_series)
    y_min_index = y_series.index(y_min)
    threshold = y_min * (1 - percent)
    diff = []
    if search_dir is 'right':
        for i in range(y_min_index, len(y_series)):
            diff.append(abs(y_series[i] - threshold))
        return diff.index(min(diff)) + 1
    else:
        for i in range(0, y_min_index):
            diff.append(abs(y_series[i] - threshold))
        return len(diff) - diff.index(min(diff))


# linear regression algorithm
def linear_regression(x, y) -> (float, float):
    length = len(x)
    sum_x = sum(x)
    sum_y = sum(y)

    sum_x_squared = sum(map(lambda k: k * k, x))
    sum_of_products = sum([x[i] * y[i] for i in range(length)])

    a = (sum_of_products - (sum_x *
                            sum_y) / length) / (sum_x_squared
                                                - ((sum_x ** 2) / length))
    b = (sum_y - a * sum_x) / length
    return a, b


# polynomial regression gap computation algorithm
# by computing fourth degree polynomial and taking
# second derivative to locate the gap
def poly_gap(x_series, y_series, gapmin, gapmax) -> float:
    # calculate poly fit, and convert it into 1D object
    z = np.poly1d(np.polyfit(x_series, y_series, 5))
    # take derivatives
    third_derivative = z.deriv().deriv().deriv()
    # find the peak of the third derivative
    root3 = third_derivative.r
    return pick_root(root3.tolist())


# custom picking out roots
# smaller in real roots, and single real root
def pick_root(roots) -> float:
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


# transpose 1D vector from horizontal to vertical
def transpose1d(vec) -> [[float]]:
    return [[row] for row in vec]

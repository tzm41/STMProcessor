#!/usr/bin/env python

import os.path
import csv
from Processor import mfn

__author__ = 'Colin Tan'
__version__ = '1.5'


# generate file path base on current python script path
def gen_path(relPath, absPath=None):
    if absPath is not None:
        return absPath
    else:
        basePath = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(basePath, relPath))


# csv writer method
def csv_writer(data, path):
    with open(path, 'wt') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


# float range method
def drange(start, end, step):
    current, list = start, []
    while current <= end:
        list.append(round(current, 7))
        current += step
    return list


# prepare file for process
# return x-series and y-series
def readFile(path_read, csv_delim):
    xs, yseries = [], []
    for path in path_read:
        # parse csv file with custom delimiter
        # 'rU' dealing with lines not ending with delimiter
        with open(path, 'rU') as csv_file:
            filecontent = csv.reader(csv_file, delimiter=csv_delim)
            openedFile = [row for row in filecontent]

        # obtain x values from the first column
        xs = [round(float(row[0]), 7) for row in openedFile]

        # obtain y values, by picking out each odd
        # column starting at index 1
        for i in range(1, len(openedFile[0]), 2):
            # remove zero spectra
            new_row = [float(row[i]) for row in openedFile]
            if new_row[0] != 0.0:
                yseries.append(new_row)

    return xs, yseries


def elimStdev(xs, yseries, stdev_multi):
    """Eliminate outliers in a group of y-series
    Args:
        xs ([float]): the x-series data
        yseries ([[float]]): potentially multiple y-series data
        stdev_multi (int): multiple of standard deviation out of which
            spectra will be eliminated
    Returns:
        Excluded indexes, and cleaned up y-series
    """
    # calculate standard deviation for each row
    # in other words, for all y values at each x value
    yStdevAtx, yMeanAtx, ysAtx = [], [], []
    # get all y values for each x value
    for i in range(len(xs)):
        ysAtx.append([col[i] for col in yseries])
    # calculate standard deviations
    for nums in ysAtx:
        yStdevAtx.append(mfn.stdev(nums))
        yMeanAtx.append(mfn.mean(nums))

    # normalize each spectrum with the average of all spectrum
    ysum = sum(yMeanAtx)
    for i in range(len(yseries)):
        yseries[i] = mfn.normalize(yseries[i], ysum)

    # pick out abnormal ys by comparing with
    # specified stdev threshold
    exclusions, excluded = [], []
    for i in range(0, len(yseries)):
        for j in range(0, len(xs)):
            if abs(yseries[i][j] -
                    yMeanAtx[j]) > stdev_multi * yStdevAtx[j]:
                exclusions.append(i)
                break
    # generate filtered y series
    for num in [x for x in range(len(yseries)) if x not in exclusions]:
        excluded.append(yseries[num])
    return exclusions, excluded


def boxcar(yseries, boxcar_width, exclusions=None):
    # boxcar before gap determination
    if boxcar_width == 0:
        return yseries
    else:
        return mfn.boxcar(yseries, boxcar_width, exclusions)


# group averaging method
def groupAverage(xs, boxed, gapmin, gapmax, xstep):
    # count and export gap sizes for boxcared data
    gap_stat = []
    for col in boxed:
        # saving only five decimal places
        # have to use col[::-1] to reverse the list
        gap_stat.append(["{0:.5f}".format(mfn.poly_gap(xs[0:20], col[0:20],
                        gapmin, gapmax).real)])

    # export averaged spectra for each gap size group
    average_box, avbox_out = [[0] + xs], []
    for i in drange(gapmin, gapmax, xstep):
        ysOfGap, this_y_ave = [], [i]
        for j in range(len(gap_stat)):
            if(float(gap_stat[j][0]) > i
                    and float(gap_stat[j][0]) < i + xstep):
                ysOfGap.append(boxed[j])
        for x in range(len(xs)):
            this_y_ave.append(mfn.mean([col[x] for col in ysOfGap]))
        average_box.append(this_y_ave)
    for i in range(len(average_box[1])):
        avbox_out.append([row[i] for row in average_box])
    return gap_stat, avbox_out

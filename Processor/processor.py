#!/usr/bin/env python3

import os.path
import csv
from Processor import mfn

__author__ = 'Colin Tan'
__version__ = '1.6'


# generate file path base on current python script path
def gen_path(rel_path, abs_path=None):
    if abs_path is not None:
        return abs_path
    else:
        base_path = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(base_path, rel_path))


# csv writer method
def csv_writer(data, path):
    with open(path, 'wt') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


# float range method
def f_range(start, end, step):
    current, num_list = start, []
    while current <= end:
        num_list.append(round(current, 7))
        current += step
    return num_list


# prepare file for process
# return x-series and y-series
def read_file(path_read, csv_delimiter):
    xs, y_series = [], []
    for path in path_read:
        # parse csv file with custom delimiter
        # 'rU' dealing with lines not ending with delimiter
        with open(path, 'rU') as csv_file:
            file_content = csv.reader(csv_file, delimiter=csv_delimiter)
            opened_file = [row for row in file_content]

        # obtain x values from the first column
        xs = [round(float(row[0]), 7) for row in opened_file]

        # obtain y values, by picking out each odd
        # column starting at index 1
        for i in range(1, len(opened_file[0]), 2):
            # remove zero spectra
            new_row = [float(row[i]) for row in opened_file]
            if new_row[0] != 0.0:
                y_series.append(new_row)

    return xs, y_series


def eliminate_std_dev(xs, y_series, std_dev_multi):
    """Eliminate outliers in a group of y-series
    Args:
        xs ([float]): the x-series data
        y_series ([[float]]): potentially multiple y-series data
        std_dev_multi (int): multiple of standard deviation out of which
            spectra will be eliminated
    Returns:
        Excluded indexes, and cleaned up y-series
    """
    # calculate standard deviation for each row
    # in other words, for all y values at each x value
    y_std_dev_at_x, y_mean_at_x, ys_at_x = [], [], []
    # get all y values for each x value
    for i in range(len(xs)):
        ys_at_x.append([col[i] for col in y_series])
    # calculate standard deviations
    for nums in ys_at_x:
        y_std_dev_at_x.append(mfn.std_dev(nums))
        y_mean_at_x.append(mfn.mean(nums))

    # normalize each spectrum with the average of all spectrum
    ysum = sum(y_mean_at_x)
    for i in range(len(y_series)):
        y_series[i] = mfn.normalize(y_series[i], ysum)

    # pick out abnormal ys by comparing with
    # specified std dev threshold
    exclusions, excluded = [], []
    for i in range(0, len(y_series)):
        for j in range(0, len(xs)):
            if abs(y_series[i][j] -
                    y_mean_at_x[j]) > std_dev_multi * y_std_dev_at_x[j]:
                exclusions.append(i)
                break
    # generate filtered y series
    for num in [x for x in range(len(y_series)) if x not in exclusions]:
        excluded.append(y_series[num])
    return exclusions, excluded


def boxcar(y_series, boxcar_width, exclusions=None):
    # boxcar before gap determination
    if boxcar_width == 0:
        return y_series
    else:
        return mfn.boxcar(y_series, boxcar_width, exclusions)


# group averaging method
def group_average(xs, boxed, gap_min, gap_max, x_step):
    # count and export gap sizes for boxcar-ed data
    gap_stat = []
    for col in boxed:
        # saving only five decimal places
        # have to use col[::-1] to reverse the list
        gap_stat.append(["{0:.5f}".format(mfn.poly_gap(xs[0:20], col[0:20],
                        gap_min, gap_max).real)])

    # export averaged spectra for each gap size group
    average_box, av_box_out = [[0] + xs], []
    for i in f_range(gap_min, gap_max, x_step):
        ys_of_gap, this_y_ave = [], [i]
        for j in range(len(gap_stat)):
            if i < float(gap_stat[j][0]) < i + x_step:
                ys_of_gap.append(boxed[j])
        for x in range(len(xs)):
            this_y_ave.append(mfn.mean([col[x] for col in ys_of_gap]))
        average_box.append(this_y_ave)
    for i in range(len(average_box[1])):
        av_box_out.append([row[i] for row in average_box])
    return gap_stat, av_box_out

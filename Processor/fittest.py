#!/usr/bin/env python
import os.path
import csv
import mfn

__author__ = 'Colin Tan'
__version__ = '1.1'


# generate file path base on current python script path
def gen_path(relPath, absPath=None):
    if absPath is not None:
        return absPath
    else:
        basePath = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(basePath, relPath))


# csv writer method
def csv_writer(data, path):
    with open(path, 'wb') as csv_file:
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


# argv[0] = absolute read path
# argv[1] = relative read path
# argv[1] = boxcar width
def main(argv):
    # predefined vars
    stdev_multi = 2
    gap_size_min = 1
    gap_size_max = 3
    csv_delim = ','

    path_read = '{}/fakeSpectra2'.format(os.path.dirname(__file__))

    xs = []
    print 'Data read from file {}.'.format(path_read)

    # parse csv file with custom delimiter
    with open(path_read, 'rb') as csv_file:
        filecontent = csv.reader(csv_file, delimiter=csv_delim)
        openedFile = [row for row in filecontent]

    # obtain x values from the first column
    xs = [round(float(row[0]), 7) for row in openedFile]

    # obtain y values, by picking out each odd
    # column starting at index 1
    yseries = []
    for i in range(1, len(openedFile[0]), 2):
        yseries.append([float(row[i]) for row in openedFile])

    print 'File contains x series with {} points.'.format(len(xs))
    print 'File contains {} y series.'.format(len(yseries))

    # calculate standard deviation for each row
    # in other words, for all y values at each x value
    yStdevAtx, yMeanAtx, ysAtx = [], [], []
    # get all y values for each x value
    for i in range(0, len(xs)):
        ysAtx.append([col[i] for col in yseries])
    # calculate standard deviations
    for nums in ysAtx:
        yStdevAtx.append(mfn.stdev(nums))
        yMeanAtx.append(mfn.mean(nums))

    # pick out abnormal ys by comparing with
    # specified stdev threshold
    exclusions, excluded = [], []
    for i in xrange(0, len(yseries)):
        for j in xrange(0, len(xs)):
            if abs(yseries[i][j] -
                    yMeanAtx[j]) > stdev_multi * yStdevAtx[j]:
                exclusions.append(i)
                break
    # generate filtered y series
    for num in [x for x in xrange(0, len(yseries)) if x not in exclusions]:
        excluded.append(yseries[num])
    # before making yseries = excluded, process using boxcar
    # or sampling to prevent averaging over sparse samples

    print 'For defined {} * sigma threshold, {} y series are excluded.' \
        .format(stdev_multi, len(exclusions))

    # normalize each spectrum with the average of all spectrum
    ysum = sum(yMeanAtx)
    for i in xrange(0, len(yseries)):
        yseries[i] = mfn.normalize(yseries[i], ysum)

    # count and export gap sizes for boxcared data
    gap_stat = []
    for col in yseries:
        # saving only five decimal places
        # have to use col[::-1] to reverse the list
        gap_stat.append(["{0:.5f}".format(mfn.poly_gap(xs[21:41], col[21:41],
                        gap_size_min, gap_size_max))])
    print gap_stat

if __name__ == "__main__":
    main([])

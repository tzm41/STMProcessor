#!/usr/bin/env python
import os.path
import csv
import sys
import mfn

__author__ = 'Colin Tan'
__version__ = '2.3.1'


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
    boxcar_width = 5
    gap_size_min = 0.025
    gap_size_max = 0.425
    csv_delim = ','
    xstep = 0.025

    path_read = []
    if len(argv) == 1:
        absReadPath = argv[0]
    elif len(argv) == 2:
        absReadPath = None
        relReadPath = argv[1]
    elif len(argv) == 3:
        absReadPath = argv[0]
        relReadPath = argv[1]
        boxcar_width = argv[2]
        if absReadPath is not None:
            for path in absReadPath:
                path_read.append(path)
        else:
            for path in relReadPath:
                path_read.append(gen_path(path, None))
    else:
        print 'Invalid arguments'
        sys.exit()
    direname = os.path.dirname(path_read[0])
    path_gap = '{}/Out/gap_{}.csv'.format(direname, boxcar_width)
    path_log = '{}/Out/log_{}.txt'.format(direname, boxcar_width)
    path_ave = '{}/Out/ave_{}.csv'.format(direname, boxcar_width)

    txt_file = open(path_log, 'wb')

    xs, boxed = [], []
    for path in path_read:
        print 'Data read from file {}.'.format(path)
        txt_file.write('-----{}-----\n'.format(os.path.basename(path)))
        txt_file.write('Data read from file {}.\n'.format(path))

        # parse csv file with custom delimiter
        with open(path, 'rU') as csv_file:
            filecontent = csv.reader(csv_file, delimiter=csv_delim)
            openedFile = [row for row in filecontent]

        # obtain x values from the first column
        xs = [round(float(row[0]), 7) for row in openedFile]

        # obtain y values, by picking out each odd
        # column starting at index 1
        yseries = []
        for i in range(1, len(openedFile[0]), 2):
            # remove zero spectra
            newRow = [float(row[i]) for row in openedFile]
            if newRow[0] != 0.0:
                yseries.append(newRow)

        print 'File contains x series with {} points.'.format(len(xs))
        txt_file.write('File contains x series with {} points.\n'
                       .format(len(xs)))
        print 'File contains {} y series.'.format(len(yseries))
        txt_file.write('File contains {} y series.\n'.format(len(yseries)))

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

        # normalize each spectrum with the average of all spectrum
        ysum = sum(yMeanAtx)
        for i in xrange(0, len(yseries)):
            yseries[i] = mfn.normalize(yseries[i], ysum)

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
        txt_file.write(
            'For defined {} * sigma threshold, {} y series are excluded.\n'
            .format(stdev_multi, len(exclusions)))

        # boxcar before gap determination
        boxing = mfn.boxcar(yseries, boxcar_width, exclusions)
        print 'Boxcar width {}.'.format(boxcar_width)
        txt_file.write('Boxcar width {}.\n'.format(boxcar_width))
        boxed.extend(boxing)

    txt_file.write('-----summary-----\n')
    # count and export gap sizes for boxcared data
    gap_stat = []
    for col in boxed:
        # saving only five decimal places
        # have to use col[::-1] to reverse the list
        gap_stat.append(["{0:.5f}".format(mfn.poly_gap(xs[0:20], col[0:20],
                        gap_size_min, gap_size_max).real)])
    csv_writer(gap_stat, path_gap)
    print 'Gap stat written to file {}, containing {} numbers' \
        .format(path_gap, len(gap_stat))
    txt_file.write(
        'Gap stat after boxcar written to file {}, containing {} numbers.\n'
        .format(path_gap, len(gap_stat)))

    # export averaged spectra for each gap size group
    average_box, avbox_out = [[0] + xs], []
    for i in drange(gap_size_min, gap_size_max, xstep):
        ysOfGap, this_y_ave = [], [i]
        for j in range(0, len(gap_stat)):
            if(float(gap_stat[j][0]) > i
                    and float(gap_stat[j][0]) < i + xstep):
                ysOfGap.append(boxed[j])
        for x in range(0, len(xs)):
            this_y_ave.append(mfn.mean([col[x] for col in ysOfGap]))
        average_box.append(this_y_ave)
    for i in range(0, len(average_box[1])):
        avbox_out.append([row[i] for row in average_box])
    csv_writer(avbox_out, path_ave)
    print 'Average in gap size group' \
        ' written to file {}, containing {} series' \
        .format(path_ave, len(avbox_out[0]))
    txt_file.write(
        'Average in gap size group'
        ' written to file {}, containing {} series\n'
        .format(path_ave, len(avbox_out[0])))
    txt_file.close()

if __name__ == "__main__":
    main([['/Users/colin/Downloads/UD78-dIdV-297k.csv'], None, 10])

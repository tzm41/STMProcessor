#!/usr/bin/env python

# helper methods for DB I/Os

__author__ = 'Colin Tan'
__version__ = '0.6'


# convert float series to text
def seriesToText(series):
    return ','.join(map(str, series))


# convert text to float series
def textToSeries(text):
    return list(map(float, text.split(",")))

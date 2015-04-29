# helper methods for DB I/Os

__author__ = 'Colin Tan'
__version__ = 0.5


# convert double series to text
def seriesToText(series):
    return ','.join(map(str, series))


# convert text to double series
def textToSeries(text):
    return map(float, text.split(","))

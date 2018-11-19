#!/usr/bin/env python3

import glob
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *


def dump_values(obj):
    for key in obj:
        print("%s -> %s" % (key, obj[key]))


def dump_array_values(obj):
    i = 0
    for container in obj:
        print("### Item %d" % (i + 1))
        for key in container:
            print("%s -> %s" % (key, container[key]))

        i = i + 1


def main():
    directory = '/home/kinow/Downloads/1998/'
    for filename in glob.glob('/'.join([directory, '**/*.*'])):
        # first we check consistency between parent directory and filename
        date1 = filename.split('/')[-2]
        date2, extension = filename.split('/')[-1].split('.')
        # ignore txt files that contain only info about the file
        if 'txt' == extension:
            continue
        if not date2.startswith(date1):
            print("Parent directory does not match with file name: {} - {} and {}".format(filename, date1, date2))

        # now compare the date data from the identification section

        pccora_parser = PCCORAParser()
        pccora_parser.parse_file(filename)
        # head = pccora_parser.get_header()
        ident = pccora_parser.get_identification()

        date_within_file = ''.join([
            str(ident['message_year']), str(ident['message_month']), str(ident['message_day']),
            str(ident['message_hour'])
        ])

        if date_within_file != date2:
            print("Date in identification section does not match with file name: {} - {} and {}".format(filename,
                                                                                                        date_within_file,
                                                                                                        date2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# copied from https://github.com/vnoel/pycode/blob/master/pccora.py
# on 2016/01/10th - 05:00PM
from pccora_win import *


def dump_values_np(obj):
    for name in obj.dtype.names:
        # dtype = obj.dtype[name]
        value = obj[name][0]
        print("%s -> %s" % (name, value))


def dump_values_np_dict(obj, print_item_index=True):
    """print values created with numpy, but converted to a dict"""

    # when converted to a dict, the name is a key, and the values are a list.
    # so it becomes kind like an associative-array, or hashmap, where the name
    # is the key, and an equal-lenghted array contains the data.
    # i.e. if you have three entries, you will have for each key a list with
    # three values.
    # e.g. your data structure is name and age, and you have three entries. So
    # the data given will be in the format:
    # {
    #   name: ['John', 'Stephen'],
    #	age: [33, 25]
    # }
    # where you can view that john has 33 years, and stephen 25
    length = n = 0

    # we have to iterate twice, as sometimes a datetime object can appear first...
    for key in obj:
        if not isinstance(obj[key], datetime):
            if length == 0:
                length = len(obj[key])

    while True:
        if print_item_index:
            print("### Item %d" % (i + 1))
        for key in obj:
            # so we have to find out the data length for the first time
            if isinstance(obj[key], datetime) or isinstance(obj[key], list):
                value = obj[key]
            else:
                value = obj[key][i]
            print("%s -> %s" % (key, value))
        n += 1

        if n >= length:
            break


def main():
    file = '/home/kinow/Downloads/96010109.EDT'

    head, ident, data, hires = pccora_read(file)
    print("#PCCORA")
    print('## HEADER')
    dump_values_np(head)
    print("\n")
    print('## IDENTIFICATION')
    dump_values_np_dict(ident, False)
    print("\n")
    print("## SYSPAR")
    # no syspar data
    print("\n")
    print("## DATA")
    dump_values_np_dict(data)
    print("\n")
    print("## HIRES DATA")
    dump_values_np_dict(hires)
    print("\n")


if __name__ == '__main__':
    import plac

    plac.call(main)

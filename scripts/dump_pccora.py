#!/usr/bin/env python3

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
    file = '/home/kinow/Downloads/96010109.EDT'

    pccora_parser = PCCORAParser()
    pccora_parser.parse_file(file)
    print("#PCCORA")
    print('## HEADER')
    head = pccora_parser.get_header()
    dump_values(head)
    print("\n")
    print('## IDENTIFICATION')
    ident = pccora_parser.get_identification()
    dump_values(ident)
    print("\n")
    print("## SYSPAR")
    syspar = pccora_parser.get_syspar()
    dump_values(syspar)
    print("\n")
    print("## DATA")
    data = pccora_parser.get_data()
    dump_array_values(data)
    print("\n")
    print("## HIRES DATA")
    hires_data = pccora_parser.get_hires_data()
    dump_array_values(hires_data)
    print("\n")


if __name__ == '__main__':
    main()

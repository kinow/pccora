#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *
import math

def dump_values(obj):
    for key in obj:
        print("%s -> %s" % (key, obj[key]))

def dump_array_values(obj, elapsed_time):
    i = 0
    for container in obj:
        if 2999 <= i <= 3019:
            ti = container['time']
            p = math.exp(float(container['logarithmic_pressure'])/float(4096))
            t = float(container['temperature'])
            h = float(container['humidity'])
            nu = container['n_data']
            c = container['cycles']
            print("%s\t%s\t%.2f %.1f  %.1f\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (i+1, (ti-elapsed_time), p, t, h, nu, container['c1'], container['c2'], container['c3'], container['c4'], container['c5'], container['c6'], container['c7'], container['c8'], c))
        i = i + 1

def main():

    file = '/home/kinow/Downloads/97031210.59s'

    pccora_parser = PCCORAParser()
    pccora_parser.parse_s_file(file)
    
    head = pccora_parser.get_header()
    ident = pccora_parser.get_identification()

    elapsed_time = ident['time_elapsed']

    syspar = pccora_parser.get_syspar()
    hires_data = pccora_parser.get_hires_data()
    dump_array_values(hires_data, elapsed_time)
    print("\n")

if __name__ == '__main__':

    main()

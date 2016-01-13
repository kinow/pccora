#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *

import csv

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
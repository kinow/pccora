#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *

import csv

def convert2csv(data, options, file):
	with(open(file, 'w')) as csvfile:
		include_header = options['include_header']
		include_ident = options['include_ident']
		include_data = options['include_data']
		include_hires = options['include_hires']

		head = data['head']
		ident = data['ident']

		data_data = data['data']
		hires_data = data['hires_data']

		csvwriter = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		header_not_set = True
		csvheaders = list()

		if include_data:
			for container in data_data:
				row = list()

				if include_header:
					for key in head:
						row.append(head[key])
						if header_not_set:
							csvheaders.append(key)

				if include_ident:
					for key in ident:
						if header_not_set:
							csvheaders.append(key)
						row.append(ident[key])

				for key in container:
					if header_not_set:
						csvheaders.append(key)
					row.append(container[key])

				if header_not_set:
					csvwriter.writerow(csvheaders)
					header_not_set = False
				csvwriter.writerow(row)

		if include_hires:
			for container in hires_data:
				row = list()

				if include_header:
					for key in head:
						row.append(head[key])
						if header_not_set:
							csvheaders.append(key)

				if include_ident:
					for key in ident:
						if header_not_set:
							csvheaders.append(key)
						row.append(ident[key])

				for key in container:
					if header_not_set:
						csvheaders.append(key)
					row.append(container[key])

				if header_not_set:
					csvwriter.writerow(csvheaders)
					header_not_set = False
				csvwriter.writerow(row)


def main():
	file = '/home/kinow/Downloads/96010109.EDT'
	output = '/home/kinow/Downloads/96010109-nohead-noident-hires.CSV'

	include_header = True
	include_ident = True
	include_data = True
	include_hires = True

	pccora_parser = PCCORAParser()
	pccora_parser.parse_file(file)

	# Data
	head = pccora_parser.get_header()
	ident = pccora_parser.get_identification()
	#syspar = pccora_parser.get_syspar()
	data = pccora_parser.get_data()
	hires_data = pccora_parser.get_hires_data()

	# Call function to print CSV
	convert2csv(
		data=dict(head=head, ident=ident, data=data, hires_data=hires_data), 
		options=dict(
			include_header=include_header, 
			include_ident=include_ident,
			include_data=include_data,
			include_hires=include_hires
		),
		file=output)

if __name__ == '__main__':
	main()
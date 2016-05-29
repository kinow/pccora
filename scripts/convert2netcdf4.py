#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *

from netCDF4 import Dataset

def convert2netcdf4(data, options, file):
	head = data['head']
	ident = data['ident']

	#data_data = data['data']
	hires_data = data['hires_data']

	rootgrp = Dataset(file, "w", format="NETCDF4")
	# Attributes
	rootgrp.category = "Radiosonde"
	rootgrp.instrument = "Vaisala"
	# TODO: or should we use launch_time?
	print(pccora_identification.build(ident))
	return
	rootgrp.start_datetime = ident['datetime']

	# Dimensions
	height_dimension = rootgrp.createDimension("height")
	height_dimension.parameter = "height"
	height_dimension.units = "metre"
	height_dimension.missing_value = "-32768"

	# Variables
	for container in hires_data:
		print(container)
		break
	rootgrp.close()


def main():
	file = '/home/kinow/Downloads/96010109.EDT'
	output = '/home/kinow/Downloads/96010109-nohead-noident-hires.nc'

	pccora_parser = PCCORAParser()
	pccora_parser.parse_file(file)

	# Data
	head = pccora_parser.get_header()
	ident = pccora_parser.get_identification()
	#syspar = pccora_parser.get_syspar()
	data = pccora_parser.get_data()
	hires_data = pccora_parser.get_hires_data()

	# Call function to print CSV
	convert2netcdf4(
		data=dict(head=head, ident=ident, data=data, hires_data=hires_data), 
		options=dict(),
		file=output)

if __name__ == '__main__':
	main()
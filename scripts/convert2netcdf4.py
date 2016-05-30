#!/usr/bin/env python3
# Requires: numpy, netCDF4

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *
from construct import *

from netCDF4 import Dataset
import numpy as np

b2 = np.dtype('int16')
b4 = np.dtype('int32')
st = np.dtype('str_')

def get_type(subcon):
	if Value == subcon.__class__:
		return st
	elif FormatField == subcon.__class__:
		packer = subcon.packer
		if packer.size == 2:
			return b2
		else:
			return b4
	else:
		raise Exception("Unexpected subcon " + str(subcon))

def get_variable(dataset, subcon, name):
	variable_type = get_type(subcon)
	v = dataset.createVariable(name, variable_type, ("height", ))
	return v

def hashify_subcons(subcons):
	h = dict()
	for format_field in subcons:
		h[format_field.name] = format_field
	return h

def convert2netcdf4(data, options, file):
	head = data['head']
	ident = data['ident']

	#data_data = data['data']
	hires_data = data['hires_data']

	rootgrp = Dataset(file, "w", format="NETCDF4")

	# Dimensions
	rootgrp.createDimension("height")
	# height_dimension.parameter = "height"
	# height_dimension.units = "metre"
	# height_dimension.missing_value = "-32768"

	# Attributes
	rootgrp.category = "Radiosonde"
	rootgrp.instrument = "Vaisala"
	# TODO: or should we use launch_time?
	d = hashify_subcons(pccora_identification.subcons)
	v = get_variable(rootgrp, d['datetime'], "datetime")
	print(v)
	return
	print(pccora_identification.build(ident))
	rootgrp.start_datetime = ident['datetime']

	

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
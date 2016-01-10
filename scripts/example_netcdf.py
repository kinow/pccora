#!/usr/bin/env python3

# pip3 install netCDF4
import netCDF4
import numpy as np

def main():

	file = '/home/kinow/Downloads/aber-o3lidar_chilbolton_2005060717_v05.nc'

	f = netCDF4.Dataset(file)
	print("## Variables")
	print([k for k in f.variables.keys()])

	print("## Whole File")
	print(f)

if __name__ == '__main__':
	main()
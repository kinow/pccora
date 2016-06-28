#!/usr/bin/env python3
# Requires: numpy, netCDF4

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *
from construct import *

from netCDF4 import Dataset
import numpy as np

def parseandconvert(input, output):
	pccora_parser = PCCORAParser()
	pccora_parser.parse_file(input)

	# Data
	head = pccora_parser.get_header()
	ident = pccora_parser.get_identification()
	#syspar = pccora_parser.get_syspar()
	data = pccora_parser.get_data()
	hires_data = pccora_parser.get_hires_data()

	# Call function to print CSV
	convert2netcdf4(
		data=dict(head=head, ident=ident, data=data, hires_data=hires_data), 
		file=output)

def convert2netcdf4(data, file):
	"""Convert a file in the Vaisala old binary format, into a netCDF file.

	Keyword arguments:
	data -- the data dictionary from a parsed radiosonde data file
	file -- the dataset output file
	"""
	head = data['head']
	ident = data['ident']

	#data_data = data['data']
	hires_data = data['hires_data']

	dataset = Dataset(file, "w", format="NETCDF4")

	# Dimensions
	dataset.createDimension("time")

	# Attributes
	dataset.category = "Radiosonde"
	dataset.instrument = "Vaisala"
	# TODO: or should we use launch_time?
	dataset.start_datetime = str(ident['datetime'])

	azimuth_angle = []
	dew_point = []
	height = []
	latitude = []
	longitude = []
	mixing_ratio = []
	pressure = []
	altitude = []
	relative_humidity = []
	temperature = []
	time = []
	east_wind = []
	north_wind = []
	wind_direction = []
	wind_speed = []

	# Variables
	for container in hires_data:
		azimuth_angle.append(container['azimuth'])
		dew_point.append(container['dew_point_temperature'])
		height.append(container['radar_height'])
		latitude.append(container['latitude'])
		longitude.append(container['longitude'])
		mixing_ratio.append(container['mixing_ratio'])
		pressure.append(container['pressure'])
		altitude.append(container['altitude'])
		relative_humidity.append(container['humidity'])
		temperature.append(container['temperature'])
		time.append(container['time'])
		east_wind.append(container['east_wind'])
		north_wind.append(container['north_wind'])
		wind_direction.append(container['wind_direction'])
		wind_speed.append(container['wind_speed'])

	# azimuth
	azimuth_angle_variable = dataset.createVariable('azimuth', 'f4', ("time", ))
	azimuth_angle_variable.standard_name = 'azimuth_angle'
	azimuth_angle_variable.units = 'degree'
	azimuth_angle_variable.long_name = 'Azimuth Angle'
	azimuth_angle_variable.g_format_type = 'FLT'
	azimuth_angle_variable.g_format_nan = -32768
	azimuth_angle_variable[:] = azimuth_angle

	# dew_point
	dew_point_variable = dataset.createVariable('FP', 'f4', ("time", ))
	dew_point_variable.units = 'K'
	dew_point_variable.long_name = 'Frostpoint'
	dew_point_variable.g_format_type = 'FLT'
	dew_point_variable.g_format_nan = -32768
	dew_point_variable.coordinates = "lon lat alt"
	dew_point_variable[:] = dew_point

	# height
	height_variable = dataset.createVariable('height', 'f4', ("time", ))
	height_variable.standard_name = 'radar_height'
	height_variable.units = 'm'
	height_variable.long_name = 'Radar height'
	height_variable.g_format_type = 'FLT'
	height_variable.g_format_nan = -32768
	height_variable[:] = height

	# latitude
	latitude_variable = dataset.createVariable('lat', 'f4', ("time", ))
	latitude_variable.standard_name = 'latitude'
	latitude_variable.units = 'degree_north'
	latitude_variable.long_name = 'Latitude'
	latitude_variable.g_format_type = 'FLT'
	latitude_variable.g_format_nan = -32768
	latitude_variable[:] = latitude

	# longitude
	longitude_variable = dataset.createVariable('long', 'f4', ("time", ))
	longitude_variable.standard_name = 'longitude'
	longitude_variable.units = 'degree_east'
	longitude_variable.long_name = 'Longitude'
	longitude_variable.g_format_type = 'FLT'
	longitude_variable.g_format_nan = -32768
	longitude_variable[:] = longitude

	# mixing_ratio
	mixing_ratio_variable = dataset.createVariable('WVMR', 'f4', ("time", ))
	mixing_ratio_variable.standard_name = 'Water_vapor_mixing_ratio'
	mixing_ratio_variable.units = '1'
	mixing_ratio_variable.long_name = 'Water Vapor Volume Mixing Ratio'
	mixing_ratio_variable.g_format_type = 'FLT'
	mixing_ratio_variable.g_format_nan = -32768
	mixing_ratio_variable[:] = mixing_ratio

	# pressure
	pressure_variable = dataset.createVariable('press', 'f4', ("time", ))
	pressure_variable.standard_name = 'air_pressure'
	pressure_variable.units = 'hPa'
	pressure_variable.long_name = 'Pressure'
	pressure_variable.g_format_type = 'FLT'
	pressure_variable.g_format_nan = -32768
	pressure_variable.coordinates = "lon lat alt"
	pressure_variable[:] = pressure

	# altitude
	altitude_variable = dataset.createVariable('alt', 'f4', ("time", ))
	altitude_variable.standard_name = 'altitude'
	altitude_variable.units = 'm'
	altitude_variable.long_name = 'Altitude'
	altitude_variable.g_format_type = 'FLT'
	altitude_variable.g_format_nan = -32768
	altitude_variable.positive = "up"
	altitude_variable[:] = altitude

	# relative_humidity
	relative_humidity_variable = dataset.createVariable('rel_humidity', 'f4', ("time", ))
	relative_humidity_variable.standard_name = 'relative_humidity'
	relative_humidity_variable.units = '1'
	relative_humidity_variable.long_name = 'Relative Humidity'
	relative_humidity_variable.g_format_type = 'FLT'
	relative_humidity_variable.g_format_nan = -32768
	relative_humidity_variable.coordinates = "lon lat alt"
	relative_humidity_variable[:] = relative_humidity

	# temperature
	temperature_variable = dataset.createVariable('temp', 'f4', ("time", ))
	temperature_variable.standard_name = 'air_temperature'
	temperature_variable.units = 'K'
	temperature_variable.long_name = 'Temperature'
	temperature_variable.g_format_type = 'FLT'
	temperature_variable.g_format_nan = -32768
	temperature_variable.coordinates = "lon lat alt"
	temperature_variable[:] = temperature

	# time
	time_variable = dataset.createVariable('time', 'f4', ("time", ))
	time_variable.standard_name = 'time'
	time_variable.units = 'seconds since ?'
	time_variable.long_name = 'Time'
	time_variable.g_format_type = 'FLT'
	time_variable.g_format_nan = -32768
	time_variable.axis = "T"
	time_variable.calendar = "gregorian"
	time_variable[:] = time

	# east_wind
	east_wind_variable = dataset.createVariable('u', 'f4', ("time", ))
	east_wind_variable.standard_name = 'eastward_wind'
	east_wind_variable.units = 'm s-1'
	east_wind_variable.long_name = 'Zonal Wind'
	east_wind_variable.g_format_type = 'FLT'
	east_wind_variable.g_format_nan = -32768
	east_wind_variable.comment = "Wind towards the east"
	east_wind_variable.coordinates = "lon lat alt"
	east_wind_variable[:] = east_wind

	# north_wind
	north_wind_variable = dataset.createVariable('v', 'f4', ("time", ))
	north_wind_variable.standard_name = 'northward_wind'
	north_wind_variable.units = 'm s-1'
	north_wind_variable.long_name = 'Meridional Wind'
	north_wind_variable.g_format_type = 'FLT'
	north_wind_variable.g_format_nan = -32768
	north_wind_variable.comment = "Wind towards the north"
	north_wind_variable.coordinates = "lon lat alt"
	north_wind_variable[:] = north_wind

	# wind_direction
	wind_direction_variable = dataset.createVariable('wdir', 'f4', ("time", ))
	wind_direction_variable.standard_name = 'wind_from_direction'
	wind_direction_variable.units = 'degree'
	wind_direction_variable.long_name = 'Wind Direction'
	wind_direction_variable.g_format_type = 'FLT'
	wind_direction_variable.g_format_nan = -32768
	wind_direction_variable.coordinates = "lon lat alt"
	wind_direction_variable.comment = "Wind direction"
	wind_direction_variable[:] = wind_direction

	# wind_speed
	wind_speed_variable = dataset.createVariable('wspeed', 'f4', ("time", ))
	wind_speed_variable.standard_name = 'wind_speed'
	wind_speed_variable.units = 'm s-1'
	wind_speed_variable.long_name = 'Wind Speed'
	wind_speed_variable.g_format_type = 'FLT'
	wind_speed_variable.g_format_nan = -32768
	wind_speed_variable.coordinates = "lon lat alt"
	wind_speed_variable.comment = "Wind speed"
	wind_speed_variable[:] = wind_speed

	dataset.close()

def main():
	file = '/home/kinow/Downloads/96010109.EDT'
	output = '/home/kinow/Downloads/96010109-nohead-noident-hires.nc'

	parseandconvert(file, output)

if __name__ == '__main__':
	main()

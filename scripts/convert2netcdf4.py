#!/usr/bin/env python3
# Requires: numpy, netCDF4

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *
from construct import *

from netCDF4 import Dataset
import numpy as np

def convert2netcdf4(data, options, file):
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
	elevation_angle = []
	height = []
	latitude = []
	longitude = []
	mixing_ratio = []
	pressure = []
	_range = []
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
		# FIXME: which one is elevation angle?
		elevation_angle.append(None)
		height.append(container['radar_height'])
		latitude.append(container['latitude'])
		longitude.append(container['longitude'])
		mixing_ratio.append(container['mixing_ratio'])
		pressure.append(container['pressure'])
		# FIXME: is that right? altitude for range?
		_range.append(container['altitude'])
		relative_humidity.append(container['humidity'])
		temperature.append(container['temperature'])
		time.append(container['time'])
		east_wind.append(container['east_wind'])
		north_wind.append(container['north_wind'])
		wind_direction.append(container['wind_direction'])
		wind_speed.append(container['wind_speed'])

	# azimuth
	azimuth_angle_variable = dataset.createVariable('azimuth_angle', 'f4', ("time", ))
	azimuth_angle_variable.units = 'degree'
	azimuth_angle_variable.missing_value = -32768
	azimuth_angle_variable.parameter = 'azimuth_angle'
	azimuth_angle_variable[:] = azimuth_angle

	# dew_point
	dew_point_variable = dataset.createVariable('dew_point', 'f4', ("time", ))
	dew_point_variable.units = 'degC'
	dew_point_variable.missing_value = -32768
	dew_point_variable.parameter = 'dew_point_temperature'
	dew_point_variable[:] = dew_point

	# elevation_angle
	elevation_angle_variable = dataset.createVariable('elevation_angle', 'f4', ("time", ))
	elevation_angle_variable.units = 'degree'
	elevation_angle_variable.missing_value = -32768
	elevation_angle_variable.parameter = 'elevation_angle'
	elevation_angle_variable[:] = elevation_angle

	# height
	height_variable = dataset.createVariable('height', 'f4', ("time", ))
	height_variable.units = 'metre'
	height_variable.missing_value = -32768
	height_variable.parameter = 'height'
	height_variable[:] = height

	# latitude
	latitude_variable = dataset.createVariable('latitude', 'f4', ("time", ))
	latitude_variable.units = 'degree'
	latitude_variable.missing_value = -32768
	latitude_variable.parameter = 'latitude'
	latitude_variable[:] = latitude

	# longitude
	longitude_variable = dataset.createVariable('longitude', 'f4', ("time", ))
	longitude_variable.units = 'degree'
	longitude_variable.missing_value = -32768
	longitude_variable.parameter = 'longitude'
	longitude_variable[:] = longitude

	# mixing_ratio
	mixing_ratio_variable = dataset.createVariable('mixing_ratio', 'f4', ("time", ))
	mixing_ratio_variable.units = 'g/kg'
	mixing_ratio_variable.missing_value = -32768
	mixing_ratio_variable.parameter = 'humidity_mixing_ratio'
	mixing_ratio_variable[:] = mixing_ratio

	# pressure
	pressure_variable = dataset.createVariable('pressure', 'f4', ("time", ))
	pressure_variable.units = 'Pascal'
	pressure_variable.missing_value = -32768
	pressure_variable.parameter = 'air_pressure'
	pressure_variable[:] = pressure

	# range
	range_variable = dataset.createVariable('range', 'f4', ("time", ))
	range_variable.units = 'metre'
	range_variable.missing_value = -32768
	range_variable.parameter = 'range'
	range_variable[:] = _range

	# relative_humidity
	relative_humidity_variable = dataset.createVariable('rel_humidity', 'f4', ("time", ))
	relative_humidity_variable.units = 'percent'
	relative_humidity_variable.missing_value = -32768
	relative_humidity_variable.parameter = 'relative_humidity'
	relative_humidity_variable[:] = relative_humidity

	# temperature
	temperature_variable = dataset.createVariable('temperature', 'f4', ("time", ))
	temperature_variable.units = 'degC'
	temperature_variable.missing_value = -32768
	temperature_variable.parameter = 'air_temperature'
	temperature_variable[:] = temperature

	# time
	time_variable = dataset.createVariable('time', 'f4', ("time", ))
	time_variable.units = 'second'
	time_variable.missing_value = -32768
	time_variable.parameter = 'time'
	time_variable[:] = time

	# east_wind
	east_wind_variable = dataset.createVariable('u_component', 'f4', ("time", ))
	east_wind_variable.units = 'metre second**-1'
	east_wind_variable.missing_value = -32768
	east_wind_variable.parameter = 'eastward_wind'
	east_wind_variable[:] = east_wind

	# north_wind
	north_wind_variable = dataset.createVariable('v_component', 'f4', ("time", ))
	north_wind_variable.units = 'metre second**-1'
	north_wind_variable.missing_value = -32768
	north_wind_variable.parameter = 'northward_wind'
	north_wind_variable[:] = north_wind

	# wind_direction
	wind_direction_variable = dataset.createVariable('wind_direction', 'f4', ("time", ))
	wind_direction_variable.units = 'degree'
	wind_direction_variable.missing_value = -32768
	wind_direction_variable.parameter = 'wind_from_direction'
	wind_direction_variable[:] = wind_direction

	# wind_speed
	wind_speed_variable = dataset.createVariable('wind_speed', 'f4', ("time", ))
	wind_speed_variable.units = 'metre second**-1'
	wind_speed_variable.missing_value = -32768
	wind_speed_variable.parameter = 'wind_speed'
	wind_speed_variable[:] = wind_speed

	dataset.close()

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
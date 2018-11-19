#!/usr/bin/env python3
# Requires: numpy, netCDF4
# @see https://www.mi.uni-hamburg.de/en/arbeitsgruppen/strahlung-und-fernerkundung/intern/datadocs/gruan.html

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

def parseandconvert_add_day(input, output):
	pccora_parser = PCCORAParser()
	pccora_parser.parse_file(input)

	# Data
	head = pccora_parser.get_header()
	ident = pccora_parser.get_identification()
	#syspar = pccora_parser.get_syspar()
	data = pccora_parser.get_data()
	hires_data = pccora_parser.get_hires_data()

	output = output.replace('DD', str(ident['day']))

	# Call function to print CSV
	convert2netcdf4(
		data=dict(head=head, ident=ident, data=data, hires_data=hires_data), 
		file=output)

def convert2netcdf4(data, file):
	"""Convert a file in the Vaisala old binary format, into a netCDF file,
	creating a file following the GRUAN data format standard.

	Keyword arguments:
	data -- the data dictionary from a parsed radiosonde data file
	file -- the dataset output file
	"""
	head = data['head']
	ident = data['ident']

	#data_data = data['data']
	hires_data = data['hires_data']

	dataset = Dataset(file, "w", format="NETCDF4_CLASSIC")

	# Dimensions
	dataset.createDimension("time")

	dataset.setncattr('g.General.SiteWmoId', ident['wmo_block_number'] + ident['wmo_station_number'])
	dataset.setncattr('g.MeasuringSystem.Longitude', str('N/A' if None == ident['station_longitude'] else ident['station_longitude']) + ' degree east')
	dataset.setncattr('g.MeasuringSystem.Latitude', str(ident['station_latitude']) + ' degree north')
	dataset.setncattr('g.MeasuringSystem.Altitude', str(ident['station_altitude']) + ' m')
	dataset.setncattr('g.SurfaceObs.Pressure', str(ident['surface_pressure']) + ' hPa')
	dataset.setncattr('g.SurfaceObs.Temperature', str(ident['surface_temperature']) + ' °C')
	dataset.setncattr('g.SurfaceObs.RelativeHumidity', str(ident['surface_humidity']) + ' %')
	dataset.setncattr('g.General.SiteCode', "INVRCRGL")
	dataset.setncattr('g.General.SiteName', "Invercargill")
	dataset.setncattr('g.General.SiteInstitution', "MetService New Zealand")
	dataset.setncattr('g.Product.Producer', "National Institute of Water and Atmospheric Research (New Zealand)")
	dataset.setncattr('g.Product.References', "https://github.com/kinow/pccora")

	dataset.station_type = ident['station_type']
	dataset.region_number = ident['region_number']
	dataset.wmo_block_number = ident['wmo_block_number']
	dataset.wmo_station_number = ident['wmo_station_number']
	dataset.wind_speed_unit = str(ident['wind_speed_unit']) + ', comment: 0 = m/s 1 = knots'
	dataset.telecommunications_headings = str(ident['telecommunications_headings']) + ', comment: 0 = No 1 = Yes'
	dataset.res = ident['reserved']
	dataset.sounding_type = str(ident['sounding_type']) + ', comment: 0 = PTU 1 = Only pressure 2 = No PTU (Radar'
	dataset.start_mode = str(ident['start_mode']) + ', comment: 0 = Auto 1 = Manual'
	dataset.time_elapsed = ident['time_elapsed']
	dataset.ptu_rate = ident['ptu_rate']
	dataset.spu_serial_number = ident['spu_serial_number']
	dataset.year = ident['year']
	dataset.month = ident['month']
	dataset.day = ident['day']
	dataset.julian_date = ident['julian_date']
	dataset.hour = ident['hour']
	dataset.minute = ident['minute']
	dataset.message_year = ident['message_year']
	dataset.message_month = ident['message_month']
	dataset.message_day = ident['message_day']
	dataset.message_hour = ident['message_hour']
	dataset.cloud_group = ident['cloud_group']
	dataset.weather_group = ident['weather_group']
	dataset.napp = ident['napp']
	dataset.humidity_correction = ident['humidity_correction']
	dataset.success_of_signal = ident['success_of_signal']
	dataset.pressure_accept_level = ident['pressure_accept_level']
	dataset.pressure_replace_level = ident['pressure_replace_level']
	dataset.pressure_reject_level = ident['pressure_reject_level']
	dataset.temperature_accept_level = ident['temperature_accept_level']
	dataset.temperature_replace_level = ident['temperature_replace_level']
	dataset.temperature_reject_level = ident['temperature_reject_level']
	dataset.humidity_accept_level = ident['humidity_accept_level']
	dataset.humidity_replace_level = ident['humidity_replace_level']
	dataset.humidity_reject_level = ident['humidity_reject_level']
	dataset.total_omega_count = ident['total_omega_count']
	dataset.reason_termination = ident['reason_termination']
	dataset.omega_count = ident['omega_count']
	dataset.wind_computing_mode = str(ident['wind_computing_mode']) + ', comment: 0 = Remote 1 = Local 2 = Differential'
	dataset.wind_mode = str(ident['wind_mode']) + ', comment: 0 = Omega 1 = Loran-C 2 = Radar 255 = Only PTU'
	dataset.stations_used = str(ident['stations_used']) + ', comment: One bit for each station 1 = Used 0 = Not used'
	dataset.loranc_chains_used = ident['loranc_chains_used']
	dataset.gri_chain_1 = ident['gri_chain_1']
	dataset.gri_chain_2 = ident['gri_chain_2']
	dataset.exclude_loran_transmitters = str(ident['exclude_loran_transmitters']) + ', comment: One bit for each in the chain; and chain 2 transmitted'
	dataset.phase_integration_time = str(ident['phase_integration_time']) + ', comment: 0 = time (s) 1 = Altitude (m/MSI'
	dataset.phase_integration_time_1 = ident['phase_integration_time_1']
	dataset.phase_integration_time_2 = ident['phase_integration_time_2']
	dataset.phase_integration_time_3 = ident['phase_integration_time_3']
	dataset.phase_integration_time_4 = ident['phase_integration_time_4']
	dataset.phase_integration_time_5 = ident['phase_integration_time_5']
	dataset.phase_integration_time_6 = ident['phase_integration_time_6']
	dataset.phase_integration_change_level_1 = ident['phase_integration_change_level_1']
	dataset.phase_integration_change_level_2 = ident['phase_integration_change_level_2']
	dataset.phase_integration_change_level_3 = ident['phase_integration_change_level_3']
	dataset.phase_integration_change_level_4 = ident['phase_integration_change_level_4']
	dataset.phase_integration_change_level_5 = ident['phase_integration_change_level_5']
	dataset.phase_integration_change_level_6 = ident['phase_integration_change_level_6']
	dataset.reference_pressure = str(ident['reference_pressure']) + ' hPa'
	dataset.reference_temperature = str(ident['reference_temperature']) + ' °C'
	dataset.reference_humidity = str(ident['reference_humidity']) + ' %'

	dataset.institution = "MetService New Zealand"
	dataset.datetime = str(ident['datetime'])
	dataset.comment = 'For more information about the variables see: https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html'

	elapsed_time = []
	logarithmic_pressure = []
	temperature = []
	relative_humidity = []
	north_wind = []
	east_wind = []
	altitude = []
	pressure = []
	dew_point = []
	mixing_ratio = []
	wind_direction = []
	wind_speed = []
	azimuth_angle = []
	horizontal_distance = []
	longitude = []
	latitude = []
	significance_key = []
	recalculated_significance_key = []
	radar_height = []

	# Variables
	for container in hires_data:
		elapsed_time.append(container['time'])
		logarithmic_pressure.append(container['logarithmic_pressure'])
		temperature.append(container['temperature'])
		relative_humidity.append(container['humidity'])
		north_wind.append(container['north_wind'])
		east_wind.append(container['east_wind'])
		altitude.append(container['altitude'])
		pressure.append(container['pressure'])
		dew_point.append(container['dew_point_temperature'])
		mixing_ratio.append(container['mixing_ratio'])
		wind_direction.append(container['wind_direction'])
		wind_speed.append(container['wind_speed'])
		azimuth_angle.append(container['azimuth'])
		horizontal_distance.append(container['horizontal_distance'])
		longitude.append(container['longitude'])
		latitude.append(container['latitude'])
		sigkey = ''.join(container['significance_key'])
		sigkey = sigkey.replace('0b', '')
		significance_key.append(sigkey)
		rsigkey = ''.join(container['recalculated_significance_key'])
		rsigkey = sigkey.replace('0b', '')
		recalculated_significance_key.append(rsigkey)
		radar_height.append(container['radar_height'])

	# elapsed_time
	elapsed_time_variable = dataset.createVariable('time', 'f4', ("time", ), zlib=True, fill_value=-32768)
	elapsed_time_variable.standard_name = 'time'
	elapsed_time_variable.units = 's'
	elapsed_time_variable.long_name = 'Seconds since sonde release'
	elapsed_time_variable.g_format_type = 'FLT'
	elapsed_time_variable[:] = elapsed_time

	# logarithmic_pressure
	logarithmic_pressure_variable = dataset.createVariable('logarithmic_pressure', 'f4', ("time", ), zlib=True, fill_value=-32768)
	logarithmic_pressure_variable.standard_name = 'logarithmic_pressure'
	logarithmic_pressure_variable.units = '4096*ln(P)hPa'
	logarithmic_pressure_variable.long_name = 'Scaled logarithmic pressure'
	logarithmic_pressure_variable.g_format_type = 'FLT'
	logarithmic_pressure_variable[:] = logarithmic_pressure

	# temperature
	temperature_variable = dataset.createVariable('temp', 'f4', ("time", ), zlib=True, fill_value=-32768)
	temperature_variable.standard_name = 'air_temperature'
	temperature_variable.units = 'K'
	temperature_variable.long_name = 'Temperature'
	temperature_variable.g_format_type = 'FLT'
	temperature_variable.coordinates = "lon lat alt"
	temperature_variable[:] = temperature

	# relative_humidity
	relative_humidity_variable = dataset.createVariable('rh', 'f4', ("time", ), zlib=True, fill_value=-32768)
	relative_humidity_variable.standard_name = 'relative_humidity'
	relative_humidity_variable.units = '1'
	relative_humidity_variable.long_name = 'Relative Humidity'
	relative_humidity_variable.g_format_type = 'FLT'
	relative_humidity_variable.coordinates = "lon lat alt"
	relative_humidity_variable[:] = relative_humidity

	# north_wind
	north_wind_variable = dataset.createVariable('v', 'f4', ("time", ), zlib=True, fill_value=-32768)
	north_wind_variable.standard_name = 'northward_wind'
	north_wind_variable.units = 'm s-1'
	north_wind_variable.long_name = 'Meridional Wind'
	north_wind_variable.g_format_type = 'FLT'
	north_wind_variable.comment = "Wind towards the north"
	north_wind_variable.coordinates = "lon lat alt"
	north_wind_variable[:] = north_wind

	# east_wind
	east_wind_variable = dataset.createVariable('u', 'f4', ("time", ), zlib=True, fill_value=-32768)
	east_wind_variable.standard_name = 'eastward_wind'
	east_wind_variable.units = 'm s-1'
	east_wind_variable.long_name = 'Zonal Wind'
	east_wind_variable.g_format_type = 'FLT'
	east_wind_variable.comment = "Wind towards the east"
	east_wind_variable.coordinates = "lon lat alt"
	east_wind_variable[:] = east_wind

	# altitude
	altitude_variable = dataset.createVariable('alt', 'f4', ("time", ), zlib=True, fill_value=-32768)
	altitude_variable.standard_name = 'altitude'
	altitude_variable.units = 'm'
	altitude_variable.long_name = 'Altitude'
	altitude_variable.g_format_type = 'FLT'
	altitude_variable.positive = "up"
	altitude_variable[:] = altitude

	# pressure
	pressure_variable = dataset.createVariable('press', 'f4', ("time", ), zlib=True, fill_value=-32768)
	pressure_variable.standard_name = 'air_pressure'
	pressure_variable.units = 'hPa'
	pressure_variable.long_name = 'Pressure'
	pressure_variable.g_format_type = 'FLT'
	pressure_variable.coordinates = "lon lat alt"
	pressure_variable[:] = pressure

	# dew_point
	dew_point_variable = dataset.createVariable('FP', 'f4', ("time", ), zlib=True, fill_value=-32768)
	dew_point_variable.units = 'K'
	dew_point_variable.long_name = 'Frostpoint'
	dew_point_variable.g_format_type = 'FLT'
	dew_point_variable.coordinates = "lon lat alt"
	dew_point_variable[:] = dew_point

	# mixing_ratio
	mixing_ratio_variable = dataset.createVariable('WVMR', 'f4', ("time", ), zlib=True, fill_value=-32768)
	mixing_ratio_variable.standard_name = 'Water_vapor_mixing_ratio'
	mixing_ratio_variable.units = '0.1 g/Kg'
	mixing_ratio_variable.long_name = 'Water Vapor Volume Mixing Ratio'
	mixing_ratio_variable.g_format_type = 'FLT'
	mixing_ratio_variable[:] = mixing_ratio

	# wind_direction
	wind_direction_variable = dataset.createVariable('wdir', 'f4', ("time", ), zlib=True, fill_value=-32768)
	wind_direction_variable.standard_name = 'wind_from_direction'
	wind_direction_variable.units = 'degree'
	wind_direction_variable.long_name = 'Wind Direction'
	wind_direction_variable.g_format_type = 'FLT'
	wind_direction_variable.coordinates = "lon lat alt"
	wind_direction_variable.comment = "Wind direction"
	wind_direction_variable[:] = wind_direction

	# wind_speed
	wind_speed_variable = dataset.createVariable('wspeed', 'f4', ("time", ), zlib=True, fill_value=-32768)
	wind_speed_variable.standard_name = 'wind_speed'
	wind_speed_variable.units = 'm s-1'
	wind_speed_variable.long_name = 'Wind Speed'
	wind_speed_variable.g_format_type = 'FLT'
	wind_speed_variable.coordinates = "lon lat alt"
	wind_speed_variable.comment = "Wind speed"
	wind_speed_variable[:] = wind_speed

	# azimuth
	azimuth_angle_variable = dataset.createVariable('azimuth', 'f4', ("time", ), zlib=True, fill_value=-32768)
	azimuth_angle_variable.standard_name = 'azimuth_angle'
	azimuth_angle_variable.units = 'degree'
	azimuth_angle_variable.long_name = 'Azimuth angle to the sonde'
	azimuth_angle_variable.g_format_type = 'FLT'
	azimuth_angle_variable[:] = azimuth_angle

	# horizontal_distance
	horizontal_distance_variable = dataset.createVariable('horizontal_distance', 'f4', ("time", ), zlib=True, fill_value=-32768)
	horizontal_distance_variable.standard_name = 'horizontal_distance'
	horizontal_distance_variable.units = '100m'
	horizontal_distance_variable.long_name = 'Horizontal distance to the sonde'
	horizontal_distance_variable.g_format_type = 'FLT'
	horizontal_distance_variable[:] = horizontal_distance

	# longitude
	longitude_variable = dataset.createVariable('lon', 'f4', ("time", ), zlib=True, fill_value=-32768)
	longitude_variable.standard_name = 'longitude'
	longitude_variable.units = 'degree_east'
	longitude_variable.long_name = 'Longitude'
	longitude_variable.g_format_type = 'FLT'
	longitude_variable[:] = longitude

	# latitude
	latitude_variable = dataset.createVariable('lat', 'f4', ("time", ), zlib=True, fill_value=-32768)
	latitude_variable.standard_name = 'latitude'
	latitude_variable.units = 'degree_north'
	latitude_variable.long_name = 'Latitude'
	latitude_variable.g_format_type = 'FLT'
	latitude_variable[:] = latitude

	# significance_key
	significance_key_variable = dataset.createVariable('significance_key', 'i1', ("time", ), zlib=True, fill_value=-32768)
	significance_key_variable.standard_name = 'significance_key'
	significance_key_variable.units = 'bit_pattern'
	significance_key_variable.long_name = 'SOND calculated significance key'
	significance_key_variable.comment = 'See LEVEL TYPE FLAG in https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html'
	significance_key_variable.g_format_type = 'CHR'
	significance_key_variable[:] = significance_key

	# significance_key
	recalculated_significance_key_variable = dataset.createVariable('recalculated_significance_key', 'f4', ("time", ), zlib=True, fill_value=-32768)
	recalculated_significance_key_variable.standard_name = 'recalculated_significance_key'
	recalculated_significance_key_variable.units = 'bit_pattern'
	recalculated_significance_key_variable.long_name = 'User edited/recalculated significance key'
	recalculated_significance_key_variable.comment = 'See LEVEL TYPE FLAG in https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html'
	recalculated_significance_key_variable.g_format_type = 'FLT'
	recalculated_significance_key_variable[:] = recalculated_significance_key

	# radar_height
	radar_height_variable = dataset.createVariable('radar_height', 'f4', ("time", ), zlib=True, fill_value=-32768)
	radar_height_variable.standard_name = 'radar_height'
	radar_height_variable.units = 'm'
	radar_height_variable.long_name = 'Radar height'
	radar_height_variable.comment = '30000m subtracted'
	radar_height_variable.g_format_type = 'FLT'
	radar_height_variable[:] = radar_height	

	dataset.close()

def main():
	file = '/home/kinow/Downloads/96010109.EDT'
	output = '/home/kinow/Downloads/96010109-nohead-noident-hires.nc'

	parseandconvert(file, output)

if __name__ == '__main__':
	main()

#!/usr/bin/env python3

"""
Outputs the same as MetGraph.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pccora'))
from pccora import *

from jinja2 import Environment

def print_template(file, head, ident):
	with(open(os.path.join(os.path.dirname(__file__), 'metgraph.j2'), 'r')) as template_file:
		template = Environment().from_string(template_file.read())

		ident_datetime = ident.datetime
		started_at = ident_datetime.strftime("%-d %B %Y  %-H:%-M")

		sounding_type = None
		if ident['sounding_type'] == 0:
			sounding_type = 'PTU'
		elif ident['sounding_type'] == 1:
			sounding_type = 'Pressure'
		elif ident['sounding_type'] == 2:
			sounding_type = 'Radar'

		latitude = "{} N".format(ident['station_latitude']) if ident['station_latitude'] >= 0 else "{} S".format(ident['station_latitude'])
		longitude = "{} E".format(ident['station_longitude']) if ident['station_longitude'] >= 0 else "{} W".format(ident['station_longitude'])

		ident_pressure = " %6s %6s %6s" % (
			round(ident['reference_pressure'], 1), 
			round(ident['reference_pressure'] - ident['pressure_correction'], 1),
			ident['pressure_correction']
		)

		ident_temperature = " %6s %6s %6s" % (
			round(ident['reference_temperature'], 1), 
			round(ident['reference_temperature'] - ident['temperature_correction'], 1),
			ident['temperature_correction']
		)

		ident_humidity = " %6s %6s %6s" % (
			round(ident['reference_humidity'], 1), 
			round(ident['reference_humidity'] - ident['humidity_correction'], 1),
			ident['humidity_correction']
		)

		s = template.render(
			file_location=file,
			started_at=started_at,
			station_id=ident['wmo_station_number'],
			station_altitude=ident['station_altitude'],
			sounding_type=sounding_type,
			rs_number=ident['radiosonde_number'].decode().strip(),
			serial_number=ident['spu_serial_number'],
			latitude=latitude,
			longitude=longitude,
			ident_pressure=ident_pressure,
			ident_temperature=ident_temperature,
			ident_humidity=ident_humidity,
			clouds=ident['cloud_group'].decode().strip(),
			special1=ident['weather_group'].decode().strip(),
			special2=ident['napp'].decode().strip(),
			success_of_signal=ident['success_of_signal']
		)
		print(s)

def main():
	file = '/home/kinow/Downloads/96010109.EDT'

	pccora_parser = PCCORAParser()
	pccora_parser.parse_file(file)
	head = pccora_parser.get_header()
	ident = pccora_parser.get_identification()
	syspar = pccora_parser.get_syspar()
	data = pccora_parser.get_data()
	hires_data = pccora_parser.get_hires_data()

	print_template(file, head, ident)

if __name__ == '__main__':
	main()
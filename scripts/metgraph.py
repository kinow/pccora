#!/usr/bin/env python3

"""
Outputs the same as MetGraph.
"""

import os

from jinja2 import Environment

from pccora import *


def print_template(file, ident, hires_data):
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

        latitude = "{} N".format(ident['station_latitude']) if ident['station_latitude'] >= 0 else "{} S".format(
            ident['station_latitude'])
        longitude = "{} E".format(ident['station_longitude']) if ident['station_longitude'] >= 0 else "{} W".format(
            ident['station_longitude'])

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

        entries = list()

        for container in hires_data:
            time = container['time']

            minute = (int(time / 60.0))
            second = (int(time % 60))
            pressure = round(float(container['spress']), 1)
            gpm = container['altitude']
            temperature = container['temperature'] - 273.15
            temperature = round(temperature - (temperature % 0.1), 1)
            rh = container['humidity']
            dew_point_temperature = container['dew_point_temperature'] - 273.15
            dew_point_temperature = round(dew_point_temperature - (dew_point_temperature % 0.1), 1)

            significance = ''
            recalculated_significance = ''
            # recalculated_significance = '' if container['significance_key'] == \
            #     container['recalculated_significance_key'] else '<>'

            entry = "  %2d %2d %8s %8d %9s %6d %6s %13s %12s" % (
                minute,
                second,
                pressure,
                int(gpm),
                str(temperature),
                rh,
                str(dew_point_temperature),
                significance,
                recalculated_significance
            )
            entries.append(entry)

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
            success_of_signal=ident['success_of_signal'],
            reason_termination=ident['reason_termination'],
            entries=entries
        )
        print(s)


def main():
    file = '/home/kinow/Downloads/96010109.EDT'

    pccora_parser = PCCORAParser()
    pccora_parser.parse_file(file)
    # head = pccora_parser.get_header()
    ident = pccora_parser.get_identification()
    # syspar = pccora_parser.get_syspar()
    # data = pccora_parser.get_data()
    hires_data = pccora_parser.get_hires_data()

    print_template(file, ident, hires_data)


if __name__ == '__main__':
    main()

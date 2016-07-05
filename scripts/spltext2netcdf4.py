
import sys
import re
from pprint import pprint, pformat
from datetime import datetime, timedelta
import pytz
import logging
from collections import namedtuple
from netCDF4 import Dataset
import numpy as np

FORMAT = '%(asctime)s %(message)s'
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

UTC = pytz.timezone('UTC')

# Regular expressions for the parser
PILOT_REGEX = '^([0-9]+)\s*([a-z0-9\s]+)\s+pilot\s+for\s+(.*)$'
PILOT_PATTERN = re.compile(PILOT_REGEX, flags=re.IGNORECASE)

STARTED_AT_REGEX = '^started\s*at\s*(.*)$'

# Settings for the parsers
DEFAULT_INTERVAL_THRESHOLD_HOURS = 4 # hours threshold to match a given time with a time in the day (0 or 12)
DEFAULT_INTERVAL = timedelta(hours=DEFAULT_INTERVAL_THRESHOLD_HOURS)

# http://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
def is_int(s):
    """Check if a given value can be parsed as Int""" 
    try: 
        int(s)
        return True
    except ValueError:
        return False

def parse_wind_file(wind_file):
    """
    Parse a file containing readings with historical wind speed and wind direction. A poor
    man's simple state machine, with just two states.
    """
    dates = dict()
    with open(wind_file, 'r') as wf:
        
        in_pilot = False
        d = None

        for line in wf:
            
            m = PILOT_PATTERN.match(line)
            if m:
                if in_pilot:
                    logging.error("Ops. Found a PILOT message before finding the values")
                    raise Exception("Ops. Found a PILOT message before finding the values"  )
                station_id = m.group(1)
                site_name  = m.group(2).strip()
                date       = m.group(3) # 27-Mar-1995 00:00Z

                d = datetime.strptime(date[:-1], '%d-%b-%Y %H:%M')
                #d = d.replace(tzinfo=UTC)
                dates[d] = {
                    'station_id': station_id,
                    'site_name': site_name,
                    'date': date,
                    'press_readings': dict(),
                    'height_readings': dict()
                }

                in_pilot = True

            elif in_pilot:
                
                if line.count('|') == 4 and line.count('hPa') == 0:

                    columns = line.split('|')
                    std_levels_col = columns[0].replace('/', ' ').split()

                    if len(std_levels_col) > 0:
                        hpa = std_levels_col[0]
                        if is_int(hpa):
                            hpa = str(float(hpa)) # to match the key in the dict... due to different units in the two files
                            if not hpa in dates[d]['press_readings']:
                                dates[d]['press_readings'][hpa] = dict()
                            if len(std_levels_col) == 3:
                                dates[d]['press_readings'][hpa]['std_wdir'] = std_levels_col[1]
                                dates[d]['press_readings'][hpa]['std_wspeed'] = std_levels_col[2]
                            else:
                                dates[d]['press_readings'][hpa]['std_wdir'] = -32768
                                dates[d]['press_readings'][hpa]['std_wspeed'] = -32768

                    for x in range(1, 4):
                        sig_levels_col = columns[x].replace('/', ' ').split()
                        if len(sig_levels_col) > 0:
                            height = sig_levels_col[0]
                            if is_int(height):
                                if not height in dates[d]['height_readings']:
                                    dates[d]['height_readings'][height] = dict()
                                if len(sig_levels_col) == 3:
                                    dates[d]['height_readings'][height]['sig_wdir'] = sig_levels_col[1]
                                    dates[d]['height_readings'][height]['sig_wspeed'] = sig_levels_col[2]
                                else:
                                    dates[d]['height_readings'][height]['sig_wdir'] = -32768
                                    dates[d]['height_readings'][height]['sig_wspeed'] = -32768

                elif line.strip().startswith('Message Numbers'):
                    in_pilot = False
        return dates

# Had to implement a bit-more-complex state machine or multiple regex'es would be just too slow

class TxtFile(object):

    def __init__(self):
        self.started_at = ''
        self.station = 0
        self.longitude = 0.0
        self.latitude = 0.0
        self.altitude = 0
        self.sounding_type = ''
        self.rs_number = ''
        self.serial_number = ''
        self.clouds = ''
        self.burst_height = 0
        self.significant_levels = dict()
        self.standard_pressure_levels = dict()

    def __repr__(self):
        return """Vaisala Text Data: 
StartedAt     [""" + self.started_at.strftime("%Y-%m-%d %H:%M") + """]
Station       [""" + str(self.station) + """]
Latitude      [""" + str(self.latitude) + """]
Longitude     [""" + str(self.longitude) + """]
Altitude      [""" + str(self.altitude) + """]
Sig Levels    [""" + pformat(self.significant_levels, indent=4) + """]
S P Levels    [""" + pformat(self.standard_pressure_levels, indent=4) + """]"""

class SimpleParser(object):

    def __init__(self, wind_data):
        self.data = None
        self.current_state = None
        self.wind_data = wind_data

    def get_data(self):
        return self.data

    def parse(self, txt_file):
        self.data = TxtFile()
        self.current_state = StartedAtState(self.data)
        with open(txt_file, 'r') as wf:
            for line in wf:
                self.parse_line(line)
            if len(self.data.standard_pressure_levels) > 0:
                self._tally()

    def parse_line(self, line):
        if self.current_state != None and self.current_state.value(line) != None:
            self.current_state = self.current_state.next()

    def _tally(self):
        """Tally results, by matching an entry in the wind data and getting wspeed and wdir"""

        needle = self.data.started_at
        haystack = self.wind_data

        for date in haystack:
            if abs(date - needle) <= DEFAULT_INTERVAL:
                wind_data = self.wind_data[date]
                # Match standard pressure readings
                for press, dic in wind_data['press_readings'].items():
                    if press in self._get_standard_pressure_levels2():
                        standard_pressure_level = self._get_standard_pressure_levels2()[press]
                        standard_pressure_level.speed = int(dic['std_wspeed'])
                        standard_pressure_level.direction = int(dic['std_wdir'])

                # FIXME: Match significant level readings
                # for height, dic in wind_data['height_readings'].items():
                #     if height in self._get_significant_levels2():
                #         standard_pressure_level = self._get_significant_levels2()[press]
                #         standard_pressure_level.speed = int(dic['std_wspeed'])
                #         standard_pressure_level.direction = int(dic['std_wdir'])
                # pprint(wind_data)
                # pprint(self._get_significant_levels2())
                # sys.exit(1)

    def _get_standard_pressure_levels2(self):
        """Return the same dict, but where keys are pressure levels instead of secs. This way we reduce
        the number of loops per pressure reading in the wind_data"""
        d = dict()
        for sec, standard_pressure_level in self.data.standard_pressure_levels.items():
            d[standard_pressure_level.press] = standard_pressure_level
        return d

    def _get_significant_levels2(self):
        """Return the same dict, but where keys are heights levels instead of secs. This way we reduce
        the number of loops per pressure reading in the wind_data"""
        d = dict()
        for sec, significant_level in self.data.significant_levels.items():
            pass
            #d[standard_pressure_level.press] = standard_pressure_level
        return self.data.significant_levels

class State(object):

    def __init__(self, txt_file):
        self.next_state = None
        self.txt_file = txt_file

    def calc_secs(self, mins, secs):
        return secs + (mins * 60)

    def next(self):
        return self.next_state

    def value(self, line):
        return None

class StartedAtState(State):

    def __init__(self, txt_file):
        super().__init__(txt_file)
        self.next_state = StationState(txt_file)

    def value(self, line):
        s = None
        try:
            idx = line.index('Started at') + len('Started at')
            if idx >= 0:
                length = len(line)
                s = line[idx:length]
                s = s.strip()
                # dates will be like:   25 March 94 10:51 GMT
                idx2 = s.index(':')
                if idx2 > 0:
                    s = s[0:idx2+3]
                    try:
                        self.txt_file.started_at = datetime.strptime(s, "%d %B %y %H:%M")
                    except ValueError:
                        self.txt_file.started_at = datetime.strptime(s, "%d %B %Y %H:%M")
        except ValueError:
            pass
        return s

class StationState(State):

    def __init__(self, txt_file):
        super().__init__(txt_file)
        self.next_state = LocationState(txt_file)

    def value(self, line):
        s = None
        try:
            idx = line.index('Station') + len('Station')
            if idx >= 0:
                length = len(line)
                s = line[idx:length]
                s = s.replace(':', '')
                s = s.strip()
                self.txt_file.station = int(s)
        except ValueError:
            pass
        return s

class LocationState(State):

    def __init__(self, txt_file):
        super().__init__(txt_file)
        self.next_state = SignificantLevelsState1(txt_file)

    def value(self, line):
        s = None
        try:
            idx = line.index('Location') + len('Location')
            if idx >= 0:
                length = len(line)
                s = line[idx:length]
                s = s.replace(':', '')
                s = s.strip()
                
                latitude = ''
                idx2 = 1
                for c in s:
                    if c == ' ':
                        break
                    latitude += c
                    idx2 += 1

                self.txt_file.latitude = float(latitude)
                s = s[idx2:]
                s = s.strip()

                direction = ''
                idx2 = 1
                for c in s:
                    if c == ' ':
                        break
                    direction += c
                    idx2 += 1
                if direction.lower() == 's':
                    self.txt_file.latitude = float(self.txt_file.latitude * -1)
                # ignore other possible values
                s = s[idx2:]
                s = s.strip()

                longitude = ''
                idx2 = 1
                for c in s:
                    if c == ' ':
                        break
                    longitude += c
                    idx2 += 1

                self.txt_file.longitude = float(longitude)
                s = s[idx2:]
                s = s.strip()

                direction = ''
                idx2 = 1
                for c in s:
                    if c == ' ':
                        break
                    direction += c
                    idx2 += 1
                if direction.lower() != 'e':
                    self.txt_file.longitude = float(self.txt_file.longitude * -1)
                # ignore other possible values
                s = s[idx2:]
                s = s.strip()

                altitude = ''
                idx2 = 1
                for c in s:
                    if c == ' ':
                        break
                    altitude += c
                    idx2 += 1

                self.txt_file.altitude = float(altitude)
        except ValueError:
            pass
        return s

class SignificantLevel(object):

    def __init__(self, press, altitude, temp, rh, fp, speed, direction):
        self.press = press
        self.altitude = altitude
        self.temp = temp
        self.rh = rh
        self.fp = fp
        self.speed = speed
        self.direction = direction

    def __repr__(self):
        return "SignificantLevel(press=%s, altitude=%s, temp=%s, rh=%s, fp=%s, speed=%s, direction=%s)" % (self.press, self.altitude, self.temp, self.rh, self.fp, self.speed, self.direction)

class SignificantLevelsState1(State):

    def __init__(self, txt_file):
        super().__init__(txt_file)
        self.next_state = None
        self.title_found = False
        self.headers1_found = False
        self.headers2_found = False
        self.white_lines = 0

    def reset_states(self):
        self.headers1_found = False
        self.headers2_found = False

    def value(self, line):
        s = None
        self.next_state = None
        if line.strip() == '' and self.title_found == True:
            self.white_lines += 1

        if self.white_lines == 4:
            self.next_state = StandardPressureLevelsState1(self.txt_file)
            return True
        elif line.strip() == '':
            return

        if self.headers2_found:
            if line.strip()[0].lower() != 's':
                values = line.split()
                if len(values) >= 7:
                    minutes = int(values[0])
                    seconds = int(values[1])
                    press   = values[2]
                    height  = values[3]
                    temp    = values[4]
                    rh      = values[5]
                    fp      = values[6]

                    secs = self.calc_secs(minutes, seconds)
                    if secs not in self.txt_file.significant_levels:
                        self.txt_file.significant_levels[secs] = SignificantLevel(press=press, altitude=height, temp=temp, rh=rh, fp=fp, speed='', direction='')
                    # FIXME: add to element
                    #pprint(minutes)
                    self.next_state = self
            else:
                self.reset_states()
        elif self.headers1_found:
            s = line.strip()
            if len(s) > 3 and s[0:3].lower() == 'min':
                self.reset_states()
                self.headers2_found = True
                self.next_state = self
            else:
                s = None
        elif self.title_found:
            s = line.strip()
            if len(s) > 3 and s[0:4].lower() == 'time':
                self.reset_states()
                self.headers1_found = True
                self.next_state = self
            else:
                s = None
        else:
            try:
                idx = line.index('Significant levels: Temperature/Humidity') + len('Significant levels: Temperature/Humidity')
                if idx >= 0:
                    self.reset_states()
                    self.title_found = True
                    self.white_lines = 0
                    self.next_state = self
            except ValueError:
                s = None
        return s

class StandardPressureLevel(object):

    def __init__(self, press, altitude, temp, rh, fp, ascrate, speed, direction):
        self.press = press
        self.altitude = altitude
        self.temp = temp
        self.rh = rh
        self.fp  = fp
        self.ascrate = ascrate
        self.speed = speed
        self.direction = direction

    def __repr__(self):
        return "StandardPressureLevel(press=%s, altitude=%s, temp=%s, rh=%s, fp=%s, ascrate=%s, speed=%s, direction=%s)" % (self.press, self.altitude, self.temp, self.rh, self.fp, self.ascrate, self.speed, self.direction)


class StandardPressureLevelsState1(State):

    def __init__(self, txt_file):
        super().__init__(txt_file)
        self.next_state = None
        self.title_found = False
        self.headers1_found = False
        self.headers2_found = False
        self.white_lines = 0

    def reset_states(self):
        self.headers1_found = False
        self.headers2_found = False

    def value(self, line):
        s = None
        self.next_state = None
        if line.strip() == '' and self.title_found == True:
            self.white_lines += 1

        if self.white_lines == 4:
            #self.next_state = StandardPressureLevelsState2()
            self.next_state = None
            return s
        elif line.strip() == '':
            return

        if self.headers2_found:
            if line.strip()[0].lower() != 's':
                values = line.split()
                if len(values) >= 8:
                    try:
                        minutes = int(values[0])
                        seconds = int(values[1])
                    except ValueError:
                        return
                    press   = values[2]
                    height  = values[3]
                    temp    = values[4]
                    rh      = values[5]
                    fp      = values[6]
                    ascrate = values[7]

                    secs = self.calc_secs(minutes, seconds)
                    if secs not in self.txt_file.standard_pressure_levels:
                        self.txt_file.standard_pressure_levels[secs] = StandardPressureLevel(press=press, altitude=height, temp=temp, rh=rh, fp=fp, ascrate=ascrate, speed='', direction='')
                    # FIXME: add to element
                    #pprint(minutes)
                    self.next_state = self
            else:
                self.reset_states()
        elif self.headers1_found:
            s = line.strip()
            if len(s) > 3 and s[0:3].lower() == 'min':
                self.reset_states()
                self.headers2_found = True
                self.next_state = self
            else:
                s = None
        elif self.title_found:
            s = line.strip()
            if len(s) > 3 and s[0:4].lower() == 'time':
                self.reset_states()
                self.headers1_found = True
                self.next_state = self
            else:
                s = None
        else:
            try:
                idx = line.index('Standard pressure levels (PTU)') + len('Standard pressure levels (PTU)')
                if idx >= 0:
                    self.reset_states()
                    self.title_found = True
                    self.white_lines = 0
                    self.next_state = self
            except ValueError:
                s = None
        return s

def parse_txt_file(txt_file, wind_data):
    """
    Parse the Vaisala txt file, returning a mixed dict.
    """
    parser = SimpleParser(wind_data)
    parser.parse(txt_file)
    return parser.get_data()

def write_netcdf_file(data, output_file):
    """Writes the resulting data to a NetCDF file"""
    dataset = Dataset(output_file, "w", format="NETCDF4_CLASSIC")

    # Dimensions
    dataset.createDimension("time")

    dataset.setncattr('g.General.SiteWmoId', '93' + str(data.station))
    dataset.setncattr('g.MeasuringSystem.Longitude', str(data.longitude) + ' degree east')
    dataset.setncattr('g.MeasuringSystem.Latitude', str(data.latitude) + ' degree north')
    dataset.setncattr('g.MeasuringSystem.Altitude', str(data.altitude) + ' m')
    #dataset.setncattr('g.SurfaceObs.Pressure', str(ident['surface_pressure']) + ' hPa')
    #dataset.setncattr('g.SurfaceObs.Temperature', str(ident['surface_temperature']) + ' °C')
    #dataset.setncattr('g.SurfaceObs.RelativeHumidity', str(ident['surface_humidity']) + ' %')
    dataset.setncattr('g.General.SiteCode', "INVRCRGL")
    dataset.setncattr('g.General.SiteName', "Invercargill")
    dataset.setncattr('g.General.SiteInstitution', "MetService New Zealand")
    dataset.setncattr('g.Product.Producer', "National Institute of Water and Atmospheric Research (New Zealand)")
    dataset.setncattr('g.Product.References', "https://github.com/kinow/pccora")

    #dataset.station_type = ident['station_type']
    #dataset.region_number = ident['region_number']
    #dataset.wmo_block_number = ident['wmo_block_number']
    dataset.wmo_block_number = 93
    dataset.wmo_station_number = data.station
    #dataset.wind_speed_unit = str(ident['wind_speed_unit']) + ', comment: 0 = m/s 1 = knots'
    #dataset.telecommunications_headings = str(ident['telecommunications_headings']) + ', comment: 0 = No 1 = Yes'
    #dataset.res = ident['reserved']
    #dataset.sounding_type = str(ident['sounding_type']) + ', comment: 0 = PTU 1 = Only pressure 2 = No PTU (Radar'
    #dataset.start_mode = str(ident['start_mode']) + ', comment: 0 = Auto 1 = Manual'
    #dataset.time_elapsed = ident['time_elapsed']
    #dataset.ptu_rate = ident['ptu_rate']
    #dataset.spu_serial_number = ident['spu_serial_number']
    #dataset.year = ident['year']
    #dataset.month = ident['month']
    #dataset.day = ident['day']
    #dataset.julian_date = ident['julian_date']
    #dataset.hour = ident['hour']
    #dataset.minute = ident['minute']
    #dataset.message_year = ident['message_year']
    #dataset.message_month = ident['message_month']
    #dataset.message_day = ident['message_day']
    #dataset.message_hour = ident['message_hour']
    #dataset.cloud_group = ident['cloud_group']
    #dataset.weather_group = ident['weather_group']
    #dataset.napp = ident['napp']
    #dataset.humidity_correction = ident['humidity_correction']
    #dataset.success_of_signal = ident['success_of_signal']
    #dataset.pressure_accept_level = ident['pressure_accept_level']
    #dataset.pressure_replace_level = ident['pressure_replace_level']
    #dataset.pressure_reject_level = ident['pressure_reject_level']
    #dataset.temperature_accept_level = ident['temperature_accept_level']
    #dataset.temperature_replace_level = ident['temperature_replace_level']
    #dataset.temperature_reject_level = ident['temperature_reject_level']
    #dataset.humidity_accept_level = ident['humidity_accept_level']
    #dataset.humidity_replace_level = ident['humidity_replace_level']
    #dataset.humidity_reject_level = ident['humidity_reject_level']
    #dataset.total_omega_count = ident['total_omega_count']
    #dataset.reason_temination = ident['reason_temination']
    #dataset.omega_count = ident['omega_count']
    #dataset.wind_computing_mode = str(ident['wind_computing_mode']) + ', comment: 0 = Remote 1 = Local 2 = Differential'
    #dataset.wind_mode = str(ident['wind_mode']) + ', comment: 0 = Omega 1 = Loran-C 2 = Radar 255 = Only PTU'
    #dataset.stations_used = str(ident['stations_used']) + ', comment: One bit for each station 1 = Used 0 = Not used'
    #dataset.loranc_chains_used = ident['loranc_chains_used']
    #dataset.gri_chain_1 = ident['gri_chain_1']
    #dataset.gri_chain_2 = ident['gri_chain_2']
    #dataset.exclude_loran_transmitters = str(ident['exclude_loran_transmitters']) + ', comment: One bit for each in the chain; and chain 2 transmitted'
    #dataset.phase_integration_time = str(ident['phase_integration_time']) + ', comment: 0 = time (s) 1 = Altitude (m/MSI'
    #dataset.phase_integration_time_1 = ident['phase_integration_time_1']
    #dataset.phase_integration_time_2 = ident['phase_integration_time_2']
    #dataset.phase_integration_time_3 = ident['phase_integration_time_3']
    #dataset.phase_integration_time_4 = ident['phase_integration_time_4']
    #dataset.phase_integration_time_5 = ident['phase_integration_time_5']
    #dataset.phase_integration_time_6 = ident['phase_integration_time_6']
    #dataset.phase_integration_change_level_1 = ident['phase_integration_change_level_1']
    #dataset.phase_integration_change_level_2 = ident['phase_integration_change_level_2']
    #dataset.phase_integration_change_level_3 = ident['phase_integration_change_level_3']
    #dataset.phase_integration_change_level_4 = ident['phase_integration_change_level_4']
    #dataset.phase_integration_change_level_5 = ident['phase_integration_change_level_5']
    #dataset.phase_integration_change_level_6 = ident['phase_integration_change_level_6']
    #dataset.reference_pressure = str(ident['reference_pressure']) + ' hPa'
    #dataset.reference_temperature = str(ident['reference_temperature']) + ' °C'
    #dataset.reference_humidity = str(ident['reference_humidity']) + ' %'

    dataset.institution = "MetService New Zealand"
    dataset.datetime = str(data.started_at)
    dataset.comment = 'For more information about the variables see: https://badc.nerc.ac.uk/data/ukmo-rad-hires/pc-coradata.html'

    elapsed_time = []
    #logarithmic_pressure = []
    temperature = []
    relative_humidity = []
    #north_wind = []
    #east_wind = []
    altitude = []
    pressure = []
    dew_point = []
    #mixing_ratio = []
    wind_direction = []
    wind_speed = []
    #azimuth_angle = []
    #horizontal_distance = []
    #longitude = []
    #latitude = []
    #significance_key = []
    #recalculated_significance_key = []
    #radar_height = []
    ascrate = []

    for secs, standard_pressure_level in data.standard_pressure_levels.items():
        elapsed_time.append(secs)
        temperature.append(standard_pressure_level.temp)
        relative_humidity.append(standard_pressure_level.rh)
        altitude.append(standard_pressure_level.altitude)
        pressure.append(standard_pressure_level.press)
        dew_point.append(standard_pressure_level.fp)
        wind_direction.append(standard_pressure_level.direction)
        wind_speed.append(standard_pressure_level.speed)
        ascrate.append(standard_pressure_level.ascrate)

    # elapsed_time
    elapsed_time_variable = dataset.createVariable('elapsed_time', 'f4', ("time", ), zlib=True, fill_value=-32768)
    elapsed_time_variable.standard_name = 'elapsed_time'
    elapsed_time_variable.units = 's'
    elapsed_time_variable.long_name = 'Elapsed time since sonde release'
    elapsed_time_variable.g_format_type = 'FLT'
    elapsed_time_variable[:] = elapsed_time

    # temperature
    temperature_variable = dataset.createVariable('temp', 'f4', ("time", ), zlib=True, fill_value=-32768)
    temperature_variable.standard_name = 'air_temperature'
    temperature_variable.units = 'C'
    temperature_variable.long_name = 'Temperature'
    temperature_variable.g_format_type = 'FLT'
    temperature_variable.coordinates = "lon lat alt"
    temperature_variable[:] = temperature

    # relative_humidity
    relative_humidity_variable = dataset.createVariable('rh', 'f4', ("time", ), zlib=True, fill_value=-32768)
    relative_humidity_variable.standard_name = 'relative_humidity'
    relative_humidity_variable.units = '%'
    relative_humidity_variable.long_name = 'Relative Humidity'
    relative_humidity_variable.g_format_type = 'FLT'
    relative_humidity_variable.coordinates = "lon lat alt"
    relative_humidity_variable[:] = relative_humidity

    # altitude
    altitude_variable = dataset.createVariable('alt', 'f4', ("time", ), zlib=True, fill_value=-32768)
    altitude_variable.standard_name = 'altitude'
    altitude_variable.units = 'gpm'
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
    dew_point_variable.units = 'C'
    dew_point_variable.long_name = 'Frostpoint'
    dew_point_variable.g_format_type = 'FLT'
    dew_point_variable.coordinates = "lon lat alt"
    dew_point_variable[:] = dew_point

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

    # ascrate
    ascrate_variable = dataset.createVariable('ascrate', 'f4', ("time", ), zlib=True, fill_value=-32768)
    ascrate_variable.standard_name = 'ascrate'
    ascrate_variable.units = 'm/s'
    ascrate_variable.long_name = 'Ascension rate'
    ascrate_variable.g_format_type = 'FLT'
    ascrate_variable[:] = ascrate 

    dataset.close()

def main():
    wind_file = '/home/kinow/Downloads/Inv_upper_air_wind_MetService_simple2.txt'
    txt_file = '/home/kinow/Downloads/99100110.TXT'
    output_file = '/home/kinow/Downloads/99100110-with-wind-data.nc'

    logger.info('Parsing WIND file')
    dates = parse_wind_file(wind_file)
    logger.info('Done')

    logger.info('Parsing TXT file')
    data = parse_txt_file(txt_file, dates)
    logger.info('Done')

    logger.info('Writing NetCDF file')
    write_netcdf_file(data, output_file)
    
if __name__ == '__main__':
    main()

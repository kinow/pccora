
import re
from pprint import pprint, pformat
from datetime import datetime
import pytz
import logging
from collections import namedtuple

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
                    'readings': dict()
                }

                in_pilot = True

            elif in_pilot:
                
                if line.count('|') == 4 and line.count('hPa') == 0:

                    columns = line.split('|')
                    std_levels_col = columns[0].replace('/', ' ').split()
                    sig_levels_col = columns[1].replace('/', '').split()

                    hpa = std_levels_col[0]
                    if is_int(hpa):
                        if not hpa in dates[d]['readings']:
                            dates[d]['readings'][hpa] = dict()
                        if len(std_levels_col) == 3:
                            dates[d]['readings'][hpa]['std_wdir'] = std_levels_col[1]
                            dates[d]['readings'][hpa]['std_wspeed'] = std_levels_col[2]
                        else:
                            dates[d]['readings'][hpa]['std_wdir'] = -32768
                            dates[d]['readings'][hpa]['std_wspeed'] = -32768

                    # TODO: it is hPa, right?
                    hpa = sig_levels_col[0]
                    if is_int(hpa):
                        if not hpa in dates[d]['readings']:
                            dates[d]['readings'][hpa] = dict()
                        if len(sig_levels_col) == 3:
                            dates[d]['readings'][hpa]['sig_wdir'] = sig_levels_col[1]
                            dates[d]['readings'][hpa]['sig_wspeed'] = sig_levels_col[2]
                        else:
                            dates[d]['readings'][hpa]['sig_wdir'] = -32768
                            dates[d]['readings'][hpa]['sig_wspeed'] = -32768

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
                self.tally()

    def parse_line(self, line):
        if self.current_state != None and self.current_state.value(line) != None:
            self.current_state = self.current_state.next()

    def tally(self):
        """Tally results, by matching an entry in the wind data and getting wspeed and wdir"""
        pprint(self.wind_data)

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
                    self.txt_file.started_at = datetime.strptime(s, "%d %B %y %H:%M")
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

SignificantLevel = namedtuple('SignificantLevel', 'press altitude temp rh fp speed direction')

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

StandardPressureLevel = namedtuple('StandardPressureLevel', 'press altitude temp rh fp ascrate speed direction')

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

def main():
    wind_file = '/home/kinow/Downloads/Inv_upper_air_wind_MetService_simple.txt'
    txt_file = '/home/kinow/Downloads/94032510.txt'

    dates = parse_wind_file(wind_file)
    data = parse_txt_file(txt_file, dates)

    pprint(data)
    
if __name__ == '__main__':
    main()

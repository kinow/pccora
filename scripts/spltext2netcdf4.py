
import re
from pprint import pprint
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

PILOT_REGEX = '^([0-9]+)\s*([a-z0-9\s]+)\s+pilot\s+for\s+(.*)$'
PILOT_PATTERN = re.compile(PILOT_REGEX, flags=re.IGNORECASE)

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

def main():
    wind_file = '/home/kinow/Downloads/Inv_upper_air_wind_MetService_simple.txt'
    txt_file = '/home/kinow/Downloads/94032510.txt'

    dates = parse_wind_file(wind_file)

    pprint(dates)

if __name__ == '__main__':
    main()

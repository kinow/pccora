from construct import *

pccora_header = Struct("pccora_header",
    String("copyright", 20),
    ULInt16("identification_length"),
    ULInt16("syspar_length"),
    ULInt16("data_records"),
    ULInt16("standard_levels"),
    ULInt16("data_type"),
    ULInt16("data_length"),
    Enum(Byte("file_ready"),
        READY = 1,
        NOT_READY = 0,
        _default_ = "UNKNOWN",
    ),
    Bytes("reserved", 17)
)

pccora_identification = Struct("pccora_identification",
    ULInt16("station_type"),
    ULInt16("region_number"),
    ULInt16("wmo_block_number"),
    ULInt16("wmo_station_number"),
    ULInt16("station_latitude", lambda x: x * 0.01),
    ULInt16("station_longitude"),
    ULInt16("station_altitude"),
    ULInt16("wind_speed_unit"),
    ULInt16("telecommunications_headings"),
    ULInt16("reserved"),
    ULInt16("sounding_type"),
    ULInt16("start_mode"),
    ULInt16("time_elapsed"),
    ULInt16("ptu_rate")
)

pccora_file = Struct("pccora_file",
    pccora_header,
    pccora_identification
)

class PCCORAParser(object):

    def __init__(self):
        self.header = None

    def parse(self, file_arg):
        fid = open(file_arg, 'rb')
        self.header = pccora_file.parse_stream(fid)
        fid.close()
        return ''

    def get_header(self):
        return self.header

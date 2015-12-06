from construct import *

#===============================================================================
# Construct parser objects
#===============================================================================

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
    ULInt16("station_latitude"),
    ULInt16("station_longitude"),
    ULInt16("station_altitude"),
    ULInt16("wind_speed_unit"),
    ULInt16("telecommunications_headings"),
    ULInt16("reserved"),
    ULInt16("sounding_type"),
    ULInt16("start_mode"),
    ULInt16("time_elapsed"),
    ULInt16("ptu_rate"),
    SLInt32("spu_serial_number"),
    ULInt16("year"),
    ULInt16("month"),
    ULInt16("day"),
    ULInt16("julian_date"),
    ULInt16("hour"),
    ULInt16("minute"),
    ULInt16("message_year"),
    ULInt16("message_month"),
    ULInt16("message_day"),
    ULInt16("message_hour"),
    String("cloud_group", 6),
    String("weather_group", 6),
    String("napp", 6),
    ULInt16("surface_pressure"),
    ULInt16("surface_temperature"),
    ULInt16("surface_humidity"),
    ULInt16("surface_wind_direction"),
    ULInt16("surface_wind_speed"),
    String("radiosonde_number", 10),
    String("sounding_number", 10),
    ULInt16("pressure_correction"),
    ULInt16("temperature_correction"),
    ULInt16("humidity_correction"),
    ULInt16("success_of_signal"),
    ULInt16("pressure_accept_level"),
    ULInt16("pressure_replace_level"),
    ULInt16("pressure_reject_level"),
    ULInt16("temperature_accept_level"),
    ULInt16("temperature_replace_level"),
    ULInt16("temperature_reject_level"),
    ULInt16("humidity_accept_level"),
    ULInt16("humidity_replace_level"),
    ULInt16("humidity_reject_level"),
    ULInt16("total_omega_count"),
    ULInt16("reason_temination"),
    ULInt16("omega_count"),
    Enum(ULInt16("wind_computing_mode"),
        REMOTE = 0,
        LOCAL = 1,
        DIFFERENTIAL = 2,
        _default_ = "UNKNOWN"
    ),
    Enum(ULInt16("wind_mode"),
        OMEGA = 0,
        LORANC = 1,
        RADAR = 2,
        ONLY_PTU = 255,
        _default_ = "UNKNOWN"
    ),
    Enum(Byte("stations_used"),
        NOT_USED = 0,
        USED = 1,
        _default_ = "UNKNOWN"
    ),
    Byte("loranc_chains_used"),
    ULInt16("gri_chain_1"),
    ULInt16("gri_chain_2"),
    ULInt16("exclude_loran_transmitters"),
    Enum(Byte("phase_integration_time"),
        TIME = 0,
        ALTITUDE = 1,
        _default_ = "UNKNOWN"
    ),
    ULInt16("phase_integration_time_1"),
    ULInt16("phase_integration_time_2"),
    ULInt16("phase_integration_time_3"),
    ULInt16("phase_integration_time_4"),
    ULInt16("phase_integration_time_5"),
    ULInt16("phase_integration_time_6"),
    ULInt16("phase_integration_change_level_1"),
    ULInt16("phase_integration_change_level_2"),
    ULInt16("phase_integration_change_level_3"),
    ULInt16("phase_integration_change_level_4"),
    ULInt16("phase_integration_change_level_5"),
    ULInt16("phase_integration_change_level_6"),
    ULInt16("referece_pressure"),
    ULInt16("reference_temperature"),
    ULInt16("reference_humidity"),
)

pccora_syspar = Struct("pccora_syspar",
    Bytes("syspar", 8087)
)

pccora_data = Struct("pccora_data",
    LFloat32("time"),
    ULInt16("logarithmic_pressure"),
    ULInt16("temperature"),
    ULInt16("humidity"),
    ULInt16("north_wind"),
    ULInt16("east_wind"),
    ULInt16("altitude"),
    ULInt16("pressure"),
    ULInt16("dew_point_temperature"),
    ULInt16("mixing_ratio"),
    ULInt16("wind_direction"),
    ULInt16("wind_speed"),
    ULInt16("azimuth"),
    ULInt16("horizontal_distance"),
    ULInt16("longitude"),
    ULInt16("latitude"),
    Bytes("significance_key", 2),
    Bytes("recalculated_significance_key", 2),
    ULInt16("radar_height")
)

pccora_file = Struct("pccora_file",
    pccora_header,
    pccora_identification,
    pccora_syspar,
    GreedyRange(pccora_data)
)

class PCCORAParser(object):
    """
    A PC-CORA parser, that uses the construct binary parser library to read the input data.

    Users may call one of the two following methods to parse either a file (that will be read with the 'rb' flag),
    or a file resource.

    * ``parse_file()``
    * ``parse_stream()``

    Both methods fill an internal 'result' object (a construct Container). After this, users may call one of the
    following methods to retrieve PC-CORA parts.

    * ``get_header()``
    * ``get_identification()``
    * ``get_syspar()``
    * ``get_data()``

    Or to get the whole result.

    * ``get_result()``
    """

    def __init__(self):
        self.result = None

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def parse_file(self, file_arg):
        """
        Parse a file, by opening it with 'rb' flags and sending it through the construct binary parser.
        """
        with open(file_arg, 'rb') as fid:
            self.result = pccora_file.parse_stream(fid)

    def parse_stream(self, stream_arg):
        """
        Parse a file, by passing the stream argument thourhg the construct binary parser.
        """
        self.result = pccora_file.parse_stream(stream_arg)

    def get_result(self):
        """Return the parser result"""
        return self.result

    def get_header(self):
        """Return the PC-CORA file header"""
        return self.result.pccora_header

    def get_identification(self):
        """Return the PC-CORA file identification"""
        return self.result.pccora_identification

    def get_syspar(self):
        """Return the PC-CORA file SYSPAR bytes"""
        return self.result.pccora_syspar

    def get_data(self):
        """Return the PC-CORA file data array"""
        return self.result.pccora_data

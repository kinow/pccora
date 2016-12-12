from construct import *
from datetime import datetime, timedelta
import math
import array

#===============================================================================
# Construct parser objects
#===============================================================================

pccora_header = Struct("pccora_header",
    ExprAdapter(String("copyright", 20),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    SLInt16("identification_length"),
    SLInt16("syspar_length"),
    SLInt16("data_records"),
    SLInt16("standard_levels"),
    SLInt16("data_type"),
    SLInt16("data_length"),
    Enum(Byte("file_ready"),
        READY = 1,
        NOT_READY = 0,
        _default_ = "UNKNOWN",
    ),
    Bytes("reserved", 17)
)

pccora_identification = Struct("pccora_identification",
    SLInt16("station_type"),
    SLInt16("region_number"),
    SLInt16("wmo_block_number"),
    SLInt16("wmo_station_number"),
    ExprAdapter(SLInt16("station_latitude"),
        encoder = lambda obj, ctx: int(obj / 0.01) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.01 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("station_longitude"),
        encoder = lambda obj, ctx: int(obj / 0.01) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.01 if obj != -32768 else obj
    ),
    SLInt16("station_altitude"),
    SLInt16("wind_speed_unit"),
    SLInt16("telecommunications_headings"),
    SLInt16("reserved"),
    SLInt16("sounding_type"),
    SLInt16("start_mode"),
    SLInt16("time_elapsed"),
    SLInt16("ptu_rate"),
    SLInt32("spu_serial_number"),
    ExprAdapter(SLInt16("year"),
        encoder = lambda obj, ctx: (divmod(obj, 100)[1]) if obj != -32768 else obj,
        decoder = lambda obj, ctx: (1900 + obj if obj >= 20 else 2000 + obj) if obj != -32768 and obj < 1000 else obj
    ),
    SLInt16("month"),
    SLInt16("day"),
    SLInt16("julian_date"),
    SLInt16("hour"),
    SLInt16("minute"),
    SLInt16("message_year"),
    SLInt16("message_month"),
    SLInt16("message_day"),
    SLInt16("message_hour"),
    ExprAdapter(String("cloud_group", 6),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    ExprAdapter(String("weather_group", 6),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    ExprAdapter(String("napp", 6),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    ExprAdapter(SLInt16("surface_pressure"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("surface_temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    SLInt16("surface_humidity"),
    SLInt16("surface_wind_direction"),
    SLInt16("surface_wind_speed"),
    ExprAdapter(String("radiosonde_number", 10),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    ExprAdapter(String("sounding_number", 10),
        encoder = lambda obj, ctx: obj.encode(),
        decoder = lambda obj, ctx: obj.decode('utf-8', 'ignore')
    ),
    ExprAdapter(SLInt16("pressure_correction"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("temperature_correction"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    SLInt16("humidity_correction"),
    SLInt16("success_of_signal"),
    SLInt16("pressure_accept_level"),
    SLInt16("pressure_replace_level"),
    SLInt16("pressure_reject_level"),
    SLInt16("temperature_accept_level"),
    SLInt16("temperature_replace_level"),
    SLInt16("temperature_reject_level"),
    SLInt16("humidity_accept_level"),
    SLInt16("humidity_replace_level"),
    SLInt16("humidity_reject_level"),
    SLInt16("total_omega_count"),
    SLInt16("reason_temination"),
    #SLInt16("omega_count"),
    Bytes('omega_count', 22),
    SLInt16("wind_computing_mode"),
    # Enum(SLInt16("wind_computing_mode"),
    #     REMOTE = 0,
    #     LOCAL = 1,
    #     DIFFERENTIAL = 2,
    #     _default_ = "UNKNOWN"
    # ),
    SLInt16("wind_mode"),
    # Enum(SLInt16("wind_mode"),
    #     OMEGA = 0,
    #     LORANC = 1,
    #     RADAR = 2,
    #     ONLY_PTU = 255,
    #     _default_ = "UNKNOWN"
    # ),
    SLInt16("stations_used"),
    # Enum(Byte("stations_used"),
    #     NOT_USED = 0,
    #     USED = 1,
    #     _default_ = "UNKNOWN"
    # ),
    Byte("loranc_chains_used"),
    SLInt16("gri_chain_1"),
    SLInt16("gri_chain_2"),
    SLInt16("exclude_loran_transmitters"),
    Byte("phase_integration_time"),
    # Enum(Byte("phase_integration_time"),
    #     TIME = 0,
    #     ALTITUDE = 1,
    #     _default_ = "UNKNOWN"
    # ),
    SLInt16("phase_integration_time_1"),
    SLInt16("phase_integration_time_2"),
    SLInt16("phase_integration_time_3"),
    SLInt16("phase_integration_time_4"),
    SLInt16("phase_integration_time_5"),
    SLInt16("phase_integration_time_6"),
    SLInt16("phase_integration_change_level_1"),
    SLInt16("phase_integration_change_level_2"),
    SLInt16("phase_integration_change_level_3"),
    SLInt16("phase_integration_change_level_4"),
    SLInt16("phase_integration_change_level_5"),
    SLInt16("phase_integration_change_level_6"),
    ExprAdapter(SLInt16("reference_pressure"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("reference_temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj * 0.1 if obj != -32768 else obj
    ),
    SLInt16("reference_humidity"),
    Value("datetime", lambda ctx: None if ctx['year'] == 0 or ctx['month'] == 0 or ctx['day'] == 0 else datetime(ctx['year'], ctx['month'], ctx['day'], ctx['hour'], ctx['minute'])),
    Value("launch_time", lambda ctx: None if ctx['datetime'] == None else ctx['datetime'] + timedelta(seconds=ctx['time_elapsed']))
)

pccora_syspar = Struct("pccora_syspar",
    Bytes("syspar", 8087)
)

pccora_data = Struct("pccora_data",
    LFloat32("time"),
    SLInt16("logarithmic_pressure"),
    ExprAdapter(SLInt16("temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    SLInt16("humidity"),
    ExprAdapter(SLInt16("north_wind"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("east_wind"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("altitude"),
        encoder = lambda obj, ctx: obj - 30000.0 if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj + 30000.0 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("pressure"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("dew_point_temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("mixing_ratio"),
        encoder = lambda obj, ctx: obj,
        decoder = lambda obj, ctx: obj
    ),
    SLInt16("wind_direction"),
    ExprAdapter(SLInt16("wind_speed"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj if obj == -32768 else int(obj * 0.01)
    ),
    SLInt16("azimuth"),
    SLInt16("horizontal_distance"),
    ExprAdapter(SLInt16("longitude"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("latitude"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(Bytes("significance_key", 2),
        encoder = lambda obj, ctx: obj if obj == -32768 else bytes(obj),
        decoder = lambda obj, ctx: [bin(obj[i]) for i in range(0, len(obj))] if obj != -32768 else obj
    ),
    ExprAdapter(Bytes("recalculated_significance_key", 2),
        encoder = lambda obj, ctx: obj if obj == -32768 else bytes(obj),
        decoder = lambda obj, ctx: [bin(obj[i]) for i in range(0, len(obj))] if obj != -32768 else obj
    ),
    SLInt16("radar_height"),
    Value('spress', lambda ctx: math.exp(ctx['logarithmic_pressure']/4096.0))
)

pccora_hires_data = Struct("pccora_hires_data",
    LFloat32("time"),
    SLInt16("logarithmic_pressure"),
    ExprAdapter(SLInt16("temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    SLInt16("humidity"),
    ExprAdapter(SLInt16("north_wind"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("east_wind"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("altitude"),
        encoder = lambda obj, ctx: obj - 30000.0 if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj + 30000.0 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("pressure"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("dew_point_temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("mixing_ratio"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    SLInt16("wind_direction"),
    ExprAdapter(SLInt16("wind_speed"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: obj if obj == -32768 else int(obj * 0.01)
    ),
    SLInt16("azimuth"),
    SLInt16("horizontal_distance"),
    ExprAdapter(SLInt16("longitude"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(SLInt16("latitude"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    ExprAdapter(Bytes("significance_key", 2),
        encoder = lambda obj, ctx: obj if obj == -32768 else bytes(obj),
        decoder = lambda obj, ctx: [bin(obj[i]) for i in range(0, len(obj))] if obj != -32768 else obj
    ),
    ExprAdapter(Bytes("recalculated_significance_key", 2),
        encoder = lambda obj, ctx: obj if obj == -32768 else bytes(obj),
        decoder = lambda obj, ctx: [bin(obj[i]) for i in range(0, len(obj))] if obj != -32768 else obj
    ),
    SLInt16("radar_height"),
    Value('spress', lambda ctx: math.exp(ctx['logarithmic_pressure']/4096.0))
)

pccora_s_hires_data = Struct("pccora_hires_data",
    SLInt16("time"),
    SLInt16("logarithmic_pressure"),
    ExprAdapter(SLInt16("temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    SLInt16("humidity"),
    SLInt16("n_data"),
    SLInt16("c1"),
    SLInt16("c2"),
    SLInt16("c3"),
    SLInt16("c4"),
    SLInt16("c5"),
    SLInt16("c6"),
    SLInt16("c7"),
    SLInt16("c8"),
    SLInt16("cycles"),
    SLInt16("not_used"),
    Bytes("buffer", 20)
)

pccora_z_hires_data = Struct("pccora_hires_data",
    SLInt16("time"),
    SLInt16("logarithmic_pressure"),
    ExprAdapter(SLInt16("temperature"),
        encoder = lambda obj, ctx: int(obj / 0.1) if obj != -32768 else obj,
        decoder = lambda obj, ctx: float(obj) * 0.1 if obj != -32768 else obj
    ),
    SLInt16("humidity"),
    SLInt16("n_data"),
    SLInt16("c1"),
    SLInt16("c2"),
    SLInt16("c3"),
    SLInt16("c4"),
    SLInt16("c5"),
    SLInt16("c6"),
    SLInt16("c7"),
    SLInt16("c8"),
    SLInt16("cycles"),
    SLInt16("not_used"),
    Bytes("buffer", 20)
)

pccora_file = Struct("pccora_file",
    pccora_header,
    pccora_identification,
    pccora_syspar,
    Range(mincount=1, maxcout=25, subcon=pccora_data),
    OptionalGreedyRange(pccora_hires_data)
)

# S file. The raw version of the Z file.
pccora_s_file = Struct("pccora_s_hires_data",
    pccora_header,
    pccora_identification,
    pccora_syspar,
    OptionalGreedyRange(pccora_s_hires_data)
)

# Z file.
pccora_s_file = Struct("pccora_z_hires_data",
    pccora_header,
    pccora_identification,
    pccora_syspar,
    OptionalGreedyRange(pccora_z_hires_data)
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
    * ``get_hires_data()``

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

    def parse_s_file(self, file_arg):
        """
        Parse an S file, by opening it with 'rb' flags and sending it through the construct binary parser.
        """
        with open(file_arg, 'rb') as fid:
            self.result = pccora_s_file.parse_stream(fid)

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

    def get_hires_data(self):
        """Return the PC-CORA file high resolution data array"""
        return self.result.pccora_hires_data



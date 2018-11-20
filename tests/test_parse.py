import unittest

from pccora import PCCORAParser


# test files from: ftp://ftp1.esrl.noaa.gov/psd3/cruises/AERO_1999/RHB/balloon/Raw/


class TestParse(unittest.TestCase):

    def setUp(self):
        self.parser = PCCORAParser()

    def test_constructor(self):
        self.assertIsNone(self.parser.result)

    def test_parse(self):
        self.parser.parse_file('93011809.21S')
        self.assertIsNotNone(self.parser.result)
        result = self.parser.get_result()
        self.assertEqual(result, self.parser.result)
        header = self.parser.get_header()
        self.assertTrue("Vaisala" in header.copyright)

    def test_parse_stream(self):
        with open('93011809.21S', 'rb') as file_stream:
            self.parser.parse_stream(file_stream)
            header = self.parser.get_header()
            self.assertTrue("Vaisala" in header.copyright)

    def test_parse_s_file(self):
        self.parser.parse_s_file('93011809.21S')
        header = self.parser.get_header()
        self.assertTrue("Vaisala" in header.copyright)

    def test_parse_z_file(self):
        self.parser.parse_z_file('93011809.21Z')
        header = self.parser.get_header()
        self.assertTrue("Vaisala" in header.copyright)

    def test_parse_header(self):
        self.parser.parse_file('93011809.21S')
        header = self.parser.get_header()
        self.assertTrue("Vaisala" in header.copyright)
        self.assertEqual(196, header.identification_length)
        self.assertEqual(8087, header.syspar_length)
        self.assertTrue(header.data_records > 0)

    def test_parse_identification(self):
        self.parser.parse_file('93011809.21S')
        identification = self.parser.get_identification()
        # TBD: funny the block number to be 2?!
        self.assertEqual(2, identification.wmo_block_number)
        self.assertEqual(313, identification.wmo_station_number)
        self.assertTrue(identification.station_latitude > 60)
        self.assertTrue(identification.station_longitude > 24)
        # these values match the file name
        self.assertEqual(1993, identification.year)
        self.assertEqual(1, identification.month)
        self.assertEqual(18, identification.day)
        self.assertEqual(9, identification.hour)
        self.assertEqual(21, identification.minute)
        self.assertTrue(identification.surface_pressure > 0)
        self.assertTrue(identification.surface_wind_speed > 0)
        self.assertTrue(identification.reference_temperature > 23)

    def test_parse_data(self):
        self.parser.parse_file('93011809.21S')
        data = self.parser.get_data()
        # TBD: funny that the length of data here does not match with header
        self.assertTrue(len(data) > 0)
        for entry in data:
            self.assertTrue(entry.time >= 0.0)
            self.assertTrue(entry.wind_speed >= 0)
            self.assertTrue(entry.pressure >= 0.0)

    def test_parse_hires_data(self):
        self.parser.parse_z_file('93011809.21Z')
        hires_data = self.parser.get_hires_data()
        # TBD: funny that the length of hires data here does not match with header
        self.assertTrue(len(hires_data) > 0)
        for entry in hires_data:
            self.assertIsNotNone(entry.time)
            self.assertIsNotNone(entry.humidity)
            self.assertIsNotNone(entry.temperature)

    def test_parse_syspar(self):
        self.parser.parse_file('93011809.21S')
        syspar = self.parser.get_syspar()
        self.assertTrue(len(syspar) > 0)

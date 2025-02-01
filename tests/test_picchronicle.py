import unittest
from datetime import datetime

from src.picchronicle import get_date_taken, get_decimal_from_dms, get_gps_coords

class TestPicChronicleFunctions(unittest.TestCase):
    def test_get_date_taken_valid(self):
        # Test with valid EXIF date format.
        exif_data = {'DateTimeOriginal': '2020:12:31 23:59:59'}
        dt = get_date_taken(exif_data)
        expected_dt = datetime(2020, 12, 31, 23, 59, 59)
        self.assertEqual(dt, expected_dt)

    def test_get_date_taken_invalid(self):
        # Test with an invalid date format.
        exif_data = {'DateTimeOriginal': 'invalid date'}
        dt = get_date_taken(exif_data)
        self.assertIsNone(dt)

    def test_get_date_taken_missing(self):
        # Test when date info is missing.
        exif_data = {}
        dt = get_date_taken(exif_data)
        self.assertIsNone(dt)

    def test_get_decimal_from_dms_positive(self):
        # Test conversion of DMS to decimal for a northern/eastern coordinate.
        dms = [(10, 1), (20, 1), (30, 1)]  # Represents 10°20'30"
        result = get_decimal_from_dms(dms, 'N')
        expected = 10 + 20/60 + 30/3600
        self.assertAlmostEqual(result, expected, places=5)

    def test_get_decimal_from_dms_negative(self):
        # Test conversion for southern/western coordinate (should be negative).
        dms = [(10, 1), (20, 1), (30, 1)]
        result = get_decimal_from_dms(dms, 'S')
        expected = -(10 + 20/60 + 30/3600)
        self.assertAlmostEqual(result, expected, places=5)

    def test_get_gps_coords(self):
        """
        Test extraction of GPS coordinates from EXIF data.
        Note: The function expects the GPSInfo dictionary keys to be the raw integer tags.
        We'll simulate this using PIL's ExifTags.GPSTAGS mapping.
        """
        from PIL import ExifTags

        # Create a fake GPSInfo dictionary using the integer keys that map to GPS tags.
        gps_tags = {v: k for k, v in ExifTags.GPSTAGS.items()}
        fake_gps = {
            gps_tags['GPSLatitudeRef']: 'N',
            gps_tags['GPSLatitude']: [(10, 1), (20, 1), (30, 1)],
            gps_tags['GPSLongitudeRef']: 'E',
            gps_tags['GPSLongitude']: [(40, 1), (50, 1), (60, 1)]
        }
        exif_data = {'GPSInfo': fake_gps}
        coords = get_gps_coords(exif_data)
        expected_lat = 10 + 20/60 + 30/3600
        expected_lon = 40 + 50/60 + 60/3600

        self.assertIsNotNone(coords, "GPS coordinates should not be None")
        self.assertAlmostEqual(coords[0], expected_lat, places=5)
        self.assertAlmostEqual(coords[1], expected_lon, places=5)

if __name__ == '__main__':
    unittest.main()

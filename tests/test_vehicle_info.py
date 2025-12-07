import os
import unittest
from unittest.mock import patch

from vehicle_info import get_vehicle_info


class VehicleInfoTests(unittest.TestCase):
    def test_known_plate_with_hyphen(self):
        info = get_vehicle_info("ABC-1234")
        self.assertIsNotNone(info)
        self.assertEqual(info.brand, "Volkswagen")

    def test_known_plate_compact(self):
        info = get_vehicle_info("ABC1234")
        self.assertIsNotNone(info)
        self.assertEqual(info.brand, "Volkswagen")

    def test_unknown_plate_returns_none(self):
        info = get_vehicle_info("ZZZ9Z99")
        self.assertIsNone(info)

    @patch.dict(os.environ, {"VEHICLE_API_URL": "https://example.test/api/{plate}"}, clear=True)
    @patch("vehicle_info.requests.get")
    def test_external_api_used_when_configured(self, mock_get):
        class Resp:
            status_code = 200

            def json(self):
                return {
                    "plate": "EXT1A23",
                    "brand": "API",
                    "model": "Retornado",
                    "color": "Azul",
                    "year": 2024,
                }

        mock_get.return_value = Resp()
        info = get_vehicle_info("EXT1A23")
        self.assertIsNotNone(info)
        self.assertEqual(info.brand, "API")


if __name__ == "__main__":
    unittest.main()

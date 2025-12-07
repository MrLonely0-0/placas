import unittest

from plate_validator import validate_plate, is_valid_plate


class PlateValidatorTests(unittest.TestCase):
    def test_old_plate_valid(self):
        result = validate_plate("ABC-1234")
        self.assertTrue(result.valid)
        self.assertEqual(result.plate_type, "ANTIGA")

    def test_mercosul_plate_valid(self):
        result = validate_plate("BRA2E19")
        self.assertTrue(result.valid)
        self.assertEqual(result.plate_type, "MERCOSUL")

    def test_mercosul_alt_valid(self):
        result = validate_plate("JDK4B22")
        self.assertTrue(result.valid)
        self.assertEqual(result.plate_type, "MERCOSUL")

    def test_old_without_hyphen_valid_and_normalized(self):
        result = validate_plate("ABC1234")
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "ABC-1234")

    def test_mercosul_missing_digit_invalid(self):
        result = validate_plate("BRA2E1")
        self.assertFalse(result.valid)

    def test_mercosul_letter_in_digit_slot_invalid(self):
        result = validate_plate("BRAAE19")
        self.assertFalse(result.valid)

    def test_special_character_invalid(self):
        result = validate_plate("A@A-1234")
        self.assertFalse(result.valid)

    def test_internal_space_invalid(self):
        result = validate_plate("ABC 1234")
        self.assertFalse(result.valid)
        self.assertIn("Nao use espacos internos", result.errors)

    def test_trim_spaces(self):
        result = validate_plate("  ABC-1234  ")
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "ABC-1234")

    def test_longer_than_allowed_invalid(self):
        result = validate_plate("ABCD-12345")
        self.assertFalse(result.valid)

    def test_empty_invalid(self):
        result = validate_plate("")
        self.assertFalse(result.valid)
        self.assertIn("Placa obrigatoria", result.errors)

    def test_lowercase_is_converted(self):
        result = validate_plate("abc-1234")
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "ABC-1234")

    def test_only_letters_invalid(self):
        result = validate_plate("ABCDEFG")
        self.assertFalse(result.valid)

    def test_only_numbers_invalid(self):
        result = validate_plate("1234567")
        self.assertFalse(result.valid)

    def test_hyphen_wrong_position_invalid(self):
        result = validate_plate("AB-C1234")
        self.assertFalse(result.valid)

    def test_partial_plate_invalid(self):
        result = validate_plate("AB-123")
        self.assertFalse(result.valid)

    def test_trailing_space_invalid(self):
        result = validate_plate("ABC-1234 ")
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "ABC-1234")

    def test_boolean_helper(self):
        self.assertTrue(is_valid_plate("ABC-1234"))
        self.assertTrue(is_valid_plate("ABC1234"))

    def test_numeric_in_letter_slot_invalid(self):
        result = validate_plate("12A-1234")
        self.assertFalse(result.valid)

    def test_non_ascii_invalid(self):
        result = validate_plate("ÃBC-1234")
        self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()

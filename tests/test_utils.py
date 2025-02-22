import unittest
from datetime import datetime, timedelta
from src.utils.time import format_timestamp, parse_duration, utc_now, time_since
from src.utils.validation import validate_price, validate_quantity, sanitize_string
from src.utils.security import generate_password_hash, check_password_hash, generate_token
from src.utils.utility_functions import (
    some_utility_function,
    format_price,
    validate_input,
    process_item_data
)

class UtilsTestCase(unittest.TestCase):
    """
    Test case for utility functions.
    """
    def test_some_utility_function(self):
        """
        Test some utility function.

        Asserts:
            The utility function returns the expected result.
        """
        result = some_utility_function('input_value')
        self.assertEqual(result, 'processed_input_value')

class TestTimeUtils(unittest.TestCase):
    def test_format_timestamp(self):
        dt = datetime(2024, 2, 17, 12, 0, 0)
        self.assertEqual(format_timestamp(dt), "2024-02-17T12:00:00")

    def test_parse_duration(self):
        self.assertEqual(parse_duration("1h"), timedelta(hours=1))
        self.assertEqual(parse_duration("30m"), timedelta(minutes=30))
        self.assertEqual(parse_duration("24h"), timedelta(days=1))
        with self.assertRaises(ValueError):
            parse_duration("invalid")

    def test_utc_now(self):
        now = utc_now()
        self.assertIsInstance(now, datetime)
        self.assertEqual(now.tzinfo, None)  # Should be naive UTC

    def test_time_since(self):
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        self.assertEqual(time_since(hour_ago), "1 hour ago")
        day_ago = now - timedelta(days=1)
        self.assertEqual(time_since(day_ago), "1 day ago")

class TestValidationUtils(unittest.TestCase):
    def test_validate_price(self):
        self.assertTrue(validate_price(1000))
        self.assertTrue(validate_price("1000"))
        with self.assertRaises(ValueError):
            validate_price(-100)
        with self.assertRaises(ValueError):
            validate_price("invalid")

    def test_validate_quantity(self):
        self.assertTrue(validate_quantity(5))
        self.assertTrue(validate_quantity("5"))
        with self.assertRaises(ValueError):
            validate_quantity(-1)
        with self.assertRaises(ValueError):
            validate_quantity("invalid")

    def test_sanitize_string(self):
        self.assertEqual(sanitize_string("Test String!"), "Test String!")
        self.assertEqual(sanitize_string("<script>alert('xss')</script>"), "alert('xss')")
        self.assertEqual(sanitize_string("  spaces  "), "spaces")

class TestSecurityUtils(unittest.TestCase):
    def test_password_hashing(self):
        password = "test_password"
        hashed = generate_password_hash(password)
        self.assertTrue(check_password_hash(hashed, password))
        self.assertFalse(check_password_hash(hashed, "wrong_password"))

    def test_token_generation(self):
        token = generate_token()
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 32)  # Should be reasonably long
        
        # Test uniqueness
        another_token = generate_token()
        self.assertNotEqual(token, another_token)

if __name__ == '__main__':
    unittest.main()

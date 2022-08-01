import unittest
import functools
from datetime import datetime

import api


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)

        return wrapper

    return decorator


class TestCharField(unittest.TestCase):

    @cases(['abc', ''])
    def test_valid_char_field(self, value):
        self.assertEqual(value, api.CharField().validate(value))

    @cases([0, 1000, -1, {},{'abc'}, [], ['abc'],datetime.today().date()])
    def test_invalid_char_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.CharField().validate(value)

class TestArgumentsField(unittest.TestCase):

    @cases([{}, {'key':'value'},{'key':None}])
    def test_valid_arg_field(self, value):
        self.assertEqual(value, api.ArgumentsField().validate(value))

    @cases([0, 1000, -1, 'abc', [], ['abc'],datetime.today().date()])
    def test_invalid_arg_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.ArgumentsField().validate(value)

class TestEmailField(unittest.TestCase):

    @cases(['user@otus.ru'])
    def test_valid_email_field(self, value):
        self.assertEqual(value, api.EmailField().validate(value))

    @cases(['user', '', 'user@', '@'])
    def test_invalid__email_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.EmailField().validate(value)

class TestPhoneField(unittest.TestCase):

    @cases([71234567890,'79876543210'])
    def test_valid_phone_field(self, value):
        self.assertEqual(value, api.PhoneField().validate(value))

    @cases(['12345678901',12345678901, 7123456789, '7123456789',
            '798765.4321','7123a456789','abc', -1, 7123456789, 777])
    def test_invalid_phone_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.PhoneField().validate(value)

class TestDateField(unittest.TestCase):

    @cases(['01.02.2003', '01.02.2003'])
    def test_valid_date_field(self, value):
        self.assertEqual(value, api.DateField().validate(value))

    @cases([datetime.today().date(), '01/02/2003', '32.02.2003',
            '01.14.2003', '00.00.2003', '01.02.0000', '01022003'])
    def test_invalid_date_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.DateField().validate(value)

class TestBirthDayField(unittest.TestCase):

    @cases(['01.02.2003', '01.02.2003'])
    def test_valid_birth_day_field(self, value):
        self.assertEqual(value, api.BirthDayField().validate(value))

    @cases([datetime.today().date(), '01/02/2003', '32.02.2003',
            '01.14.2003', '00.00.2003', '01.02.0000', '01022003'])
    def test_invalid_birth_day_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.BirthDayField().validate(value)

    @cases(['01.01.1951'])
    def test_invalid_age_for_birth_day_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.BirthDayField().validate(value)


class TestGenderField(unittest.TestCase):

    @cases([0,1,2])
    def test_valid_gender_field(self, value):
        self.assertEqual(value, api.GenderField().validate(value))

    @cases([1000, -1, 3, 'abc'])
    def test_invalid_gender_field(self, value):
        with self.assertRaises(api.ValidationError):
            api.GenderField().validate(value)

class TestClientIDsField(unittest.TestCase):

    @cases([[1,2,3],[1000]])
    def test_valid_gender_field(self, value):
        self.assertEqual(value, api.ClientIDsField().validate(value))

    @cases([1000, -1, 3, 'abc',{1:2}])
    def test_invalid_gender_field_not_list(self, value):
        with self.assertRaises(api.ValidationError):
            api.ClientIDsField().validate(value)

    @cases([[1,'a'], ['abc'], [2,{1: 2}]])
    def test_invalid_gender_field_not_int(self, value):
        with self.assertRaises(api.ValidationError):
            api.ClientIDsField().validate(value)

if __name__ == "__main__":
    unittest.main()

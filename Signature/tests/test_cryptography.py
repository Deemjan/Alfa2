from django.test import TestCase

from Signature.services import _date_is_valid


class CryptographyDateTestCase(TestCase):
    def _date_is_valid_test(self):
        result = _date_is_valid
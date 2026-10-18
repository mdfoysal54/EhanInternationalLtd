from django.test import SimpleTestCase
from .adapters import NormalizedAttendance
class AdapterTests(SimpleTestCase):
    def test_event_contract(self):
        self.assertEqual(NormalizedAttendance.__dataclass_fields__['external_id'].name,'external_id')
        
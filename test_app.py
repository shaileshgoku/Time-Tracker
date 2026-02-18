import unittest
import json
from app import app, parse_time
from datetime import datetime, timedelta

class TimeTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_calculate_multiple_intervals(self):
        # 1:10 pm - 1:20 pm (10 mins)
        # 1:40 pm - 1:50 pm (10 mins)
        # Total: 20 mins
        payload = {
            'intervals': [
                {'start': '1:10 pm', 'end': '1:20 pm'},
                {'start': '1:40 pm', 'end': '1:50 pm'}
            ]
        }
        response = self.app.post('/calculate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['hours'], 0)
        self.assertEqual(data['minutes'], 20)
        self.assertEqual(data['result'], "20 minutes")

    def test_calculate_single_interval_in_list(self):
        payload = {
            'intervals': [
                {'start': '10:00 am', 'end': '11:00 am'}
            ]
        }
        response = self.app.post('/calculate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['hours'], 1)
        self.assertEqual(data['minutes'], 0)

    def test_calculate_mixed_intervals(self):
        # 9:00 am - 12:00 pm (3h)
        # 1:00 pm - 2:30 pm (1h 30m)
        # Total: 4h 30m
        payload = {
            'intervals': [
                {'start': '9:00 am', 'end': '12:00 pm'},
                {'start': '1:00 pm', 'end': '2:30 pm'}
            ]
        }
        response = self.app.post('/calculate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['hours'], 4)
        self.assertEqual(data['minutes'], 30)

    def test_missing_input_list(self):
        response = self.app.post('/calculate', 
                                 data=json.dumps({'intervals': []}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

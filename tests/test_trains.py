from tests.base_case import BaseCase

import unittest

class AuthTest(BaseCase):

    def test_add_train(self):
        data = {
            "train_number": "12426",
            "train_name": "Rajdhani Express",
            "source": "JAMMU TAWI",
            "destination": "NEW DELHI",
            "time_": "19:40",
            "price": 1550.0,
            "seats_available": 22
        }

        res = self.testapp.post_json('/api/v1/add/train', params=data)

        self.assertEqual(res.json['status'], 200)

    def test_all_train(self):
        
        res = self.testapp.get('/api/v1/trains/?slug=12426')
        self.assertEqual(res.json['status'], 200)

    def test_specific_train(self):
        
        res = self.testapp.get('/api/v1/train/1')
        self.assertEqual(res.json['status'], 200)
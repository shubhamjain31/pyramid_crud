from tests.base_case import BaseCase

import unittest

class AuthTest(BaseCase):

    def test_login(self):
        data = {"username": "shubham31", "password": "admin@1234"}

        res = self.testapp.post_json('/api/v1/accounts/login', params=data)

        self.token = res.json['data']['token']
        self.assertEqual(res.json['status'], 200)

    def test_register(self):
        data = {
                "username": "test12",
                "password": "test@1234",
                "name": "Test",
                "email": "test@email.com",
                "phone": "9876543210",
                "role": ""
            }
        
        res = self.testapp.post_json('/api/v1/account/register', params=data)
        self.assertEqual(res.json['status'], 201)

    def test_logout(self):
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGVtYWlsLmNvbSIsImV4cGlyZXMiOjE2OTIzNTI4MDYuMTczMzQwMywic3ViIjoxLCJpYXQiOjE2OTIzNDkyMDZ9.4HDadNa3eCEML1ZYIioQYFKco3Ph77p-92sQ4FApJyk"}

        res = self.testapp.get('/api/v1/accounts/logout', headers=headers)
        self.assertEqual(res.json['status'], 200)
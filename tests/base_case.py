import unittest
from pyramid import testing
from webtest import TestApp

settings = {}
settings["core.secret"]     = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
settings["core.algorithm"]  = "HS256"
settings["sqlalchemy.url"]  = "postgresql://crud_pyramid_user:root@localhost:5432/crud_pyramid_db"

class BaseCase(unittest.TestCase):
    def setUp(self):
        from core import main

        self.app = main({}, **settings)
        self.testapp = TestApp(self.app)
        self.testapp.authorization = ('Bearer', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGVtYWlsLmNvbSIsImV4cGlyZXMiOjE2OTIzNTg1MzAuMDc3NDkzNywic3ViIjoxLCJpYXQiOjE2OTIzNTQ5MzB9.1hwhUuT6vfTejXvK-VMIyUk5i2vF8le8YfXKfi3gsIo')

    def tearDown(self):
        testing.tearDown()
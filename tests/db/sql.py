from db_plugins.db.sql import *
from db_plugins.db.sql.models import *
import tempfile
import unittest
import pytest
import json
import requests

import os
import sys

FILE_PATH = os.path.dirname(os.path.abspath(os.curdir))
print (FILE_PATH)
sys.path.append(FILE_PATH + "/ztf-api-apf")

from api import app, db

def init():
    db_fd, temp = tempfile.mkstemp()
    app.config["DATABASE"]["SQL"] = "sqlite:///"+temp
    app.config["TESTING"] = True
    client = app.test_client()
    print(app.config["DATABASE"]["SQL"])
    # db.init_db()
    return db_fd, temp, client


class ClassTest(unittest.TestCase):

   def setUp(self):
       pass
       

   def tearDown(self):
       pass

   def test_get(self):
       pass

   def test_get_list(self):
       pass


class TaxonomyTest(unittest.TestCase):

    def setUp(self):
       pass 

    def tearDown(self):
       pass 

    def test_get(self):
       pass 

    def test_get_list(self):
        pass


class ClassifierTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass  

    def test_get(self):
        pass

    def test_get_list(self):
        pass


class XMatchTest(unittest.TestCase):
    pass


class MagnitudeStatisticsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get(self):
        pass
    def test_get_list(self):
        pass

class ClassificationTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_get(self):
        pass
    def test_get_list(self):
        pass

class AstroObjectTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_get(self):
        pass
    def test_get_list(self):
        pass

    def test_get_query(self):
        pass

class FeaturesObjectTest(unittest.TestCase):

    def setUp(self):
       pass
    def tearDown(self):
        pass
    def test_get(self):
        pass
    def test_get_list(self):
        pass


class DetectionTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_get(self):
        pass
    def test_get_list(self):
        pass

class NonDetectionTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get(self):
        pass
    def test_get_list(self):
        pass

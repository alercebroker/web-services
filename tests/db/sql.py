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


#class ClassTest(unittest.TestCase):

#    def setUp(self):
#        self.fd, self.temp, self.client = init()
#        model = Class(name="SN")
#        db.session.add(model)
#        db.session.commit()

#    def tearDown(self):
#        os.close(self.fd)
#        os.unlink(self.temp)

#    def test_get(self):
#        instance = self.client.get("/class/Ceph")
#        self.assertEqual(instance.status_code, 200)

#    def test_get_list(self):
#        instance = self.client.get("/class")
#        self.assertEqual(instance.status_code, 200)


# class TaxonomyTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = Taxonomy(name="test")
#         class_object = Class(name="SN")
#         self.model.classes.append(class_object)
#         classifier = Classifier(name="asdasd")
#         self.model.classifiers.append(classifier)
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/taxonomy/LateClassificationV1")
#         #taxonomy = {'name': 'test'}
#         #self.assertEqual(instance.json, taxonomy)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/taxonomy")
#         self.assertEqual(instance.status_code, 200)


# class ClassifierTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = Classifier(name="Late Classifier")
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/class/Ceph")
#         #classifier = {'name': 'Late Classifier'}
#         #self.assertEqual(instance.json, classifier)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/class")
#         self.assertEqual(instance.status_code, 200)


# class XMatchTest(unittest.TestCase):
#     pass


# class MagnitudeStatisticsTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = MagnitudeStatistics()
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/magnitude_statistics")
#         #magnitude = {}
#         #self.assertEqual(instance.json, magnitude)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/magnitude_statistics")
#         self.assertEqual(instance.status_code, 200)


# class ClassificationTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = Classification()
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/classification")
#         #classification = {}
#         #self.assertEqual(instance.json, classification)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/classification")
#         self.assertEqual(instance.status_code, 200)


class AstroObjectTest(unittest.TestCase):

    def setUp(self):
        self.fd, self.temp, self.client = init()
        #model = AstroObject(oid="ZTF1", nobs=1, lastmjd=1.0, meanra=1.0,
        #                          meandec=1.0, sigmara=1.0, sigmadec=1.0, deltajd=1.0, firstmjd=1.0)
        #db.session.add(model)
        #db.session.commit()

    def tearDown(self):
        os.close(self.fd)
        os.unlink(self.temp)

#     def test_get(self):
#         instance = client.get("/astro_objects/ZTF19adamfha")
#         #object = {'oid': 'ZTF1', 'nobs': 1, 'lastmjd': 1.0, 'meanra': 1.0, 'meandec': 1.0, 'sigmara': 1.0,
#         #                'sigmadec': 1.0, 'deltajd': 1.0, 'firstmjd': 1.0}
#         #self.assertEqual(instance.json, object)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/astro_objects")
#         self.assertEqual(instance.status_code, 200)

    def test_get_query(self):
        instance = self.client.get("/astro_objects_query")
        print ("---------ESTO----------")
        print (instance.json)
        self.assertEqual(instance.status_code, 200)


# class FeaturesObjectTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = FeaturesObject()
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/features_object/ZTF18abcdbsx")
#         #features_object = {}
#         #self.assertEqual(instance.json, features_object)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/features_object")
#         self.assertEqual(instance.status_code, 200)


# class DetectionTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = Detection()
#         self.session.add(self.model)
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/detection")
#         #detection = {}
#         #self.assertEqual(instance.json, detection)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/detection")
#         print (instance.json)
#         self.assertEqual(instance.status_code, 200)


# """
# class NonDetectionTest(unittest.TestCase):

#     def setUp(self):
#         self.connection = engine.connect()
#         self.trans = self.connection.begin()
#         self.session = Session(bind=self.connection)
#         self.model = NonDetection()
#         self.session.commit()

#     def tearDown(self):
#         self.session.close()
#         self.trans.rollback()
#         self.connection.close()

#     def test_get(self):
#         instance = client.get("/non_detection")
#         #non_detection = {}
#         #self.assertEqual(instance.json, non_detection)
#         self.assertEqual(instance.status_code, 200)

#     def test_get_list(self):
#         instance = client.get("/non_detection")
#         print (instance.json)
#         self.assertEqual(instance.status_code, 200)
#

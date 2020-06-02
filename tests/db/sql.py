from db_plugins.db.sql import *
from db_plugins.db.sql.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
import json
import requests

import os
import sys

FILE_PATH = os.path.dirname(os.path.abspath(os.curdir))
print (FILE_PATH)
sys.path.append(FILE_PATH)

from api import app
from api.sql.resources.AstroObject import *
from api.sql.resources.Class import *
from api.sql.resources.Classification import *
from api.sql.resources.Classifier import *
from api.sql.resources.Detection import *
from api.sql.resources.FeaturesObject import *
from api.sql.resources.MagnitudeStatistics import *
from api.sql.resources.NonDetection import *
from api.sql.resources.Taxonomy import *


engine = create_engine('sqlite:///:memory:')
Session = sessionmaker()
Base.metadata.create_all(engine)

url = "http://localhost:8085/"

TEST_DB = 'test.db'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' + \
            os.path.join(basedir, TEST_DB)
client = app.test_client()

class SQLMethodsTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        class_object = Class()
        self.session.add(class_object)
        taxonomy = Taxonomy()
        self.session.add(taxonomy)
        classifier = Classifier()
        self.session.add(classifier)
        xmatch = Xmatch()
        self.session.add(xmatch)
        magnitude_statistics = MagnitudeStatistics()
        self.session.add(magnitude_statistics)
        classification = Classification()
        self.session.add(classification)
        astro_object = AstroObject()
        self.session.add(astro_object)
        features_object = FeaturesObject()
        self.session.add(features_object)
        detection = Detection()
        self.session.add(detection)
        non_detection = NonDetection()
        self.session.add(non_detection)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()


class ClassTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Class(name="Super Nova", acronym="SN")
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    """
    def test_post(self):
        instance = client.post("/class/Ceph")
        self.assertEqual(instance.status_code, 200)
    """

    def test_get(self):
        #client.post("/class/Ceph")
        instance = client.get("/class/Ceph")
        #class_object = {'name': 'Super Nova', 'acronym': "SN"}
        #self.assertEqual(instance.json, class_object)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/class")
        self.assertEqual(instance.status_code, 200)


class TaxonomyTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Taxonomy(name="test")
        class_object = Class(name="SN")
        self.model.classes.append(class_object)
        classifier = Classifier(name="asdasd")
        self.model.classifiers.append(classifier)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/taxonomy/LateClassificationV1")
        #taxonomy = {'name': 'test'}
        #self.assertEqual(instance.json, taxonomy)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/taxonomy")
        self.assertEqual(instance.status_code, 200)


class ClassifierTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Classifier(name="Late Classifier")
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/class/Ceph")
        #classifier = {'name': 'Late Classifier'}
        #self.assertEqual(instance.json, classifier)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/class")
        self.assertEqual(instance.status_code, 200)


class XMatchTest(unittest.TestCase):
    pass


class MagnitudeStatisticsTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = MagnitudeStatistics()
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/magnitude_statistics")
        #magnitude = {}
        #self.assertEqual(instance.json, magnitude)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/magnitude_statistics")
        self.assertEqual(instance.status_code, 200)


class ClassificationTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Classification()
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/classification")
        #classification = {}
        #self.assertEqual(instance.json, classification)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/classification")
        self.assertEqual(instance.status_code, 200)


class AstroObjectTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = AstroObject(oid="ZTF1", nobs=1, lastmjd=1.0, meanra=1.0,
                                 meandec=1.0, sigmara=1.0, sigmadec=1.0, deltajd=1.0, firstmjd=1.0)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/astro_objects/ZTF19adamfha")
        #object = {'oid': 'ZTF1', 'nobs': 1, 'lastmjd': 1.0, 'meanra': 1.0, 'meandec': 1.0, 'sigmara': 1.0,
        #                'sigmadec': 1.0, 'deltajd': 1.0, 'firstmjd': 1.0}
        #self.assertEqual(instance.json, object)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/astro_objects")
        self.assertEqual(instance.status_code, 200)


class FeaturesObjectTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = FeaturesObject()
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/features_object/ZTF18abcdbsx")
        #features_object = {}
        #self.assertEqual(instance.json, features_object)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/features_object")
        self.assertEqual(instance.status_code, 200)


"""
class DetectionTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Detection()
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/detection")
        #detection = {}
        #self.assertEqual(instance.json, detection)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/detection")
        print (instance.json)
        self.assertEqual(instance.status_code, 200)


class NonDetectionTest(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = NonDetection()
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = client.get("/non_detection")
        #non_detection = {}
        #self.assertEqual(instance.json, non_detection)
        self.assertEqual(instance.status_code, 200)

    def test_get_list(self):
        instance = client.get("/non_detection")
        print (instance.json)
        self.assertEqual(instance.status_code, 200)
"""
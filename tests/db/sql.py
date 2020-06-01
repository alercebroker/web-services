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

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(TEST_DB)
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

    def test_get(self):
        instance = client.get("/class/Ceph")
        self.assertIsInstance(instance, Class)

    def test_get_list(self):
        instance = client.get("/class")
        self.assertIsInstance(instance, Class)
        """
        instances = client.get("/class")
        for i in instances:
            self.assertIsInstance(i, Class)
        """

"""
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
        instance = requests.get(url + "/taxonomy/test")
        self.assertIsInstance(instance, Taxonomy)
    def test_get_list(self):
        instances = requests.get(url + "/taxonomy")
        for i in instances:
            self.assertIsInstance(i, Taxonomy)
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
        instance = requests.get(url + "/classifier/Late Classifier")
        self.assertIsInstance(instance, Classifier)
    def test_get_list(self):
        instances = requests.get(url + "/classifier")
        for i in instances:
            self.assertIsInstance(i, Classifier)
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
        instance = requests.get(url + "/magnitude_statistics")
        self.assertIsInstance(instance, MagnitudeStatistics)
    def test_get_list(self):
        instances = requests.get(url + "/magnitude_statistics")
        for i in instances:
            self.assertIsInstance(i, MagnitudeStatistics)
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
        instance = requests.get(url + "/classification")
        self.assertIsInstance(instance, Classification)
    def test_get_list(self):
        instances = requests.get(url + "/classification")
        for i in instances:
            self.assertIsInstance(i, Classification)
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
        instance = requests.get(url + "/astro_object/ZTF1")
        self.assertIsInstance(instance, AstroObject)
    def test_get_list(self):
        instances = requests.get(url + "/astro_object")
        for i in instances:
            self.assertIsInstance(i, AstroObject)
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
        instance = requests.get(url + "/features_object")
        self.assertIsInstance(instance, FeaturesObject)
    def test_get_list(self):
        instances = requests.get(url + "/features_object")
        for i in instances:
            self.assertIsInstance(i, FeaturesObject)
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
        instance = requests.get(url + "/detection")
        self.assertIsInstance(instance, Detection)
    def test_get_list(self):
        instances = requests.get(url + "/detection")
        for i in instances:
            self.assertIsInstance(i, Detection)
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
        instance = requests.get(url + "/non_detection")
        self.assertIsInstance(instance, NonDetection)
    def test_get_list(self):
        instances = requests.get(url + "/non_detection")
        for i in instances:
            self.assertIsInstance(i, NonDetection)
"""
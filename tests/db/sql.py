from .core import *
from apf.db.sql import *
from apf.db.sql.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
import json
import requests

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker()
Base.metadata.create_all(engine)


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


class ClassTest(unittest.TestCase, GenericClassTest):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Class(name="Super Nova", acronym="SN")
        astro_object = AstroObject(oid="ZTF1", nobs=1, lastmjd=1.0,
                                   meanra=1.0, meandec=1.0, sigmadec=1.0, deltajd=1.0, firstmjd=1.0)
        classifier = Classifier(name="test")
        classification = Classification(
            astro_object="ZTF1", classifier_name="test", class_name="SN")
        self.model.classifications.append(classification)
        self.session.add(astro_object)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = requests.get(engine + "/class/Super Nova")
        self.assertIsInstance(instance, Class)

    def test_get_list(self):
        instances = requests.get(engine + "/class")
        for i in instances:
            self.assertIsInstance(i, Class)


class TaxonomyTest(GenericTaxonomyTest, unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Taxonomy(name="test")
        class_ = Class(name="SN")
        classifier = Classifier(name="asdasd")
        self.model.classifiers.append(classifier)
        self.model.classes.append(class_)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = requests.get(engine + "/taxonomy/test")
        self.assertIsInstance(instance, Taxonomy)

    def test_get_list(self):
        instances = requests.get(engine + "/taxonomy")
        for i in instances:
            self.assertIsInstance(i, Taxonomy)

class ClassifierTest(GenericClassifierTest, unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        self.model = Classifier(name="Late Classifier")
        astro_object = AstroObject(oid="ZTF1", nobs=1, lastmjd=1.0,
                                   meanra=1.0, meandec=1.0, sigmadec=1.0, deltajd=1.0, firstmjd=1.0)
        classifier = Classifier(name="test")
        class_ = Class(name="SN")
        classification = Classification(
            astro_object="ZTF1", classifier_name="test", class_name="SN")
        self.model.classifications.append(classification)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = requests.get(engine + "/classifier/Late Classifier")
        self.assertIsInstance(instance, Classifier)

    def test_get_list(self):
        instances = requests.get(engine + "/classifier")
        for i in instances:
            self.assertIsInstance(i, Classifier)


class XMatchTest(GenericXMatchTest, unittest.TestCase):
    pass


class MagnitudeStatisticsTest(GenericMagnitudeStatisticsTest, unittest.TestCase):

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
        instance = requests.get(engine + "/magnitude_statistics")
        self.assertIsInstance(instance, MagnitudeStatistics)

    def test_get_list(self):
        instances = requests.get(engine + "/magnitude_statistics")
        for i in instances:
            self.assertIsInstance(i, MagnitudeStatistics)


class ClassificationTest(GenericClassificationTest, unittest.TestCase):

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
        instance = requests.get(engine + "/classification")
        self.assertIsInstance(instance, Classification)

    def test_get_list(self):
        instances = requests.get(engine + "/classification")
        for i in instances:
            self.assertIsInstance(i, Classification)


class AstroObjectTest(GenericAstroObjectTest, unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)

        class_ = Class(name="Super Nova", acronym="SN")
        taxonomy = Taxonomy(name="Test")
        class_.taxonomies.append(taxonomy)
        classifier = Classifier(name="C1")
        taxonomy.classifiers.append(classifier)
        self.model = AstroObject(oid="ZTF1", nobs=1, lastmjd=1.0, meanra=1.0,
                                 meandec=1.0, sigmara=1.0, sigmadec=1.0, deltajd=1.0, firstmjd=1.0)
        self.model.xmatches.append(
            Xmatch(catalog_id="C1", catalog_object_id="O1"))
        self.model.magnitude_statistics = MagnitudeStatistics(
            fid=1, magnitude_type="psf", mean=1.0, median=1.0, max_mag=1.0, min_mag=1.0, sigma=1.0, last=1.0, first=1.0)
        self.model.classifications.append(Classification(
            class_name="Super Nova", probability=1.0, classifier_name="C1"))

        features_object = FeaturesObject(data=json.loads('{"test":"test"}'))
        features_object.features = Features(version="V1")
        self.model.features.append(features_object)
        self.model.detections.append(Detection(candid="t", mjd=1, fid=1, ra=1, dec=1, rb=1,
                                               magap=1, magpsf=1, sigmapsf=1, sigmagap=1,
                                               alert=json.loads('{"test":"test"}')))
        self.model.non_detections.append(
            NonDetection(mjd=1, fid=1, diffmaglim=1))

        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def test_get(self):
        instance = requests.get(engine + "/astro_object/ZTF1")
        self.assertIsInstance(instance, AstroObject)

    def test_get_list(self):
        instances = requests.get(engine + "/astro_object")
        for i in instances:
            self.assertIsInstance(i, AstroObject)


class FeaturesObjectTest(GenericFeaturesTest, unittest.TestCase):

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
        instance = requests.get(engine + "/features_object")
        self.assertIsInstance(instance, FeaturesObject)

    def test_get_list(self):
        instances = requests.get(engine + "/features_object")
        for i in instances:
            self.assertIsInstance(i, FeaturesObject)


class DetectionTest(GenericDetectionTest, unittest.TestCase):

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
        instance = requests.get(engine + "/detection")
        self.assertIsInstance(instance, Detection)

    def test_get_list(self):
        instances = requests.get(engine + "/detection")
        for i in instances:
            self.assertIsInstance(i, Detection)


class NonDetectionTest(GenericNonDetectionTest, unittest.TestCase):

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
        instance = requests.get(engine + "/non_detection")
        self.assertIsInstance(instance, NonDetection)

    def test_get_list(self):
        instances = requests.get(engine + "/non_detection")
        for i in instances:
            self.assertIsInstance(i, NonDetection)
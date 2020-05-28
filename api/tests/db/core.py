class GenericClassTest():
    model = None

    def test_get_taxonomies(self):
        taxonomies = self.model.get_taxonomies()
        self.assertIsInstance(taxonomies, list)

    def test_get_classifications(self):
        classifications = self.model.get_classifications()
        self.assertIsInstance(classifications, list)
        self.assertEqual(len(classifications), 1)



class GenericTaxonomyTest():
    model = None

    def test_get_classes(self):
        classes = self.model.get_classes()
        self.assertIsInstance(classes, list)
        self.assertEqual(len(classes), 1)

    def test_get_classifiers(self):
        classifiers = self.model.get_classifiers()
        self.assertIsInstance(classifiers, list)
        self.assertEqual(len(classifiers), 1)


class GenericClassifierTest():
    model = None
    
    def test_get_classifications(self):
        classifications = self.model.get_classifications()
        self.assertIsInstance(classifications, list)
        self.assertEqual(len(classifications), 1)


class GenericXMatchTest():
    pass


class GenericMagnitudeStatisticsTest():
    pass


class GenericClassificationTest():
    pass


class GenericAstroObjectTest():
    model = None

    def test_get_xmatches(self):
        xmatches = self.model.get_xmatches()
        self.assertEqual(len(xmatches),1)

    def test_get_magnitude_statistics(self):
        magstats = self.model.get_magnitude_statistics()
        self.assertEqual(magstats.fid, 1)

    def test_get_classifications(self):
        classes = self.model.get_classifications()
        self.assertEqual(len(classes), 1)

    def test_get_features(self):
        features = self.model.get_features()
        self.assertIsInstance(features, list)
        self.assertEqual(len(features), 1)

    def test_get_detections(self):
        detections = self.model.get_detections()
        self.assertIsInstance(detections, list)
        self.assertEqual(len(detections), 1)

    def test_get_non_detections(self):
        non_detections = self.model.get_non_detections()
        self.assertIsInstance(non_detections, list)
        self.assertEqual(len(non_detections), 1)

    def test_get_lightcurve(self):
        light_curve = self.model.get_lightcurve()
        self.assertIsInstance(light_curve, dict)
        self.assertTrue("detections" in light_curve)
        self.assertTrue("non_detections" in light_curve)
        self.assertIsInstance(light_curve["detections"], list)
        self.assertIsInstance(light_curve["non_detections"], list)


class GenericFeaturesTest():
    pass


class GenericNonDetectionTest():
    pass


class GenericDetectionTest():
    pass

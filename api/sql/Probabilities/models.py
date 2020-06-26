from flask_restx import Resource, fields, Model

class ProbabilitiesField(fields.Raw):
    def format(self, value):
        if isinstance(value, dict):
            return value

classification_model = Model("classification", {
    "classifier_name": fields.String(description="Classifier that did the classification"),
    "class_name": fields.String(description="Class with the highest probability"),
    "probability": fields.String(description="Highest probability"),
    "probabilities": ProbabilitiesField(description="Probabilities for all classes")
})
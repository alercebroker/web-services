from flask_restx import Resource, fields, Model


probability_model = Model(
    "probability",
    {
        "classifier_name": fields.String(
            description="Classifier that did the classification"
        ),
        "classifier_version": fields.String(description="Version of the classifier"),
        "class_name": fields.String(description="Class name"),
        "probability": fields.Float(description="Value of the probability for the class"),
        "ranking": fields.Integer(
            description="position of the probability against the others"
        ),
    },
)

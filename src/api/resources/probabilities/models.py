from flask_restx import fields, Model


probability = Model(
    "Probability",
    {
        "classifier_name": fields.String(
            description="Classifier that did the classification"
        ),
        "classifier_version": fields.String(
            description="Version of the classifier"
        ),
        "class_name": fields.String(description="Class name"),
        "probability": fields.Float(
            description="Value of the probability for the class"
        ),
        "ranking": fields.Integer(
            description="Position of the probability against the others"
        ),
    },
)

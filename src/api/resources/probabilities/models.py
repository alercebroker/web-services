from flask_restx import fields, Model


probability = Model(
    "Probability",
    {
        "classifier_name": fields.String(description="Classifier name"),
        "classifier_version": fields.String(description="Classifier version"),
        "class_name": fields.String(description="Class name"),
        "probability": fields.Float(
            description="Probability of belonging to the class"
        ),
        "ranking": fields.Integer(
            description="Position of the probability within classifier"
        ),
    },
)

from flask_restx import Resource, fields, Model

classifier_model = Model(
    "Classifier Model",
    {
        "classifier_name": fields.String(description="Classifier name", attribute="name"),
        # "taxonomy_name": fields.String(description="Taxonomy used by the classifier"),
    },
)

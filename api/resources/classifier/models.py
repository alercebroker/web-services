from flask_restx import Resource, fields, Model

classifier_model = Model(
    "Classifier Model",
    {
        "classifier_name": fields.String(
            description="Classifier name", attribute="classifier_name"
        ),
        "classifier_version": fields.String(
            description="Classifier Version", attribute="classifier_version"
        ),
        "classes": fields.List(
            fields.String(description="Class Name"), attribute="classes"
        ),
    },
)

class_model = Model("Class", {"name": fields.String()})

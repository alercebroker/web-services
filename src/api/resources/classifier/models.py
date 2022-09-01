from flask_restx import fields, Model

classifiers = Model(
    "Classifier Model",
    {
        "classifier_name": fields.String(description="Classifier name"),
        "classifier_version": fields.String(description="Classifier version"),
        "classes": fields.List(fields.String(description="Class names")),
    },
)

classes = Model("Class", {"name": fields.String(description="Class name")})

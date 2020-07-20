from flask_restx import Resource, fields, Model

class_model = Model(
  "Class", 
  {
    "name": fields.String,
    "acronym": fields.String
  }
)
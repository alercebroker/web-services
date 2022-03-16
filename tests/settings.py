TESTING = True
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:postgres@localhost:5432/postgres"

DATABASE = {
  "SQL": {"SQLALCHEMY_DATABASE_URL": SQLALCHEMY_DATABASE_URL},
  "MONGO": {
    "HOST": "mongodb://localhost",
    "USER": "mongo",
    "PASSWORD": "mongo",
    "PORT": 27017, 
    "DATABASE": "database"
  },
  "APP_CONFIG": {
      "CONNECT_PSQL": True,
      "CONNECT_MONGO": True
  }
}

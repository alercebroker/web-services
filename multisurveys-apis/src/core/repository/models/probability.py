from sqlalchemy import (
    Column,
    Integer,
    String,
    Integer,
    ForeignKey,
    Float,
    Index,

)
from db_plugins.db.sql.models import Object


from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Probability(Base):
    __tablename__ = "probability"
    oid = Column(Integer, ForeignKey(Object.oid), primary_key=True)
    class_name = Column(String, primary_key=True)
    classifier_name = Column(String, primary_key=True)
    classifier_version = Column(String, primary_key=True)
    probability = Column(Float, nullable=False)
    ranking = Column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_probabilities_oid", "oid", postgresql_using="hash"),
        Index("ix_probabilities_probability", "probability", postgresql_using="btree"),
        Index("ix_probabilities_ranking", "ranking", postgresql_using="btree"),
        Index(
            "ix_classification_rank1",
            "ranking",
            postgresql_where=ranking == 1,
            postgresql_using="btree",
        ),
    )
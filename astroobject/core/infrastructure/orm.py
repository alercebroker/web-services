from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    ARRAY,
    Index,
)
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Object(Base):
    __tablename__ = "object"

    oid = Column(String, primary_key=True)
    ndethist = Column(Integer)
    ncovhist = Column(Integer)
    mjdstarthist = Column(Float(precision=53))
    mjdendhist = Column(Float(precision=53))
    corrected = Column(Boolean)
    stellar = Column(Boolean)
    ndet = Column(Integer)
    g_r_max = Column(Float)
    g_r_max_corr = Column(Float)
    g_r_mean = Column(Float)
    g_r_mean_corr = Column(Float)
    meanra = Column(Float(precision=53))
    meandec = Column(Float(precision=53))
    sigmara = Column(Float(precision=53))
    sigmadec = Column(Float(precision=53))
    deltajd = Column(Float(precision=53))
    firstmjd = Column(Float(precision=53))
    lastmjd = Column(Float(precision=53))
    step_id_corr = Column(String)
    diffpos = Column(Boolean)
    reference_change = Column(Boolean)

    __table_args__ = (
        Index("ix_object_ndet", "ndet", postgresql_using="btree"),
        Index("ix_object_firstmjd", "firstmjd", postgresql_using="btree"),
        Index("ix_object_g_r_max", "g_r_max", postgresql_using="btree"),
        Index("ix_object_g_r_mean_corr", "g_r_mean_corr", postgresql_using="btree"),
        Index("ix_object_meanra", "meanra", postgresql_using="btree"),
        Index("ix_object_meandec", "meandec", postgresql_using="btree"),
    )

    def __repr__(self):
        return "<Object(oid='%s')>" % (self.oid)


class Taxonomy(Base):
    __tablename__ = "taxonomy"
    classifier_name = Column(String, primary_key=True)
    classifier_version = Column(String, primary_key=True)
    classes = Column(ARRAY(String), nullable=False)


class Probability(Base):
    __tablename__ = "probability"
    oid = Column(String, ForeignKey(Object.oid), primary_key=True)
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
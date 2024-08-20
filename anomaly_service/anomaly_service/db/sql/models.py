from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    ForeignKey,
    Float,
    Boolean,
    ARRAY,
    Index,
    UniqueConstraint,
    DateTime,
    JSON,
    ForeignKeyConstraint,
)

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.schema import PrimaryKeyConstraint


class Base(DeclarativeBase):
    pass


class Commons:
    def __getitem__(self, field):
        return self.__dict__[field]


class AnomalyScoreTop(Base):
    __tablename__ = "scores_top"

    oid = Column(String, primary_key=True)
    update_date = Column(DateTime, primary_key=False, server_default=func.now())
    created_date = Column(DateTime, primary_key=False, onupdate=func.now())
    score_trainsient = Column(Float, primary_key=False)
    score_stochastic = Column(Float, primary_key=False)
    score_periodic = Column(Float, primary_key=False)


class AnomalyScore(Base):
    __tablename__ = "scores"

    oid = Column(String, primary_key=True)
    update_date = Column(DateTime, primary_key=False, server_default=func.now())
    created_date = Column(DateTime, primary_key=False, onupdate=func.now())
    score_SNIa = Column(Float, primary_key=False)
    score_SNIbc = Column(Float, primary_key=False)
    score_SNII = Column(Float, primary_key=False)
    score_SNIIn = Column(Float, primary_key=False)
    score_SLSN = Column(Float, primary_key=False)
    score_TDE = Column(Float, primary_key=False)
    score_Microlensing = Column(Float, primary_key=False)
    score_QSO = Column(Float, primary_key=False)
    score_AGN = Column(Float, primary_key=False)
    score_Blazar = Column(Float, primary_key=False)
    score_YSO = Column(Float, primary_key=False)
    score_CVnova = Column(Float, primary_key=False)
    score_LPV = Column(Float, primary_key=False)
    score_EA = Column(Float, primary_key=False)
    score_EBEW = Column(Float, primary_key=False)
    score_PeriodicOther = Column(Float, primary_key=False)
    score_RSCVn = Column(Float, primary_key=False)
    score_CEP = Column(Float, primary_key=False)
    score_RLLab = Column(Float, primary_key=False)
    score_RLLc = Column(Float, primary_key=False)
    score_DSCT = Column(Float, primary_key=False)


class AnomalyDistributions(Base):
    __tablename__ = "distributions"

    name = Column(String, primary_key=True)
    category = Column(String, primary_key=True)
    value = Column(Float)
    update_date = Column(DateTime, primary_key=False, server_default=func.now())
    created_date = Column(DateTime, primary_key=False, onupdate=func.now())

    __table_args__ = PrimaryKeyConstraint("name", "category")

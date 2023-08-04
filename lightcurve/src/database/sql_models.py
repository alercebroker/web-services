from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Index,
    BigInteger,
    ForeignKey,
)
from .sql import Base


class Commons:
    def __getitem__(self, field):
        return self.__dict__[field]


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
        Index(
            "ix_object_g_r_mean_corr",
            "g_r_mean_corr",
            postgresql_using="btree",
        ),
        Index("ix_object_meanra", "meanra", postgresql_using="btree"),
        Index("ix_object_meandec", "meandec", postgresql_using="btree"),
    )


class Detection(Base, Commons):
    __tablename__ = "detection"

    candid = Column(BigInteger, primary_key=True)
    oid = Column(String, ForeignKey("object.oid"), primary_key=True)
    mjd = Column(Float(precision=53), nullable=False)
    fid = Column(Integer, nullable=False)
    pid = Column(Float, nullable=False)
    diffmaglim = Column(Float)
    isdiffpos = Column(Integer, nullable=False)
    nid = Column(Integer)
    ra = Column(Float(precision=53), nullable=False)
    dec = Column(Float(precision=53), nullable=False)
    magpsf = Column(Float, nullable=False)
    sigmapsf = Column(Float, nullable=False)
    magap = Column(Float)
    sigmagap = Column(Float)
    distnr = Column(Float)
    rb = Column(Float)
    rbversion = Column(String)
    drb = Column(Float)
    drbversion = Column(String)
    magapbig = Column(Float)
    sigmagapbig = Column(Float)
    rfid = Column(Integer)
    magpsf_corr = Column(Float)
    sigmapsf_corr = Column(Float)
    sigmapsf_corr_ext = Column(Float)
    corrected = Column(Boolean, nullable=False)
    dubious = Column(Boolean, nullable=False)
    parent_candid = Column(BigInteger)
    has_stamp = Column(Boolean, nullable=False)
    step_id_corr = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_ndetection_oid", "oid", postgresql_using="hash"),
    )


class NonDetection(Base, Commons):
    __tablename__ = "non_detection"

    oid = Column(String, ForeignKey("object.oid"), primary_key=True)
    fid = Column(Integer, primary_key=True)
    mjd = Column(Float(precision=53), primary_key=True)
    diffmaglim = Column(Float)
    __table_args__ = (
        Index("ix_non_detection_oid", "oid", postgresql_using="hash"),
    )


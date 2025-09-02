import datetime as dt
from enum import Enum
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime, Float,
    Enum as SAEnum, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine("sqlite:///glide.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Status(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"

class PeriodStatus(str, Enum):
    planned="planned"; open="open"; submitted="submitted"; approved="approved"; overdue="overdue"

class FrameworkLevel(str, Enum):
    output="output"; outcome="outcome"

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(SAEnum(Status), default=Status.planned)
    overhead_rate = Column(Float, default=0.15)
    revised_on = Column(DateTime, default=dt.datetime.utcnow)

    framework_nodes = relationship("FrameworkNode", back_populates="project", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="project", cascade="all, delete-orphan")
    periods = relationship("ReportingPeriod", back_populates="project", cascade="all, delete-orphan")

class FrameworkNode(Base):
    __tablename__ = "framework_node"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    level = Column(SAEnum(FrameworkLevel), nullable=False)
    parent_node_id = Column(Integer, ForeignKey("framework_node.id"))
    title = Column(String, nullable=False)
    project = relationship("Project", back_populates="framework_nodes")
    parent = relationship("FrameworkNode", remote_side=[id])
    indicators = relationship("Indicator", back_populates="framework_node", cascade="all, delete-orphan")

class Indicator(Base):
    __tablename__ = "indicator"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    framework_node_id = Column(Integer, ForeignKey("framework_node.id"), nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String)
    project = relationship("Project", back_populates="indicators")
    framework_node = relationship("FrameworkNode", back_populates="indicators")

class ReportingPeriod(Base):
    __tablename__ = "reporting_period"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    label = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    due_date = Column(Date)
    status = Column(SAEnum(PeriodStatus), default=PeriodStatus.open)
    project = relationship("Project", back_populates="periods")
    __table_args__ = (UniqueConstraint("project_id","label",name="uq_project_period"),)

def init_db():
    Base.metadata.create_all(bind=engine)

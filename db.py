# db.py
import datetime as dt
from enum import Enum

from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime, Float, Boolean,
    Enum as SAEnum, ForeignKey, UniqueConstraint, select
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ---------------------------------------------------------------------
# Engine / Session  (SQLite file in the project directory)
# To switch to Postgres later: create_engine("postgresql+psycopg2://user:pass@host/db")
# ---------------------------------------------------------------------
engine = create_engine("sqlite:///glide.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ---------------------------------------------------------------------
# Enums (match your Base44 JSON)
# ---------------------------------------------------------------------
class Status(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"

class PeriodStatus(str, Enum):
    planned  = "planned"
    open     = "open"
    submitted= "submitted"
    approved = "approved"
    overdue  = "overdue"

class FrameworkLevel(str, Enum):
    output  = "output"
    outcome = "outcome"

class Direction(str, Enum):
    increase = "increase"
    decrease = "decrease"

# ---------------------------------------------------------------------
# Models (1:1 with your Entities)
# ---------------------------------------------------------------------
class Project(Base):
    __tablename__ = "project"
    id           = Column(Integer, primary_key=True)
    title        = Column(String, nullable=False)                  # required
    description  = Column(String)                                  # optional
    start_date   = Column(Date,   nullable=False)                  # required
    end_date     = Column(Date,   nullable=False)                  # required
    status       = Column(SAEnum(Status), default=Status.planned, nullable=False)
    manager_user = Column(String, nullable=False)                  # required (email as text)
    funder       = Column(String, nullable=False)                  # required
    overhead_rate= Column(Float,  default=0.15, nullable=False)    # default 0.15
    notes        = Column(String)                                  # optional
    revised_on   = Column(Date, default=dt.date.today)             # JSON said "date"

    # Relationships
    framework_nodes = relationship("FrameworkNode", back_populates="project", cascade="all, delete-orphan")
    indicators      = relationship("Indicator",      back_populates="project", cascade="all, delete-orphan")
    periods         = relationship("ReportingPeriod",back_populates="project", cascade="all, delete-orphan")
    activities      = relationship("Activity",       back_populates="project", cascade="all, delete-orphan")
    budgets         = relationship("BudgetLine",     back_populates="project", cascade="all, delete-orphan")

class FrameworkNode(Base):
    __tablename__ = "framework_node"
    id             = Column(Integer, primary_key=True)
    project_id     = Column(Integer, ForeignKey("project.id"), nullable=False)   # required
    level          = Column(SAEnum(FrameworkLevel), nullable=False)              # required
    parent_node_id = Column(Integer, ForeignKey("framework_node.id"))
    title          = Column(String, nullable=False)                              # required
    description    = Column(String)
    sort_order     = Column(Integer, default=1)

    project  = relationship("Project", back_populates="framework_nodes")
    parent   = relationship("FrameworkNode", remote_side=[id])
    indicators = relationship("Indicator", back_populates="framework_node", cascade="all, delete-orphan")

class Indicator(Base):
    __tablename__ = "indicator"
    id                = Column(Integer, primary_key=True)
    project_id        = Column(Integer, ForeignKey("project.id"), nullable=False)          # required
    framework_node_id = Column(Integer, ForeignKey("framework_node.id"), nullable=False)   # required (usually output)
    name              = Column(String, nullable=False)                                     # required
    unit              = Column(String, nullable=False)                                     # required
    direction         = Column(SAEnum(Direction), nullable=False)                          # required
    requires_disaggregation = Column(Boolean, default=False, nullable=False)
    tags              = Column(String)

    project        = relationship("Project",      back_populates="indicators")
    framework_node = relationship("FrameworkNode",back_populates="indicators")
    targets        = relationship("IndicatorTarget", back_populates="indicator", cascade="all, delete-orphan")
    actuals        = relationship("IndicatorActual", back_populates="indicator", cascade="all, delete-orphan")

class ReportingPeriod(Base):
    __tablename__ = "reporting_period"
    id         = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)   # required
    label      = Column(String, nullable=False)                              # required (e.g., "Baseline", "Q1 2026")
    start_date = Column(Date,   nullable=False)                              # required
    end_date   = Column(Date,   nullable=False)                              # required
    due_date   = Column(Date,   nullable=False)                              # required (end + 15d)
    status     = Column(SAEnum(PeriodStatus), default=PeriodStatus.open, nullable=False)

    project = relationship("Project", back_populates="periods")
    __table_args__ = (UniqueConstraint("project_id", "label", name="uq_project_period_label"),)

class IndicatorTarget(Base):
    __tablename__ = "indicator_target"
    id           = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicator.id"),       nullable=False)
    period_id    = Column(Integer, ForeignKey("reporting_period.id"), nullable=False)
    target_value = Column(Float,  nullable=False, default=0.0)

    indicator = relationship("Indicator", back_populates="targets")
    __table_args__ = (UniqueConstraint("indicator_id", "period_id", name="uq_target_indicator_period"),)

class IndicatorActual(Base):
    __tablename__ = "indicator_actual"
    id           = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicator.id"),       nullable=False)
    period_id    = Column(Integer, ForeignKey("reporting_period.id"), nullable=False)
    actual_value = Column(Float,  nullable=False, default=0.0)
    qa_status    = Column(String, default="draft")   # draft|approved (MVP)

    indicator = relationship("Indicator", back_populates="actuals")
    __table_args__ = (UniqueConstraint("indicator_id", "period_id", name="uq_actual_indicator_period"),)

class Activity(Base):
    __tablename__ = "activity"
    id               = Column(Integer, primary_key=True)
    project_id       = Column(Integer, ForeignKey("project.id"),        nullable=False)  # required
    framework_node_id= Column(Integer, ForeignKey("framework_node.id"), nullable=False)  # required (output)
    title            = Column(String, nullable=False)                                     # required
    start_date       = Column(Date,   nullable=False)                                     # required
    end_date         = Column(Date,   nullable=False)                                     # required
    status           = Column(SAEnum(Status), default=Status.planned, nullable=False)
    owner_user       = Column(String, nullable=False)                                     # required

    project = relationship("Project", back_populates="activities")

class BudgetLine(Base):
    __tablename__ = "budget_line"
    id            = Column(Integer, primary_key=True)
    project_id    = Column(Integer, ForeignKey("project.id"), nullable=False)
    activity_id   = Column(Integer, ForeignKey("activity.id"), nullable=False)
    fiscal_year   = Column(String, nullable=False)
    planned_amount= Column(Float,  nullable=False, default=0.0)
    actual_amount = Column(Float,  nullable=False, default=0.0)

    project = relationship("Project", back_populates="budgets")

class StrategicIndicator(Base):
    __tablename__ = "strategic_indicator"
    id        = Column(Integer, primary_key=True)
    code      = Column(String, nullable=False, unique=True)  # required unique
    name      = Column(String, nullable=False)               # required
    unit      = Column(String, nullable=False)               # required
    direction = Column(SAEnum(Direction), nullable=False)    # required

class IndicatorMapping(Base):
    __tablename__ = "indicator_mapping"
    id                     = Column(Integer, primary_key=True)
    indicator_id           = Column(Integer, ForeignKey("indicator.id"),            nullable=False)
    strategic_indicator_id = Column(Integer, ForeignKey("strategic_indicator.id"), nullable=False)

# ---------------------------------------------------------------------
# Helpers (period generation, overdue marking, date overlap)
# ---------------------------------------------------------------------
def generate_reporting_periods(session, project: Project) -> None:
    """Create Baseline + quarterly periods overlapping project dates."""
    # Baseline
    exists = session.execute(
        select(ReportingPeriod).where(
            ReportingPeriod.project_id == project.id,
            ReportingPeriod.label == "Baseline"
        )
    ).scalar_one_or_none()
    if not exists:
        session.add(ReportingPeriod(
            project_id=project.id,
            label="Baseline",
            start_date=project.start_date,
            end_date=project.start_date,
            due_date=project.start_date + dt.timedelta(days=15),
            status=PeriodStatus.open
        ))

    # Quarterly periods (only if overlapping project duration)
    def last_day_of_month(year: int, month: int) -> int:
        # simple (OK for MVP): Feb = 28 (ignores leap years)
        return 31 if month in (1,3,5,7,8,10,12) else (30 if month in (4,6,9,11) else 28)

    start_year = project.start_date.year
    end_year   = project.end_date.year
    for year in range(start_year, end_year + 1):
        for q, (sm, em) in [("Q1",(1,3)), ("Q2",(4,6)), ("Q3",(7,9)), ("Q4",(10,12))]:
            q_start = dt.date(year, sm, 1)
            q_end   = dt.date(year, em, last_day_of_month(year, em))
            # overlap check
            if q_end < project.start_date or q_start > project.end_date:
                continue
            label = f"{q} {year}"
            exists = session.execute(
                select(ReportingPeriod).where(
                    ReportingPeriod.project_id == project.id,
                    ReportingPeriod.label == label
                )
            ).scalar_one_or_none()
            if not exists:
                session.add(ReportingPeriod(
                    project_id=project.id,
                    label=label,
                    start_date=q_start,
                    end_date=q_end,
                    due_date=q_end + dt.timedelta(days=15),
                    status=PeriodStatus.open
                ))
    session.commit()

def mark_overdue_periods(session) -> int:
    """Flip open/planned periods to 'overdue' if past due_date. Returns #updated."""
    today = dt.date.today()
    q = select(ReportingPeriod).where(
        ReportingPeriod.due_date < today,
        ReportingPeriod.status.notin_([PeriodStatus.submitted, PeriodStatus.approved, PeriodStatus.overdue])
    )
    updated = 0
    for rp in session.execute(q).scalars().all():
        rp.status = PeriodStatus.overdue
        updated += 1
    session.commit()
    return updated

def overlaps(a_start: Date, a_end: Date, p_start: Date, p_end: Date) -> bool:
    """True if [a_start, a_end] overlaps [p_start, p_end]."""
    return not (a_end < p_start or a_start > p_end)

# ---------------------------------------------------------------------
# Init (create tables)
# ---------------------------------------------------------------------
def init_db() -> None:
    Base.metadata.create_all(bind=engine)

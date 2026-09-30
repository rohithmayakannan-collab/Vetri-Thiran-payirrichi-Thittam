from pathlib import Path

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent.parent / 'fitbuddy.db'}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    schedule = Column(Integer, nullable=False, default=7)
    plans = relationship("WorkoutPlan", back_populates="user", order_by="WorkoutPlan.id")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    user = relationship("User", back_populates="plans")


def save_user(
    user_id: int,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id=user_id).first()

        if existing:
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            db.add(
                User(
                    id=user_id,
                    name=name,
                    age=age,
                    weight=weight,
                    goal=goal,
                    intensity=intensity,
                    schedule=7,
                )
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def save_plan(user_id: int, plan: str) -> None:
    db = SessionLocal()
    try:
        workout = WorkoutPlan(user_id=user_id, original_plan=plan)
        db.add(workout)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_original_plan(user_id: int) -> str | None:
    db = SessionLocal()
    try:
        workout = (
            db.query(WorkoutPlan)
            .filter_by(user_id=user_id)
            .order_by(WorkoutPlan.id)
            .first()
        )
        return workout.original_plan if workout else None
    finally:
        db.close()


def update_plan(user_id: int, updated_plan: str) -> bool:
    db = SessionLocal()
    try:
        workout = (
            db.query(WorkoutPlan)
            .filter_by(user_id=user_id)
            .order_by(WorkoutPlan.id)
            .first()
        )
        if not workout:
            return False

        workout.updated_plan = updated_plan
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
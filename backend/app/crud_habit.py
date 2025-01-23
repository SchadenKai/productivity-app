from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select, and_

from app.models import Habit, HabitCreate, HabitUpdate, HabitPublic
from app.core.security import get_password_hash

def create_habit(session: Session, habit_create: HabitCreate) -> Habit:
    db_habit = Habit.from_orm(habit_create)
    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit

def get_habit(session: Session, habit_id: str, user_id: str) -> Optional[Habit]:
    habit = session.exec(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == user_id
            )
        )
    ).first()
    return habit

def get_user_habits(session: Session, user_id: str) -> list[Habit]:
    habits = session.exec(
        select(Habit).where(Habit.user_id == user_id)
    ).all()
    return habits

def update_habit(
    session: Session, 
    db_habit: Habit, 
    habit_update: HabitUpdate
) -> Habit:
    habit_data = habit_update.dict(exclude_unset=True)
    
    # Handle habit completion
    if habit_update.is_completed is not None:
        if habit_update.is_completed:
            # Update streak if completed today
            if db_habit.last_completed is None or (
                datetime.utcnow().date() > db_habit.last_completed.date()
            ):
                db_habit.streak += 1
            db_habit.last_completed = datetime.utcnow()
        else:
            # Reset streak if uncompleted
            db_habit.streak = 0
    
    for key, value in habit_data.items():
        setattr(db_habit, key, value)
    
    db_habit.updated_at = datetime.utcnow()
    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit

def delete_habit(session: Session, db_habit: Habit) -> None:
    session.delete(db_habit)
    session.commit()

def reset_habits(session: Session, user_id: str) -> None:
    """Reset all habits for a user based on their timezone and reset time"""
    habits = get_user_habits(session, user_id)
    now = datetime.utcnow()
    
    for habit in habits:
        # Convert reset time to UTC based on user's timezone
        reset_time = datetime.strptime(habit.reset_time, "%H:%M").time()
        last_reset = now.replace(
            hour=reset_time.hour,
            minute=reset_time.minute,
            second=0,
            microsecond=0
        )
        
        # If reset time hasn't occurred yet today, adjust to previous day
        if last_reset > now:
            last_reset -= timedelta(days=1)
        
        # Reset habit if it hasn't been completed since last reset
        if habit.last_completed is None or habit.last_completed < last_reset:
            habit.is_completed = False
            session.add(habit)
    
    session.commit()

def calculate_habit_stats(session: Session, user_id: str) -> dict:
    """Calculate habit statistics for a user"""
    habits = get_user_habits(session, user_id)
    total_habits = len(habits)
    completed_today = sum(1 for h in habits if h.is_completed)
    
    return {
        "total_habits": total_habits,
        "completed_today": completed_today,
        "completion_rate": completed_today / total_habits if total_habits > 0 else 0
    }
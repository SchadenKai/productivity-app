from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import SessionDep, CurrentUser
from app.models import Habit, HabitCreate, HabitUpdate, HabitPublic
from app.crud_habit import (
    create_habit,
    get_habit,
    get_user_habits,
    update_habit,
    delete_habit,
    reset_habits,
    calculate_habit_stats
)

router = APIRouter()

@router.post("/", response_model=HabitPublic)
def create_new_habit(
    *, 
    session: SessionDep, 
    current_user: CurrentUser,
    habit: HabitCreate
):
    habit.user_id = current_user.id
    db_habit = create_habit(session=session, habit_create=habit)
    return db_habit

@router.get("/", response_model=List[HabitPublic])
def read_user_habits(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
):
    habits = get_user_habits(session=session, user_id=str(current_user.id))
    return habits

@router.get("/{habit_id}", response_model=HabitPublic)
def read_habit(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    habit_id: str
):
    habit = get_habit(session=session, habit_id=habit_id, user_id=str(current_user.id))
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.put("/{habit_id}", response_model=HabitPublic)
def update_existing_habit(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    habit_id: str,
    habit: HabitUpdate
):
    db_habit = get_habit(session=session, habit_id=habit_id, user_id=str(current_user.id))
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db_habit = update_habit(session=session, db_habit=db_habit, habit_update=habit)
    return db_habit

@router.delete("/{habit_id}")
def delete_existing_habit(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    habit_id: str
):
    db_habit = get_habit(session=session, habit_id=habit_id, user_id=str(current_user.id))
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    delete_habit(session=session, db_habit=db_habit)
    return {"ok": True}

@router.get("/stats/")
def get_habit_stats(
    *,
    session: SessionDep,
    current_user: CurrentUser
):
    return calculate_habit_stats(session=session, user_id=str(current_user.id))

@router.post("/reset/")
def reset_user_habits(
    *,
    session: SessionDep,
    current_user: CurrentUser
):
    reset_habits(session=session, user_id=str(current_user.id))
    return {"message": "Habits reset successfully"}
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

from app.ai.init import (
	generate_nutrition_tip_with_flash,
	generate_workout_gemini,
	update_workout_plan,
)
from app.database import (
	SessionLocal,
	User,
	get_original_plan,
	save_plan,
	save_user,
	update_plan,
)


router = APIRouter()
templates = Jinja2Templates(directory="templates")


class UserInput(BaseModel):
	user_id: int
	username: str
	age: int
	weight: float
	goal: str
	intensity: str


class FeedbackRequest(BaseModel):
	feedback: str


@router.post("/generate-plan")
def generate_plan(user_data: UserInput):
	try:
		save_user(
			user_id=user_data.user_id,
			name=user_data.username,
			age=user_data.age,
			weight=user_data.weight,
			goal=user_data.goal,
			intensity=user_data.intensity,
		)

		plan = generate_workout_gemini(
			{"goal": user_data.goal, "intensity": user_data.intensity}
		)
		save_plan(user_data.user_id, plan)

		return {
			"message": "Workout plan generated and saved successfully!",
			"workout_plan": plan,
		}
	except Exception as error:
		raise HTTPException(
			status_code=500,
			detail=f"Something went wrong: {error}",
		) from error


@router.post("/update-plan/{user_id}", response_model=dict)
def update_user_plan(user_id: int, data: FeedbackRequest):
	original = get_original_plan(user_id)
	if not original:
		return {"error": "Original plan not found for this user."}

	updated = update_workout_plan(original, data.feedback)
	update_plan(user_id, updated)
	return {"updated_plan": updated}


@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
	tip = generate_nutrition_tip_with_flash(goal)
	return {"goal": goal, "nutrition_tip": tip}


@router.get("/view-all-users", response_class=HTMLResponse, name="view_all_users")
def view_all_users(request: Request):
	db = SessionLocal()
	try:
		users = (
			db.query(User)
			.options(selectinload(User.plans))
			.order_by(User.id)
			.all()
		)
		user_data = []
		for user in users:
			plan = user.plans[0] if user.plans else None
			user_data.append(
				{
					"id": user.id,
					"name": user.name,
					"age": user.age,
					"weight": user.weight,
					"goal": user.goal,
					"intensity": user.intensity,
					"schedule": user.schedule,
					"original_plan": plan.original_plan if plan else "N/A",
					"updated_plan": (
						plan.updated_plan if plan and plan.updated_plan else "Not updated"
					),
				}
			)
		return templates.TemplateResponse(
			request=request,
			name="all_users.html",
			context={"users": user_data},
		)
	finally:
		db.close()

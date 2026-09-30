import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _generate_with_flash(prompt: str, empty_response_message: str) -> str:
	api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("Set GOOGLE_API_KEY or GEMINI_API_KEY to use Gemini Flash.")

	client = genai.Client(api_key=api_key)
	try:
		response = client.models.generate_content(
			model="gemini-2.5-flash",
			contents=prompt,
		)
		if not response.text:
			raise RuntimeError(empty_response_message)
		return response.text.strip()
	finally:
		client.close()


def generate_nutrition_tip_with_flash(goal: str) -> str:
	return _generate_with_flash(
		"Give one concise, practical nutrition tip for a person with this fitness "
		f"goal: {goal!r}. Keep it general and evidence-informed; do not diagnose or "
		"recommend extreme diets or supplement dosages.",
		"Gemini returned an empty nutrition tip.",
	)


def generate_workout_gemini(user_data: dict[str, str]) -> str:
	goal = user_data["goal"]
	intensity = user_data["intensity"]
	return _generate_with_flash(
		"Create a practical workout plan for a person with this fitness goal: "
		f"{goal!r}, at this intensity: {intensity!r}. Include a weekly structure, "
		"exercise names, sets and repetitions or durations, and brief recovery guidance. "
		"Keep it general and include a reminder to adjust for pain or medical limitations.",
		"Gemini returned an empty workout plan.",
	)


def update_workout_plan(original_plan: str, feedback: str) -> str:
	return _generate_with_flash(
		"Revise this workout plan to address the user's feedback. Preserve useful "
		"structure, keep the plan practical and general, and include a safety reminder "
		"to adjust for pain or medical limitations.\n\n"
		f"Current plan:\n{original_plan}\n\nUser feedback:\n{feedback}",
		"Gemini returned an empty updated workout plan.",
	)

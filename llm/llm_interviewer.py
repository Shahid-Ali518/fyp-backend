import json
import traceback

import openai
from typing import List, Dict

from openai import AsyncOpenAI

from schemas.survey_option_schema import SurveyOptionDTO

client = AsyncOpenAI(
    base_url="http://localhost:11434/",
    api_key="ollama" # Ollama doesn't need a real key, but the client requires a string
)


class LLMInterviewer:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def evaluate_answer(self, user_answer: str, options: List[Dict]) -> Dict:
        # If options are dicts from constants.py, access them like dicts
        # If they are DTOs, use opt.id
        try:
            options_text = {str(opt["id"]): opt["option_text"] for opt in options}
            # Clinical System Prompt
            system_message = (
                "You are a psychiatric clinical assistant helping conduct an initial patient intake. "
                "Your goal is to listen to the patient's response and map it to the correct clinical observation. "
                "Your feedback should be empathetic, calm, and supportive in a mix of Urdu and English."
            )

            prompt = f"""
            Current Clinical Options: {options_text}
            Patient's Response: "{user_answer}"

            Task:
            1. Select the 'selected_id' that best fits the patient's symptomatic description.
            2. Provide 'feedback' (one sentence) that acknowledges their feeling and moves to the next part of the form.
            """


            response = await self.client.chat.completions.create(
                model="qwen2.5:1.5b",  # Use your local model name here
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            print("Model is called")
            print(response)

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            return {}
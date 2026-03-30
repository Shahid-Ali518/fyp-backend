import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Configure Google Generative AI (Gemini)
# Note: User needs to provide GEMINI_API_KEY in .env

ENABLE_LLM = os.getenv("ENABLE_GEMINI_LLM", "false").lower() == "true"

if ENABLE_LLM:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
    else:
        model = None

class LLMInterviewService:
    def __init__(self):
        self.system_prompt = (
            "You are a professional psychiatrist conducting a structured mental health assessment.\n"
            "Your goal is to assess the user's mental state regarding: {category}.\n"
            "You must ask exactly 5 questions in total to reach a conclusion.\n"
            "Current progress: You have already asked {q_count} questions.\n"
            "History of questions and user answers is provided below.\n"
            "Rules:\n"
            "1. Each question must be unique and build upon the user's previous responses.\n"
            "2. Do not repeat yourself.\n"
            "3. Be empathetic but professional.\n"
            "4. Return ONLY the text of the next single question."
        )

    async def get_next_question(self, category: str, previous_questions: List[str], previous_answers: List[str]) -> str:
        """Generates the next question based on the assessment category and history."""
        
        q_count = len(previous_answers)
        if not model:
            # Fallback to static questions if no API key is provided
            default_questions = {
                "depression": [
                    "How has your mood been over the past two weeks?",
                    "Have you noticed a loss of interest in activities you normally enjoy?",
                    "How would you describe your energy levels lately?",
                    "Have you been experiencing any changes in your sleep patterns?",
                    "How are you feeling about your future right now?"
                ],
                "anxiety": [
                    "How often have you felt nervous or on edge recently?",
                    "Have you found it difficult to stop or control worrying?",
                    "Have you experienced any physical symptoms of tension, like restlessness?",
                    "How much does worry interfere with your daily life?",
                    "Do you find yourself avoiding certain situations due to fear or anxiety?"
                ]
            }
            q_idx = q_count
            cat_lower = category.lower()
            if cat_lower in default_questions and q_idx < 5:
                return default_questions[cat_lower][q_idx]
            return "Thank you for sharing. We have enough information for your assessment."

        # Build prompt for LLM
        history_text = ""
        for i, (q, a) in enumerate(zip(previous_questions, previous_answers)):
            history_text += f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n\n"
        
        # If there's a question without an answer yet (the current one being processed)
        if len(previous_questions) > len(previous_answers):
            current_q = previous_questions[-1]
            history_text += f"Current Question (just answered): {current_q}\nUser's Latest Answer: {previous_answers[-1]}\n"

        prompt = self.system_prompt.format(category=category, q_count=q_count)
        if history_text:
            prompt += f"\n--- Interview History ---\n{history_text}\n"

        prompt += "\nBased on the above, what is the next most relevant question to ask?"
        
        print(f"DEBUG: Generating question {q_count + 1} for category: {category}")
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                generated_text = response.text.strip()
                # Remove any markdown or "Question:" prefixes if LLM adds them
                if generated_text.lower().startswith("question:"):
                    generated_text = generated_text[9:].strip()
                
                print(f"DEBUG: LLM Response: {generated_text}")
                return generated_text
            else:
                print("DEBUG: LLM returned empty response")
                return "How does that impact your daily life?"
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Could you tell me more about how you've been feeling lately?"

llm_service = LLMInterviewService()
 
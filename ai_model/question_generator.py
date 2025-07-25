# ai_model/question_generator.py
from groq import Groq
import os
from dotenv import load_dotenv
import random
import re
import json

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set GROQ_API_KEY in .env")

# API_KEY = "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"  # Replace with your actual key
client = Groq(api_key=API_KEY)

def generate_multiple_questions(topic: str, difficulty: str, count: int) -> list:
    questions = []
    for _ in range(count):
        rand_id = random.randint(1000, 9999)
        prompt = (
            f"Generate a unique {difficulty} level aptitude multiple-choice question from topic '{topic}'. "
            "It must have exactly 4 distinct options. The correct answer must be one of these options. "
            "Output strictly as a JSON object with the following keys:\n"
            "'question': (string, the question text),\n"
            "'options': (array of 4 strings, each starting with 'A) ', 'B) ', 'C) ', 'D) ' followed by the option text),\n"
            "'answer_label': (string, the label of the correct option, e.g., 'A', 'B', 'C', or 'D'),\n"
            "'explanation': (string, a concise explanation for the correct answer).\n"
            "Ensure no other text, comments, or markdown fences are present outside the JSON object. "
            "Do not repeat any previously generated questions."
            f"Example for '{topic}': {{\"question\": \"What is 10% of 200?\", \"options\": [\"A) 10\", \"B) 20\", \"C) 30\", \"D) 40\"], \"answer_label\": \"B\", \"explanation\": \"To find 10% of 200, multiply 200 by 0.10, which equals 20.\"}}"
        )

        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
            )
            content = completion.choices[0].message.content.strip()
            try:
                parsed_data = json.loads(content)
                question = parsed_data.get('question')
                options = parsed_data.get('options')
                answer_label = parsed_data.get('answer_label', '').upper()

                # Basic validation of parsed data
                if not question or not isinstance(options, list) or len(options) != 4 or not answer_label:
                    print(f"⚠️ Skipped due to incomplete or invalid JSON data from AI. Content: {content}")
                    continue

                # Find the full answer string based on the label
                answer = ""
                for opt in options:
                    if opt.startswith(f"{answer_label})"):
                        answer = opt
                        break

                if not answer:
                    print(f"⚠️ Skipped: Correct answer option label '{answer_label}' not found among generated options. Content: {content}")
                    continue

            except json.JSONDecodeError:
                print(f"⚠️ Skipped due to JSON parsing error (AI did not return valid JSON). Raw Content: {content}")
                continue
            if question and len(options) == 4 and answer:
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
            else:
                print("⚠️ Skipped due to incomplete data.")
        except Exception as e:
            print("Parsing error:", e)
            continue

    return questions

import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def evaluate_answer(
    question,
    answer,
    profile,
    interview_type,
    difficulty
):

    prompt = f"""
You are a professional interviewer evaluating a candidate.

Interview type:
{interview_type}

Difficulty:
{difficulty}

Candidate profile:
{profile}

Question asked:
{question}

Candidate's answer:
{answer}

Evaluate the candidate's answer.

Return ONLY valid JSON in this format:

{{
    "score": 0,
    "strengths": [],
    "weaknesses": [],
    "feedback": ""
}}

Rules:

1. Score the answer from 0 to 10.
2. Check whether the answer actually addresses the question.
3. Check technical correctness when relevant.
4. Identify what the candidate did well.
5. Identify what the candidate should improve.
6. Give useful and practical feedback.
7. Do not invent information about the candidate.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text.strip()

    except errors.ClientError as e:

        print("❌ Gemini API error while evaluating answer:")
        print(e)

        # Important:
        # Return feedback instead of crashing Flask.

        return """
{
    "score": 0,
    "strengths": [],
    "weaknesses": ["AI evaluation temporarily unavailable"],
    "feedback": "The answer was received successfully, but AI evaluation is temporarily unavailable because the Gemini API quota has been exceeded."
}
"""

    except Exception as e:

        print("❌ Answer evaluation error:")
        print(e)

        return """
{
    "score": 0,
    "strengths": [],
    "weaknesses": ["Evaluation unavailable"],
    "feedback": "Your answer was received, but the AI evaluator could not process it."
}
"""
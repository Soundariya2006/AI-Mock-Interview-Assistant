import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_followup_question(
    previous_question,
    previous_answer,
    evaluation,
    profile,
    interview_type,
    difficulty
):

    prompt = f"""
You are a professional human interviewer conducting an adaptive interview.

Interview type:
{interview_type}

Difficulty:
{difficulty}

Candidate profile:
{profile}

Previous question:
{previous_question}

Candidate's previous answer:
{previous_answer}

AI evaluation:
{evaluation}

Generate the NEXT interview question.

Rules:

1. The question MUST match the interview type.
2. The question should relate to the previous answer when appropriate.
3. Use the candidate's resume/profile when relevant.
4. If the answer was weak, ask a question that clarifies or tests the missing concept.
5. If the answer was strong, increase the depth or difficulty.
6. Do not repeat the previous question.
7. Ask ONLY ONE question.
8. Sound like a real human interviewer.
9. Do not provide the answer.
10. Do not provide feedback.
11. Return ONLY the question.

Generate the next question now.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text.strip()

    except errors.ClientError as e:

        print("❌ Gemini API error while generating follow-up:")
        print(e)

        # Mode-specific fallback
        interview_mode = (interview_type or "").lower()

        if "hr" in interview_mode:

            return (
                "What are your career goals, and how do you think "
                "this role will help you achieve them?"
            )

        elif "behavior" in interview_mode:

            return (
                "Can you describe another situation where you had "
                "to overcome a difficult challenge?"
            )

        elif "technical" in interview_mode:

            return (
                "Can you explain one technical challenge you faced "
                "in a project and how you solved it?"
            )

        return (
            "Can you tell me about another challenge you faced "
            "and how you handled it?"
        )

    except Exception as e:

        print("❌ Follow-up question error:")
        print(e)

        return (
            "Can you tell me about another challenge you faced "
            "and how you handled it?"
        )
import os 
import json
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def create_candidate_profile(resume_text):

    if not resume_text or not resume_text.strip():

        print("❌ No text could be extracted from resume.")

        return {
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "certifications": []
        }

    print("✅ Resume text extracted.")
    print("Resume text length:", len(resume_text))


    prompt = f"""
You are a professional resume analyzer.

Analyze the following resume and extract the candidate's information.

Return ONLY valid JSON in this exact structure:

{{
    "skills": [],
    "projects": [],
    "education": [],
    "experience": [],
    "certifications": []
}}

Rules:

1. Extract only information that actually exists in the resume.
2. Do not invent information.
3. Keep skills as individual items.
4. Keep projects as individual items.
5. Keep education as individual items.
6. Keep experience as individual items.
7. Keep certifications as individual items.

Resume:

{resume_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        response_text = response.text.strip()

        if response_text.startswith("```"):

            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "")
            response_text = response_text.strip()

        profile = json.loads(response_text)

        print("✅ Resume profile extracted successfully.")
        print(profile)

        return profile


    except errors.ClientError as e:

        print("❌ Gemini API error while analyzing resume:")
        print(e)

        return {
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "certifications": []
        }


    except json.JSONDecodeError:

        print("❌ Gemini returned invalid JSON.")

        print("Gemini response:")
        print(response_text)

        return {
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "certifications": []
        }


    except Exception as e:

        print("❌ Resume analyzer error:")
        print(e)

        return {
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "certifications": []
        }
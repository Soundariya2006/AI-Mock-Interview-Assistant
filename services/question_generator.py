import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_first_question(profile, interview_type, difficulty):

    interview_mode = (interview_type or "").lower().strip()

    prompt = f"""
You are a professional human interviewer.

You are conducting a {interview_type} interview.

Interview difficulty:
{difficulty}

Candidate profile:

Skills:
{profile.get("skills", [])}

Projects:
{profile.get("projects", [])}

Education:
{profile.get("education", [])}

Experience:
{profile.get("experience", [])}

Certifications:
{profile.get("certifications", [])}


IMPORTANT: The question MUST strictly match the selected interview type.

INTERVIEW TYPE RULES:

1. HR INTERVIEW:
   Ask questions about:
   - Self introduction
   - Career goals
   - Strengths and weaknesses
   - Motivation
   - Why the candidate wants the role/company
   - Workplace preferences
   - Career plans

2. BEHAVIORAL INTERVIEW:
   Ask questions about real situations and past experiences.
   Examples:
   - Teamwork
   - Conflict
   - Leadership
   - Failure
   - Challenges
   - Problem solving
   - Handling pressure
   Prefer questions that can be answered using the STAR approach.

3. TECHNICAL INTERVIEW:
   Ask technical concept or project-related questions.
   Examples:
   - Java concepts
   - Python concepts
   - SQL
   - OOP
   - Data structures
   - Databases
   - Technologies listed in the resume
   - Technical decisions made in projects

4. CODING INTERVIEW:
   This is VERY IMPORTANT.

   Ask an ACTUAL PROGRAMMING/CODING question.

   The question should involve one or more of:
   - Writing code
   - Arrays
   - Strings
   - HashMap / HashSet
   - Linked lists
   - Stack / Queue
   - Searching
   - Sorting
   - Recursion
   - Algorithms
   - Data structures
   - Debugging
   - Time complexity
   - Space complexity

   The candidate should be expected to WRITE or EXPLAIN CODE.

   Do NOT ask a general data-science question.
   Do NOT ask a general career question.
   Do NOT ask a general technical theory question unless it is directly part
   of a coding problem.

   If the candidate has Java in the resume, Java coding questions are preferred.

   If the candidate has Python in the resume, Python coding questions may also
   be used.

   Example coding question:

   "Given an integer array, write a Java program to find the second largest
   element without sorting the array. Explain the time complexity."

DIFFICULTY RULES:

Beginner:
- Basic programming
- Simple loops
- Conditions
- Basic arrays
- Basic strings
- Simple HashMap usage

Intermediate:
- Arrays and strings
- HashMap / HashSet
- Two pointers
- Sliding window
- Sorting/searching
- Recursion
- Moderate algorithmic problems
- Time and space complexity

Advanced:
- Dynamic programming
- Graphs
- Trees
- Advanced algorithms
- Optimization
- Complex data structures

GENERAL RULES:

1. Use the candidate's resume/profile when relevant.
2. Do not invent candidate experience.
3. Match the requested difficulty.
4. Make it sound like a real human interviewer.
5. Ask ONLY ONE question.
6. Do not provide the answer.
7. Do not provide feedback.
8. Do not provide multiple questions.
9. Return ONLY the interview question.
10. Do not add labels such as "Question:".
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text.strip()

    except errors.ClientError as e:

        print("❌ Gemini API error while generating first question:")
        print(e)

        # -----------------------------------------
        # MODE-SPECIFIC FALLBACK QUESTIONS
        # -----------------------------------------

        if "hr" in interview_mode:

            return (
                "Could you introduce yourself and explain "
                "why you are interested in this role?"
            )

        elif "behavior" in interview_mode:

            return (
                "Tell me about a challenging situation you faced "
                "while working on a project and how you handled it."
            )

        elif "coding" in interview_mode:

            skills = profile.get("skills", [])

            if "Java" in skills:

                return (
                    "Given an integer array, write a Java program to find "
                    "the second largest element without sorting the array. "
                    "Explain your approach and time complexity."
                )

            elif "Python" in skills:

                return (
                    "Given an integer array, write a Python program to find "
                    "the second largest element without sorting the array. "
                    "Explain your approach and time complexity."
                )

            return (
                "Given an integer array, write a program to find the "
                "second largest element without sorting the array. "
                "Explain your approach and time complexity."
            )

        elif "technical" in interview_mode:

            skills = profile.get("skills", [])

            if skills:

                return (
                    f"Can you explain your experience with "
                    f"{skills[0]} and how you have used it in a project?"
                )

            return (
                "Can you explain one technical concept "
                "that you are confident about?"
            )

        return (
            "Could you introduce yourself and explain your key strengths?"
        )

    except Exception as e:

        print("❌ Question generator error:")
        print(e)

        if "coding" in interview_mode:

            return (
                "Given an integer array, write a Java program to find "
                "the second largest element without sorting the array. "
                "Explain your approach and time complexity."
            )

        return (
            "Could you introduce yourself and explain your key strengths?"
        )
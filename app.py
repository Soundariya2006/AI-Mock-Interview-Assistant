from flask import Flask, render_template, request, session
import os
import html

from services.resume_parser import extract_resume_text
from services.resume_analyzer import create_candidate_profile
from services.question_generator import generate_first_question
from services.answer_evaluator import evaluate_answer
from services.followup_generator import generate_followup_question


app = Flask(__name__)

# Required for Flask session
app.secret_key = "ai-mock-interview-secret-key"


# ============================================================
# UPLOAD FOLDER
# ============================================================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# START INTERVIEW
# ============================================================

@app.route("/start-interview", methods=["POST"])
def start_interview():

    # --------------------------------------------------------
    # GET RESUME
    # --------------------------------------------------------

    resume = request.files.get("resume")

    if not resume or resume.filename == "":
        return "No resume uploaded."

    # --------------------------------------------------------
    # SAVE RESUME
    # --------------------------------------------------------

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(file_path)

    # --------------------------------------------------------
    # EXTRACT RESUME TEXT
    # --------------------------------------------------------

    try:
        resume_text = extract_resume_text(file_path)

    except Exception as e:

        print("❌ Resume extraction error:")
        print(e)

        return """
        <h2>❌ Could not read the resume.</h2>
        <p>Please make sure you uploaded a valid PDF or DOCX file.</p>
        <a href="/">Go Back</a>
        """

    # --------------------------------------------------------
    # CHECK WHETHER TEXT WAS EXTRACTED
    # --------------------------------------------------------

    print("\n========================================")
    print("RESUME TEXT EXTRACTED")
    print("========================================")
    print(resume_text[:5000])
    print("========================================\n")

    if not resume_text or not resume_text.strip():

        return """
        <h2>❌ Resume text could not be extracted.</h2>

        <p>
        The uploaded resume appears to contain no readable text.
        </p>

        <p>
        If this is a scanned/image-based PDF, please upload a
        text-based PDF or DOCX resume.
        </p>

        <a href="/">Go Back</a>
        """

    # --------------------------------------------------------
    # GET INTERVIEW SETTINGS
    # --------------------------------------------------------

    interview_type = request.form.get(
        "interview_type",
        "technical"
    )

    difficulty = request.form.get(
        "difficulty",
        "intermediate"
    )

    print("Interview Type:", interview_type)
    print("Difficulty:", difficulty)

    # --------------------------------------------------------
    # CREATE CANDIDATE PROFILE
    # --------------------------------------------------------

    try:

        profile = create_candidate_profile(resume_text)

    except Exception as e:

        print("❌ Resume analyzer error:")
        print(e)

        profile = {
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "certifications": []
        }

    print("\n========================================")
    print("CANDIDATE PROFILE")
    print("========================================")
    print(profile)
    print("========================================\n")

    # --------------------------------------------------------
    # GENERATE FIRST QUESTION
    # --------------------------------------------------------

    try:

        first_question = generate_first_question(
            profile,
            interview_type,
            difficulty
        )

    except Exception as e:

        print("❌ First question generation error:")
        print(e)

        first_question = (
            "Could you introduce yourself and briefly "
            "describe your background?"
        )

    # Safety fallback
    if not first_question or not first_question.strip():

        first_question = (
            "Could you introduce yourself and briefly "
            "describe your background?"
        )

    # --------------------------------------------------------
    # CREATE INTERVIEW SESSION
    # --------------------------------------------------------

    session["profile"] = profile
    session["interview_type"] = interview_type
    session["difficulty"] = difficulty
    session["resume_text"] = resume_text

    # Interview history
    session["history"] = []

    # Question number
    session["question_number"] = 1

    # IMPORTANT:
    # Store current question
    session["current_question"] = first_question

    # --------------------------------------------------------
    # ESCAPE TEXT BEFORE DISPLAYING IN HTML
    # --------------------------------------------------------

    safe_first_question = html.escape(first_question)

    # Convert profile values to readable strings
    skills = html.escape(
        ", ".join(profile.get("skills", []))
    )

    projects = html.escape(
        ", ".join(profile.get("projects", []))
    )

    education = html.escape(
        ", ".join(profile.get("education", []))
    )

    experience = html.escape(
        ", ".join(profile.get("experience", []))
    )

    certifications = html.escape(
        ", ".join(profile.get("certifications", []))
    )

    # --------------------------------------------------------
    # DISPLAY FIRST QUESTION
    # --------------------------------------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

    <title>AI Mock Interview</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
        }}

        textarea {{
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
        }}

        button {{
            padding: 12px 20px;
            margin-top: 10px;
            cursor: pointer;
            border-radius: 6px;
        }}

        .end-btn {{
            background: #dc3545;
            color: white;
            border: none;
        }}

        .submit-btn {{
            background: #198754;
            color: white;
            border: none;
        }}

        .question {{
            background: #eef4ff;
            padding: 20px;
            border-radius: 10px;
        }}

        .profile {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}

        #voiceStatus {{
            font-weight: bold;
            margin-top: 10px;
        }}

    </style>

</head>


<body>

<div class="container">

    <h1>🎤 AI Mock Interview</h1>

    <p>
        <strong>Interview Type:</strong>
        {html.escape(interview_type)}
    </p>

    <p>
        <strong>Difficulty:</strong>
        {html.escape(difficulty)}
    </p>

    <p>
        Question {session["question_number"]}
    </p>

    <hr>


    <div class="profile">

        <h2>👤 Candidate Profile</h2>

        <h3>Skills</h3>
        <p>{skills if skills else "Not detected"}</p>

        <h3>Projects</h3>
        <p>{projects if projects else "Not detected"}</p>

        <h3>Education</h3>
        <p>{education if education else "Not detected"}</p>

        <h3>Experience</h3>
        <p>{experience if experience else "Not detected"}</p>

        <h3>Certifications</h3>
        <p>{certifications if certifications else "Not detected"}</p>

    </div>


    <hr>


    <div class="question">

        <h2>🤖 AI Interviewer's Question</h2>

        <h3 id="question">
            {safe_first_question}
        </h3>

        <button
            type="button"
            onclick="speakQuestion()"
        >
            🔊 Listen to Question
        </button>

    </div>


    <hr>


    <h2>💬 Your Answer</h2>


    <form
        action="/submit-answer"
        method="POST"
    >

        <textarea
            name="answer"
            rows="8"
            placeholder="Type your answer here..."
            required
        ></textarea>

        <br>

        <button
            type="submit"
            class="submit-btn"
        >
            🧠 Submit Answer
        </button>

    </form>


    <br>


    <button
        type="button"
        class="end-btn"
        onclick="endInterview()"
    >
        🏁 End Interview
    </button>


    <script>

        // ==================================================
        // READ QUESTION ALOUD
        // ==================================================

        function speakQuestion() {{

            const question =
                document.getElementById("question").innerText;

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(question);

            speech.lang = "en-US";
            speech.rate = 0.9;
            speech.pitch = 1;

            window.speechSynthesis.speak(speech);
        }}


        // ==================================================
        // END INTERVIEW
        // ==================================================

        function endInterview() {{

            const confirmEnd = confirm(
                "Are you sure you want to end the interview?"
            );

            if (confirmEnd) {{

                window.speechSynthesis.cancel();

                window.location.href =
                    "/end-interview";
            }}
        }}

    </script>


</div>

</body>

</html>
"""


# ============================================================
# SUBMIT ANSWER
# ============================================================

@app.route("/submit-answer", methods=["POST"])
def submit_answer():

    # --------------------------------------------------------
    # GET CURRENT QUESTION FROM SESSION
    # --------------------------------------------------------

    question = session.get(
        "current_question",
        ""
    )

    # --------------------------------------------------------
    # GET ANSWER
    # --------------------------------------------------------

    answer = request.form.get(
        "answer",
        ""
    ).strip()

    if not answer:

        return """
        <h2>❌ Please provide an answer.</h2>
        <a href="/">Go Back</a>
        """

    if not question:

        return """
        <h2>❌ Interview session expired.</h2>
        <a href="/">Start New Interview</a>
        """

    # --------------------------------------------------------
    # GET SESSION DATA
    # --------------------------------------------------------

    profile = session.get(
        "profile",
        {}
    )

    interview_type = session.get(
        "interview_type",
        "technical"
    )

    difficulty = session.get(
        "difficulty",
        "intermediate"
    )

    # --------------------------------------------------------
    # EVALUATE ANSWER
    # --------------------------------------------------------

    try:

        evaluation = evaluate_answer(
            question,
            answer,
            profile,
            interview_type,
            difficulty
        )

    except Exception as e:

        print("❌ Evaluation error:")
        print(e)

        evaluation = """
{
    "score": 0,
    "strengths": [],
    "weaknesses": ["AI evaluation unavailable"],
    "feedback": "Your answer was received successfully, but AI evaluation is temporarily unavailable."
}
"""

    # --------------------------------------------------------
    # SAVE INTERVIEW HISTORY
    # --------------------------------------------------------

    history = session.get(
        "history",
        []
    )

    history.append({
        "question": question,
        "answer": answer,
        "evaluation": evaluation
    })

    session["history"] = history

    # --------------------------------------------------------
    # QUESTION NUMBER
    # --------------------------------------------------------

    question_number = session.get(
        "question_number",
        1
    )

    question_number += 1

    session["question_number"] = question_number

    # --------------------------------------------------------
    # GENERATE FOLLOW-UP QUESTION
    # --------------------------------------------------------

    try:

        next_question = generate_followup_question(
            question,
            answer,
            evaluation,
            profile,
            interview_type,
            difficulty
        )

    except Exception as e:

        print("❌ Follow-up question error:")
        print(e)

        next_question = (
            "Could you explain more about the experience "
            "you mentioned in your previous answer?"
        )

    # Safety fallback
    if not next_question or not next_question.strip():

        next_question = (
            "Could you explain more about the experience "
            "you mentioned in your previous answer?"
        )

    # Store current question
    session["current_question"] = next_question

    # --------------------------------------------------------
    # ESCAPE DISPLAY TEXT
    # --------------------------------------------------------

    safe_question = html.escape(question)
    safe_answer = html.escape(answer)
    safe_evaluation = html.escape(evaluation)
    safe_next_question = html.escape(next_question)

    # --------------------------------------------------------
    # DISPLAY FEEDBACK + NEXT QUESTION
    # --------------------------------------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

    <title>AI Mock Interview</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
        }}

        textarea {{
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
        }}

        button {{
            padding: 12px 20px;
            margin-top: 10px;
            cursor: pointer;
            border-radius: 6px;
        }}

        .submit-btn {{
            background: #198754;
            color: white;
            border: none;
        }}

        .end-btn {{
            background: #dc3545;
            color: white;
            border: none;
        }}

        .feedback {{
            background: #f0f8ff;
            padding: 20px;
            border-radius: 10px;
        }}

        .question {{
            background: #eef4ff;
            padding: 20px;
            border-radius: 10px;
        }}

        #voiceStatus {{
            font-weight: bold;
            margin-top: 10px;
        }}

    </style>

</head>


<body>

<div class="container">


    <h1>🎤 AI Mock Interview</h1>

    <p>
        Question {question_number}
    </p>


    <hr>


    <h2>🤖 Previous Question</h2>

    <p>
        {safe_question}
    </p>


    <hr>


    <h2>💬 Your Answer</h2>

    <p>
        {safe_answer}
    </p>


    <hr>


    <div class="feedback">

        <h2>📊 AI Feedback</h2>

        <pre>{safe_evaluation}</pre>

    </div>


    <hr>


    <div class="question">

        <h2>🤖 Next Interview Question</h2>

        <h3 id="question">
            {safe_next_question}
        </h3>

        <button
            type="button"
            onclick="speakQuestion()"
        >
            🔊 Listen to Question
        </button>

    </div>


    <hr>


    <h2>💬 Your Answer</h2>


    <form
        action="/submit-answer"
        method="POST"
    >

        <textarea
            name="answer"
            rows="8"
            placeholder="Type your answer here..."
            required
        ></textarea>

        <br><br>


        <button
            type="button"
            onclick="startVoice()"
        >
            🎤 Start Speaking
        </button>


        <button
            type="button"
            onclick="stopVoice()"
        >
            ⏹ Stop Speaking
        </button>


        <p id="voiceStatus"></p>


        <br>


        <button
            type="submit"
            class="submit-btn"
        >
            🚀 Submit Answer
        </button>

    </form>


    <br>


    <button
        type="button"
        class="end-btn"
        onclick="endInterview()"
    >
        🏁 End Interview
    </button>


    <script>

        // ==================================================
        // READ QUESTION ALOUD
        // ==================================================

        function speakQuestion() {{

            const question =
                document.getElementById("question").innerText;

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(question);

            speech.lang = "en-US";
            speech.rate = 0.9;
            speech.pitch = 1;

            window.speechSynthesis.speak(speech);
        }}


        // ==================================================
        // SPEECH TO TEXT
        // ==================================================

        let recognition = null;


        function startVoice() {{

            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;


            if (!SpeechRecognition) {{

                alert(
                    "Speech recognition is not supported in this browser. Please use Google Chrome."
                );

                return;
            }}


            recognition =
                new SpeechRecognition();


            recognition.lang = "en-US";

            recognition.continuous = true;

            recognition.interimResults = false;


            const textarea =
                document.querySelector(
                    'textarea[name="answer"]'
                );


            const status =
                document.getElementById(
                    "voiceStatus"
                );


            recognition.onstart = function() {{

                status.innerText =
                    "🎤 Listening... Speak your answer.";

            }};


            recognition.onresult =
                function(event) {{

                    let finalText = "";


                    for (
                        let i = event.resultIndex;
                        i < event.results.length;
                        i++
                    ) {{

                        if (
                            event.results[i].isFinal
                        ) {{

                            finalText +=
                                event.results[i][0]
                                .transcript + " ";

                        }}

                    }}


                    if (
                        finalText.trim() !== ""
                    ) {{

                        textarea.value +=
                            finalText;

                    }}

                }};


            recognition.onerror =
                function(event) {{

                    status.innerText =
                        "❌ Voice error: "
                        + event.error;

                }};


            recognition.onend =
                function() {{

                    status.innerText =
                        "⏹ Voice input stopped.";

                }};


            recognition.start();

        }}


        function stopVoice() {{

            if (recognition) {{

                recognition.stop();

                document.getElementById(
                    "voiceStatus"
                ).innerText =
                    "⏹ Voice input stopped.";

            }}

        }}


        // ==================================================
        // END INTERVIEW
        // ==================================================

        function endInterview() {{

            const confirmEnd = confirm(
                "Are you sure you want to end the interview?"
            );


            if (confirmEnd) {{

                window.speechSynthesis.cancel();


                if (recognition) {{

                    recognition.stop();

                }}


                window.location.href =
                    "/end-interview";

            }}

        }}

    </script>


</div>

</body>

</html>
"""


# ============================================================
# END INTERVIEW
# ============================================================

@app.route("/end-interview")
def end_interview():

    # --------------------------------------------------------
    # GET INTERVIEW HISTORY
    # --------------------------------------------------------

    history = session.get(
        "history",
        []
    )

    # --------------------------------------------------------
    # IF NO ANSWERS
    # --------------------------------------------------------

    if not history:

        return """
<!DOCTYPE html>

<html>

<head>

    <title>Interview Completed</title>

</head>

<body>

    <h1>🏁 Interview Completed!</h1>

    <p>
        You did not answer any questions.
    </p>

    <a href="/">
        🔄 Start New Interview
    </a>

</body>

</html>
"""

    # --------------------------------------------------------
    # PREPARE HISTORY FOR AI
    # --------------------------------------------------------

    history_text = ""

    for i, item in enumerate(
        history,
        start=1
    ):

        history_text += f"""

Question {i}:
{item["question"]}

Candidate Answer:
{item["answer"]}

AI Evaluation:
{item["evaluation"]}

----------------------------

"""

    # --------------------------------------------------------
    # GENERATE FINAL REPORT
    # --------------------------------------------------------

    try:

        from google import genai
        from dotenv import load_dotenv

        load_dotenv()

        client = genai.Client(
            api_key=os.getenv(
                "GEMINI_API_KEY"
            )
        )


        prompt = f"""

You are an expert interview evaluator.

Analyze the following complete mock interview.

{history_text}

Create a final interview performance report.

Include:

1. Overall score out of 10
2. Technical knowledge
3. Communication
4. Problem solving
5. Confidence
6. Strengths
7. Weaknesses
8. Areas to improve
9. Final recommendation

Keep the report practical and useful for the candidate.

"""


        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        final_report = response.text


    except Exception as e:

        print("❌ Final report error:")
        print(e)

        final_report = f"""
Final report could not be generated right now.

Your interview contained {len(history)} answered question(s).

The interview data was saved successfully in this session.

Technical information:
{str(e)}
"""

    # --------------------------------------------------------
    # ESCAPE FINAL REPORT
    # --------------------------------------------------------

    safe_final_report = html.escape(
        final_report
    )

    # --------------------------------------------------------
    # DISPLAY FINAL REPORT
    # --------------------------------------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

    <title>Interview Completed</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
        }}

        .report {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            white-space: pre-wrap;
        }}

        a {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 20px;
            background: #198754;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }}

    </style>

</head>


<body>

<div class="container">


    <h1>🏁 Interview Completed!</h1>


    <h2>🎉 Great Job!</h2>

    <p>
        You answered
        {len(history)}
        interview question(s).
    </p>


    <hr>


    <h2>📊 Final AI Performance Report</h2>


    <div class="report">

{safe_final_report}

    </div>


    <hr>


    <a href="/">
        🔄 Start New Interview
    </a>


</div>

</body>

</html>
"""


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
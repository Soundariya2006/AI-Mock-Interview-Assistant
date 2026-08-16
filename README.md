# AI Mock Interview Assistant

An AI-powered mock interview application that helps candidates practice interviews based on their resume, skills, projects, education, experience, and certifications.

## Features

- Resume upload and PDF text extraction
- Candidate profile generation from resume
- ATS score analysis
- Resume improvement suggestions
- AI-generated interview questions
- Multiple interview types:
  - HR
  - Behavioral
  - Technical
  - Coding
- Different difficulty levels
- Answer evaluation
- AI-generated follow-up questions
- Personalized questions based on candidate profile

## Technologies Used

- Python
- Flask
- Google Gemini API
- PyMuPDF
- python-docx
- HTML
- CSS
- JavaScript
- python-dotenv

## Project Structure

```text
AI-Mock-Interview-Assistant/
│
├── app.py
├── requirements.txt
├── test_gemini.py
├── .gitignore
├── README.md
│
├── services/
│   ├── answer_evaluator.py
│   ├── followup_generator.py
│   ├── question_generator.py
│   ├── resume_analyzer.py
│   └── resume_parser.py
│
├── static/
│   └── style.css
│
└── templates/
    └── index.html

How It Works
Resume Upload
      ↓
Resume Text Extraction
      ↓
Candidate Profile Generation
      ↓
Select Interview Type
      ↓
Select Difficulty
      ↓
AI Generates Interview Question
      ↓
Candidate Answers
      ↓
Answer Evaluation
      ↓
Follow-up Question


Installation

1. Clone the repository
git clone https://github.com/Soundariya2006/AI-Mock-Interview-Assistant.git

2. Open the project folder
cd AI-Mock-Interview-Assistant

3. Create a virtual environment
python -m venv venv

4. Activate the virtual environment

For Windows PowerShell:

venv\Scripts\Activate.ps1

5. Install the required packages
pip install -r requirements.txt

API Configuration
Create a .env file in the project root folder.

Add your Gemini API key:

GEMINI_API_KEY=your_api_key_here

Do not upload the .env file to GitHub.

Run the Application
python app.py

Open the local Flask URL shown in the terminal.

Interview Types
HR Interview

Focuses on questions related to:

Introduction
Career goals
Strengths and weaknesses
Motivation
Company and role interest
Behavioral Interview

Focuses on real-life situations, teamwork, challenges, and problem-solving experiences.

Technical Interview

Generates technical questions based on the candidate's skills, projects, and experience.

Coding Interview

Generates programming and problem-solving questions based on the candidate's technical background.

Future Enhancements
Voice-based interviews
Speech-to-text answers
AI interviewer voice
Interview performance dashboard
Interview history
User authentication
Database integration
Advanced ATS analysis
More coding question categories
Author

Soundariya S

B.Tech – Artificial Intelligence and Data Science
Mailam Engineering College

Project Status

This project is currently under development.
```

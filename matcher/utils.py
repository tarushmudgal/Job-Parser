import pdfplumber
from openai import OpenAI
import os
import json
from docx import Document
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Extract Text from PDF

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extract Text from Docs

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_resume(file_path, file_type):
    if file_type == "pdf":
        resume_text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(file_path)
    else:
        return None

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract structured data from resumes."},
            {"role": "user", "content": resume_text},
        ],
        functions=[
            {
                "name": "parse_resume",
                "description": "Parse resume and return structured JSON.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "education": {"type": "array", "items": {"type": "string"}},
                        "work_experience": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name"]
                }
            }
        ],
        function_call={"name": "parse_resume"}
    )

    function_call = response.choices[0].message.function_call
    if function_call:
        parsed_data = function_call.arguments
        return json.loads(parsed_data)
    
    return None

def parse_job_posting(job_text):
    """Extract structured job details from a job posting using LLM."""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a job description parser."},
            {"role": "user", "content": job_text}
        ],
        functions=[
            {
                "name": "parse_job_posting",
                "description": "Extract job details into structured format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Job title"},
                        "company": {"type": "string", "description": "Company name"},
                        "required_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of required skills for the job."
                        },
                        "description": {"type": "string", "description": "Full job description text"}
                    },
                    "required": ["title", "required_skills", "description"]
                }
            }
        ],
        function_call="auto"
    )

    function_response = response.choices[0].message.function_call.arguments
    return function_response


def match_candidate_to_job(candidate, job):
    """Match a candidate to a job and return a match score, missing skills, and summary."""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a job matching assistant."},
            {"role": "user", "content": f"Match this candidate {candidate} with job {job}."}
        ],
        functions=[
            {
                "name": "match_candidate_to_job",
                "description": "Match a candidate to a job and return relevant details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "match_score": {"type": "integer", "description": "Percentage score of how well the candidate fits the job."},
                        "missing_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of skills missing from the candidate's profile."
                        },
                        "summary": {"type": "string", "description": "Short summary of the match assessment."}
                    },
                    "required": ["match_score", "missing_skills", "summary"]
                }
            }
        ],
        function_call="auto"
    )

    function_response = response.choices[0].message.function_call.arguments
    return function_response


def generate_cover_letter(candidate, job):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert resume writer and career advisor."},
            {
                "role": "user",
                "content": f"Generate a professional cover letter for the following candidate based on the given job description. \n\nCandidate: {candidate}\n\nJob: {job}"
            }
        ]
    )

    return response.choices[0].message.content.strip()
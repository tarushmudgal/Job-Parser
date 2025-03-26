# **Job Matcher API**

**This project provides a backend API** to parse resumes, job descriptions, match candidates to job postings, and generate cover letters using OpenAI's GPT models. It is built with Django as the backend framework and uses various utility functions to process resumes, job postings, and generate insights.

## **Table of Contents**

1. Installation  
2. Environment Variables  
3. [Running the](https://slite.com/micro-apps/document-formatter#running-the-application) Application  
4. API Endpoints

## **Installation**

Follow these steps to set up the project on your local machine.

### **1\. Clone the Repository**

git clone https://github.com/your-username/job-matcher-api.git

cd job-matcher-api

### **2\. Set Up a Virtual Environment**

Create and activate a virtual environment:

python3 \-m venv venv

source venv/bin/activate \# Mac Command

On Windows use \`venv\\Scripts\\activate\`

### **3\. Install Dependencies**

Install all required dependencies using **pip**:

pip install \-r requirements.txt

### **4\. Install .env File**

Create a **.env** file in the root directory of the project, and add the following environment variables (replace with your actual API keys):

OPENAI\_API\_KEY=your-openai-api-key

## **Environment Variables**

Make sure to set the following environment variables:

* OPENAI\_API\_KEY: Your OpenAI API key for interacting with GPT models. You can get this from [OpenAI's website](https://platform.openai.com/).

## **Running the Application**

### **1\. Apply Migrations**

If using Django, run migrations to set up the database:

python manage.py migrate

### **2\. Start the Development Server**

Start the development server:

python manage.py runserver

#### **3\. Frontend (Streamlit)**

##### **Navigate to the Frontend Directory**

Go to the **Frontend** directory:

cd Frontend

##### **Start the Frontend Development Server**

* using **Streamlit**:

streamlit run app.py

Your frontend application will be accessible at **http://localhost:8501/**.

## **API Endpoints**

### **1\. Upload Resume**

POST **/api/upload\_resume/**

Upload a resume file (PDF or DOCX) to the API. The system will parse the resume and extract structured data.

### **2\. Job Listings**

GET **/api/job\_listings/**

Fetch all available job listings.

### **3\. Match Candidate to Job**

POST **/api/match/**

Submit a candidate's information and a job listing to get a match score, missing skills, and a summary.

### **4\. Generate Cover Letter**

POST **/api/generate\_cover\_letter/**

Submit a candidate's profile and job description to generate a tailored cover letter.


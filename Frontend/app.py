import streamlit as st
import requests
import json


BASE_URL = "http://127.0.0.1:8000/api/"

def upload_resume():
    """
    Resume Upload Section
    """
    st.header("📄 Resume Upload")
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx'])
    
    if uploaded_file is not None:
        # Determine file type
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        # Prepare file for upload
        files = {
            'resume': (uploaded_file.name, uploaded_file.getvalue(), f'application/{file_type}')
        }
        
        # Send file to backend
        try:
            response = requests.post(
                f"{BASE_URL}upload_resume/", 
                files=files
            )
            
            if response.status_code == 200:
                parsed_resume = response.json()
                st.success("Resume Parsed Successfully!")
                
                # Display parsed resume details
                st.json(parsed_resume)
                
                # Store resume in session state for matching
                st.session_state.parsed_resume = parsed_resume
            else:
                st.error(f"Upload failed: {response.text}")
        
        except Exception as e:
            st.error(f"Error uploading resume: {e}")


def match_resume_to_jobs():
    """
    Resume-Job Matching Section
    """
    st.header("🔍 Job Match")
    
    # Check if resume is parsed
    if 'parsed_resume' not in st.session_state:
        st.warning("Please upload and parse a resume first!")
        return
    
    # Fetch job listings for matching
    try:
        response = requests.get(f"{BASE_URL}job_listings/")
        
        if response.status_code == 200:
            jobs = response.json()
            
            # Select job for matching
            job_titles = [job.get('title', 'Untitled Job') for job in jobs]
            selected_job_title = st.selectbox("Select a Job to Match", job_titles)
            
            # Find selected job
            selected_job = next((job for job in jobs if job.get('title') == selected_job_title), None)
            
            if st.button("Match Resume"):
                if selected_job:
                    # Prepare matching payload
                    match_payload = {
                        'candidate': dict(st.session_state.parsed_resume),
                        'job': dict(selected_job)
                    }
                    
                    # Send match request
                    match_response = requests.post(
                        f"{BASE_URL}match/", 
                        json=match_payload
                    )
                    
                    if match_response.status_code == 200:
                        # Debugging: print raw response text
                        st.write("Raw Response:", match_response.text)
                        
                        # Try to parse the response
                        try:
                            # Remove surrounding quotes and escape any internal quotes
                            match_result_text = match_response.text.strip('"').replace('\\"', '"')
                            match_result = json.loads(match_result_text)
                        except json.JSONDecodeError as e:
                            st.error(f"JSON Decode Error: {e}")
                            st.error(f"Problematic text: {match_response.text}")
                            return
                        except Exception as e:
                            st.error(f"Failed to parse response: {e}")
                            st.error(f"Response text: {match_response.text}")
                            return
                        
                        # Display match results
                        st.subheader("Match Results")
                        
                        # Safely access match result keys
                        match_score = match_result.get('match_score', 'N/A')
                        missing_skills = match_result.get('missing_skills', [])
                        summary = match_result.get('summary', 'No summary available')
                        
                        st.write(f"**Match Score:** {match_score}/100")
                        
                        st.write("**Missing Skills:**")
                        for skill in missing_skills:
                            st.write(f"- {skill}")
                        
                        st.write(f"**Summary:** {summary}")
                
                else:
                    st.warning("Please select a job")
        else:
            st.error("Failed to fetch job listings for matching")
    
    except Exception as e:
        st.error(f"Error in job matching: {e}")
        # Optional: print full traceback for debugging
        import traceback
        st.error(traceback.format_exc())
        
def generate_cover_letter():
    """
    Cover Letter Generation Section
    """
    st.header("📝 Cover Letter Generator")
    
    # Check if resume is parsed
    if 'parsed_resume' not in st.session_state:
        st.warning("Please upload and parse a resume first!")
        return

    try:
        # Fetch job listings
        response = requests.get(f"{BASE_URL}job_listings/")
        
        if response.status_code == 200:
            jobs = response.json()
            
            # Select job for cover letter
            job_titles = [job.get('title', 'Untitled Job') for job in jobs]
            selected_job_title = st.selectbox("Select Job for Cover Letter", job_titles)
            
            # Find selected job
            selected_job = next((job for job in jobs if job.get('title') == selected_job_title), None)
            
            if st.button("Generate Cover Letter"):
                if selected_job:
                    # Prepare payload exactly matching Postman example
                    cover_letter_payload = {
                        "candidate": {
                            "name": st.session_state.parsed_resume.get('name', 'Applicant'),
                            "skills": st.session_state.parsed_resume.get('skills', []),
                            "work_experience": st.session_state.parsed_resume.get('work_experience', [])
                        },
                        "job": {
                            "title": selected_job.get('title', ''),
                            "company": selected_job.get('company', ''),
                            "required_skills": selected_job.get('required_skills', [])
                        }
                    }
                    
                    # Debug: Print payload
                    st.write("Payload being sent:", json.dumps(cover_letter_payload, indent=2))
                    
                    # Send cover letter generation request
                    try:
                        cover_letter_response = requests.post(
                            f"{BASE_URL}generate_cover_letter/",
                            json=cover_letter_payload,
                            timeout=30
                        )
                        
                        # Debug response
                        st.write(f"Response Status: {cover_letter_response.status_code}")
                        st.write(f"Response Content: {cover_letter_response.text}")
                        
                        if cover_letter_response.status_code == 200:
                            # Parse the response
                            response_data = cover_letter_response.json()
                            cover_letter = response_data.get('cover_letter', '')
                            
                            if cover_letter:
                                st.subheader("Generated Cover Letter")
                                st.text_area("Cover Letter", cover_letter, height=400)
                                
                                # Add download button
                                st.download_button(
                                    label="Download Cover Letter",
                                    data=cover_letter,
                                    file_name=f"Cover_Letter_{selected_job_title}.txt",
                                    mime="text/plain"
                                )
                            else:
                                st.warning("Generated cover letter is empty")
                        else:
                            # More detailed error handling
                            st.error(f"Cover letter generation failed: {cover_letter_response.text}")
                    
                    except requests.exceptions.RequestException as req_error:
                        st.error(f"Network error: {req_error}")
                
                else:
                    st.warning("Please select a job")
        else:
            st.error("Failed to fetch job listings")
    
    except Exception as e:
        st.error(f"Error generating cover letter: {e}")
        import traceback
        st.error(traceback.format_exc())

def list_jobs():
    """
    Comprehensive Job Listings Section with Detailed Filtering and Search
    """
    st.header("💼 Job Listings")
    
    # Fetch job listings
    try:
        response = requests.get(f"{BASE_URL}job_listings/")
        
        if response.status_code == 200:
            jobs = response.json()
            
            # Sidebar for filtering
            st.sidebar.header("🔍 Job Search Filters")
            
            # Collect unique values for filters
            all_companies = sorted(set(job.get('company', 'Unknown') for job in jobs))
            all_skills = sorted(set(skill for job in jobs for skill in job.get('required_skills', [])))
            
            # Filter widgets
            selected_companies = st.sidebar.multiselect(
                "Filter by Companies", 
                options=all_companies, 
                default=[]
            )
            
            
            selected_skills = st.sidebar.multiselect(
                "Filter by Skills", 
                options=all_skills, 
                default=[]
            )
            
            # Search box
            search_term = st.sidebar.text_input("Search Jobs")
            
            # Apply filters
            filtered_jobs = jobs
            
            if selected_companies:
                filtered_jobs = [job for job in filtered_jobs if job.get('company') in selected_companies]
            
            
            if selected_skills:
                filtered_jobs = [
                    job for job in filtered_jobs 
                    if any(skill in job.get('required_skills', []) for skill in selected_skills)
                ]
            
            if search_term:
                filtered_jobs = [
                    job for job in filtered_jobs
                    if search_term.lower() in job.get('title', '').lower() or 
                       search_term.lower() in job.get('description', '').lower()
                ]
            
            # Display job count
            st.write(f"🔢 Total Jobs Found: {len(filtered_jobs)}")
            
            # Job display
            for job in filtered_jobs:
                with st.expander(f"📋 {job.get('title', 'Untitled Job')} at {job.get('company', 'Unknown Company')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Company:** {job.get('company', 'N/A')}")
                        st.write(f"**Location:** {job.get('location', 'N/A')}")
                        st.write(f"**Job Type:** {job.get('job_type', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Salary Range:** {job.get('salary_range', 'Not Disclosed')}")
                        st.write(f"**Posted Date:** {job.get('posted_date', 'N/A')}")
                    
                    st.write("**Job Description:**")
                    st.write(job.get('description', 'No description available'))
                    
                    st.write("**Required Skills:**")
                    skills = job.get('required_skills', [])
                    if skills:
                        skill_cols = st.columns(min(len(skills), 5))
                        for i, skill in enumerate(skills[:5]):
                            skill_cols[i].badge(skill)
                    else:
                        st.write("No specific skills listed")
                    
        
        else:
            st.error("Failed to fetch job listings")
    
    except Exception as e:
        st.error(f"Error fetching job listings: {e}")

def view_match_results():
    """
    Match Results Section
    """
    st.header("📊 Match Results")

    # Fetch match results
    try:
        response = requests.get(f"{BASE_URL}match-results/")
        
        if response.status_code == 200:
            match_results = response.json()
            
            if not match_results:
                st.info("No match results available yet.")
                return
            
            # Display match results
            for result in match_results:
                with st.expander(f"Match Result for {result.get('candidate_name', 'Unknown')} - {result.get('job_title', 'Unknown')}"):
                    st.write(f"**Candidate Name:** {result.get('candidate_name', 'N/A')}")
                    st.write(f"**Job Title:** {result.get('job_title', 'N/A')}")
                    st.write(f"**Company:** {result.get('company', 'N/A')}")
                    st.write(f"**Match Score:** {result.get('match_score', 'N/A')}%")
                    st.write("**Missing Skills:**")
                    
                    missing_skills = result.get('missing_skills', [])
                    if missing_skills:
                        for skill in missing_skills:
                            st.write(f"- {skill}")
                    else:
                        st.write("✅ No missing skills!")
                    
                    st.write(f"**Summary:** {result.get('summary', 'No summary available')}")
        
        else:
            st.error("Failed to fetch match results")
    
    except Exception as e:
        st.error(f"Error fetching match results: {e}")


def main():
    """
    Main Streamlit Application
    """
    st.title("🚀 Job Application Assistant")
    
    # Sidebar for navigation
    menu = ["Resume Upload", "Job Listings", "Job Match", "Match Results","Cover Letter Generator"]
    choice = st.sidebar.selectbox("Navigation", menu)
    
    # Routing based on sidebar selection
    if choice == "Resume Upload":
        upload_resume()
    elif choice == "Job Listings":
        list_jobs()
    elif choice == "Job Match":
        match_resume_to_jobs()
    elif choice == "Match Results":
        view_match_results()
    elif choice == "Cover Letter Generator":
        generate_cover_letter()

if __name__ == "__main__":
    main()
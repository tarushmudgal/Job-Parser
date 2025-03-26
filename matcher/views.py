from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MatchResult, CandidateProfile, JobPosting
import json 
from rest_framework import status
from .utils import parse_resume, match_candidate_to_job, parse_job_posting, generate_cover_letter
from django.core.files.storage import default_storage
from .serializers import JobPostingSerializer

class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES["resume"]
        file_path = default_storage.save(file.name, file)
        file_type = file.name.split(".")[-1]

        parsed_data = parse_resume(file_path, file_type)
        return Response(parsed_data)


class JobParsingView(APIView):
    def post(self, request):
        job_text = request.data.get("job_text", "")
        if not job_text:
            return Response({"error": "Job description missing"}, status=400)
        
        parsed_job = parse_job_posting(job_text)
        return Response(parsed_job)
 

class MatchView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            candidate_data = request.data.get("candidate", {})
            job_data = request.data.get("job", {})

            candidate_name = candidate_data.get("name", "").strip()
            job_title = job_data.get("title", "").strip()
            company_name = job_data.get("company", "").strip()

            if not candidate_name:
                return Response({"error": "Candidate name is missing!"}, status=status.HTTP_400_BAD_REQUEST)
            if not job_title or not company_name:
                return Response({"error": "Job title or company name is missing!"}, status=status.HTTP_400_BAD_REQUEST)

            #  Find Candidate (Use Name as Unique Identifier)
            candidate, created = CandidateProfile.objects.get_or_create(
                name=candidate_name,
                defaults={
                    "skills": candidate_data.get("skills", []),
                    "education": candidate_data.get("education", []),
                    "work_experience": candidate_data.get("work_experience", []),
                    "resume_file": candidate_data.get("resume_file", None),
                }
            )

            #  Find Job (Use Title + Company as Unique Identifier)
            job, created = JobPosting.objects.get_or_create(
                title=job_title,
                company=company_name,
                defaults={
                    "required_skills": job_data.get("required_skills", []),
                    "description": job_data.get("description", ""),
                }
            )

            #  Call Matching Logic
            match_result = match_candidate_to_job(candidate_data, job_data)
            print("Raw match_result:", match_result) 

            if isinstance(match_result, str):  
                match_result = json.loads(match_result)  

            match_score = match_result.get("match_score", 0)
            missing_skills = match_result.get("missing_skills", [])  
            summary = match_result.get("summary", "No summary available")

            if not isinstance(missing_skills, list):
                missing_skills = [missing_skills]  

            # ✅ Save to database (Ensure candidate and job are linked)
            match_entry = MatchResult.objects.create(
                candidate=candidate,
                job=job,
                match_score=match_score,
                missing_skills=missing_skills,
                summary=summary
            )

            return Response({
                "match_score": match_entry.match_score,
                "missing_skills": match_entry.missing_skills,
                "summary": match_entry.summary,
                "candidate_name": candidate.name,
                "job_title": job.title,
                "company": job.company
            }, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            return Response({"error": f"JSON Decode Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            import traceback
            print(traceback.format_exc())  
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CoverLetterView(APIView):
    def post(self, request):
        candidate = request.data.get("candidate")
        job = request.data.get("job")

        if not candidate or not job:
            return Response({"error": "Candidate and job data are required."}, status=400)

        cover_letter = generate_cover_letter(candidate, job)
        return Response({"cover_letter": cover_letter})


class JobListView(APIView):
    def get(self, request):
        jobs = JobPosting.objects.all().values()
        return Response(list(jobs), status=status.HTTP_200_OK)

    
class AddJobView(APIView):
    def post(self, request):
        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class MatchResultListView(APIView):
    def get(self, request):
        matches = MatchResult.objects.select_related('candidate', 'job').all()

        match_results = []
        for match in matches:
            match_results.append({
                "candidate_name": match.candidate.name if match.candidate else "N/A",
                "job_title": match.job.title if match.job else "N/A",
                "company": match.job.company if match.job else "N/A",
                "match_score": match.match_score,
                "missing_skills": match.missing_skills,
                "summary": match.summary,
                "created_at": match.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return Response(match_results, status=status.HTTP_200_OK)

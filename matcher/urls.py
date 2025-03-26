# matcher/urls.py
from django.urls import path
from .views import ResumeUploadView, MatchView, JobParsingView, CoverLetterView, JobListView, AddJobView, MatchResultListView

urlpatterns = [
    path("upload_resume/", ResumeUploadView.as_view(), name="upload_resume"),
    path("match/", MatchView.as_view(), name="match"),
    path("parse_job/", JobParsingView.as_view(), name="parse_job"),
    path("generate_cover_letter/", CoverLetterView.as_view(), name="generate_cover_letter"),
    path('job_listings/', JobListView.as_view(), name='job_listings'),
    path('add_job/', AddJobView.as_view(), name='add_job'),
    path('match-results/', MatchResultListView.as_view(), name='match-results'),
]

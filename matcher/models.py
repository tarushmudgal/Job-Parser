from django.db import models

class CandidateProfile(models.Model):
    name = models.CharField(max_length=255)
    skills = models.JSONField()  # Store skills as a list
    education = models.JSONField()
    work_experience = models.JSONField()
    resume_file = models.FileField(upload_to="resumes/")

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    required_skills = models.JSONField()
    description = models.TextField()

    def __str__(self):
        return self.title
    
class MatchResult(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    match_score = models.IntegerField()
    missing_skills = models.JSONField(default=list)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title} ({self.match_score}%)"


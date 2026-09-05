from django.db import models


class CandidateProfile(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)
    extra_instructions = models.TextField(blank=True, default='')

    def __str__(self) -> str:
        return self.phone_number

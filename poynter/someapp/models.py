from django.db import models


class Dummy(models.Model):
    title = models.CharField(max_length=50, default="I am a record")
    attachment = models.FileField(
        max_length=256,
        upload_to="attachments",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id} - {self.title}"

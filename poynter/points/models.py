import requests
from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import AutoSlugField


class Project(TimeStampedModel):
    """Voting Sessions are associated with projects within the organization."""

    name = models.name = models.CharField(
        max_length=120,
        help_text="A project title within the organization.",
    )

    def __str__(self):
        return f"{self.name}"


class Vote(TimeStampedModel):
    """One user's vote on one ticket."""

    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(help_text="Numerical vote up to 2 digits")

    def __str__(self):
        return f"'{self.voter}' on {self.created.strftime('%A, %d %B, %Y at %X')}"


class Space(TimeStampedModel):
    """A space is a meeting locations owned by a combination of one moderator in one project.
    A permanent URL goes with each space. Results of voting sessions are captured as JSON documents
    for posterity.
    A PointingSession has a moderator and a collection of tickets.
    TODO: Allow NOW or arbitrary date
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from=["project", "moderator"])
    is_open = models.BooleanField(help_text="Voting is currently open", default=False)

    def __str__(self):
        return f"{self.moderator.username}: {self.project}"

    class Meta:
        unique_together = [
            (
                "project",
                "moderator",
            )
        ]


class Ticket(TimeStampedModel):
    """A ticket reference (e.g. to Jira), to be stored in a PointingSession and voted upon by users."""

    url = models.URLField(help_text="Link into ticket system", verbose_name="URL")
    title = models.name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Extracted automatically if possible, or populate manually.",
    )
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    active = models.BooleanField(
        help_text=(
            "The active ticket for this project is the one being voted on. "
            "Only one ticket may be marked active per voting session at a time."
        ),
        null=True,
        default=False,
    )

    def __str__(self):
        return f"{self.pk}: {self.title}"

    def save(self, *args, **kwargs):
        """
        Also, try to populate the title automatically.
        If we can't get to the remote system, we can still enter the title manually."""

        if not self.title:
            page = requests.get(self.url)
            text = page.text
            self.title = text[text.find("<title>") + 7 : text.find("</title>")]
        return super(Ticket, self).save(*args, **kwargs)

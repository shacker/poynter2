import requests
from django.conf import settings
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel


class Project(TimeStampedModel):
    """Voting Sessions are associated with projects within the organization."""

    name = models.name = models.CharField(
        max_length=120,
        help_text="A project title within the organization.",
    )

    def __str__(self):
        return f"{self.name}"


class Space(TimeStampedModel):
    """A space is a meeting location for one moderator in one project.
    Each Space has a permanent URL. Results of voting sessions are captured as JSON documents.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from=["project", "moderator"])
    is_open = models.BooleanField(help_text="Voting is currently open", default=False)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text="Users who have joined this space.",
        related_name="members",
    )

    def __str__(self):
        return f"{self.moderator.username}: {self.project}"

    class Meta:
        unique_together = [
            (
                "project",
                "moderator",
            )
        ]


class Snapshot(TimeStampedModel):
    """When voting is closed for a space, automatically save voting snapshot
    as a JSONField for posterity.
    """

    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    snapshot = models.JSONField(
        default=dict, blank=True, help_text="Capture state of voting when Space is closed."
    )

    def __str__(self):
        return f"{self.space.slug}: {self.created}"


class Ticket(TimeStampedModel):
    """A ticket reference (e.g. to Jira),
    to be stored in a PointingSession and voted upon by users."""

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
    closed = models.BooleanField(
        help_text=("Moderator has marked voting complete for this ticket."),
        default=False,
    )
    archived = models.BooleanField(
        help_text=("Tickets from former sessions don't appear on board at all, but we keep them."),
        default=False,
    )

    def __str__(self):
        return f"{self.pk}: {self.title}"

    def save(self, *args, **kwargs):
        """
        Also, try to populate the title automatically.
        If we can't get to the remote system, we can still enter the title manually."""

        if not self.title:
            page = requests.get(self.url, timeout=15)
            text = page.text
            self.title = text[text.find("<title>") + 7 : text.find("</title>")]
        return super(Ticket, self).save(*args, **kwargs)

    class Meta:
        ordering = [
            "id",
        ]


# TODO temporary
class BroadcastMessage(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

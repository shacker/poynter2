import logging

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from faker import Faker

from poynter.points.models import Project, Space, Ticket

log = logging.getLogger(__name__)

fake = Faker()


"""One-time script demo. Run with:

./manage.py runscript 0000_hopper --script-args live  # Makes live changes to data
"""


projects = ["Iris", "Cosmos", "Greenhouse", "TPR"]
users = ["joe", "amshar", "gkaleka", "shacker", "rob"]
moderators = ["shacker", "rob"]


def run(*args):
    #  Set up dummy data to work with locally and in tests
    if "live" in args:

        # Make users and moderators
        for username in users:
            try:
                user = User.objects.create_user(username=username, is_staff=True)
            except IntegrityError:
                pass

        for proj in projects:
            project, created = Project.objects.get_or_create(name=proj)

            for mod in moderators:
                user = User.objects.get(username=mod)
                try:
                    Space.objects.get_or_create(moderator=user, project=project, is_open=True)
                except IntegrityError:
                    pass

            # Normal users with spaces here too?

        # Make tickets in one space - these are what we'll mostly work with.
        proj = Project.objects.get(name="Cosmos")
        mod = User.objects.get(username="shacker")
        space = Space.objects.get(moderator=mod, project=proj)
        Ticket.objects.filter(space=space).delete()

        for x in range(5):
            # Using manual ticket titles here, not extracting automatically
            ticket = Ticket.objects.create(
                url="http://example.com", title=fake.sentence().strip("."), space=space
            )
        # Set last ticket to active
        ticket.active = True
        ticket.save()

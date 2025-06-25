from django.core.cache import cache
from django.http import HttpResponse


def tally_single(request):
    """HTMX view receives POST from a voting space, and logs
    the space name, username, and vote.


    space_key = {

    }
    """
    if request.method == "POST":
        data = request.POST

        username = data.get("username")
        vote = data.get("number")
        space = data.get("space")
        ticket = data.get("ticket")

        # To allow user to override their vote, write every time
        cache_key = f"{space}_{username}_{ticket}"
        vote_data = {"space": space, "username": username, "ticket": ticket, "vote": vote}
        cache.set(cache_key, vote_data)

    # retrieved = cache.get("space_*")

    return HttpResponse(status=204)  # Do nothing

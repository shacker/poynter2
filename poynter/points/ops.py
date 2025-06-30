from collections import defaultdict

from django.core.cache import cache


def get_votes_for_space(space_name: str) -> dict:
    """
    Get all votes for current workspace with computed averages appended.
    Average may not fit an existing Fibonacci number - up to moderator
    to assign final average from returned value. Ticket db IDs are keys in
    this dict.

    {
        8: {
            "rob": 3,
            "joe": 2,
        },
        17: {
            "rob": 8,
            "erin": 3,
        }
    }

    append averages as a final dict:
    {
        "averages": {
            8: 2.5,
            17: 5.5
        }
    }

    """

    avgs = {}
    data = cache.get(space_name, defaultdict(dict))
    for key in data.keys():
        vals = data[key].values()
        avg = sum(vals) / len(vals)
        avgs[key] = avg

    data["averages"] = avgs

    # default_dict is unhashable - cast back
    return dict(data)

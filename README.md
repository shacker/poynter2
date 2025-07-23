# WRITE THIs

There is ONE active ticket at a time.
Until all have been voted on , then there are none
Moderators can open or close a ticket at any time
Moderator can switch the active ticket at any time.
Moderator is told whether all votes are in or not

Each space has one moderator. No special roles or permissiosn are needed - just associate space with user

We don't auto-advance to next ticket because people want to look at who just voted AND the moderator has their reasons for picking the next active ticket.

Different things:
ticket.active - this one is currenly being voted on by group
ticket.closed - moderator has closed ticket, usually after everyone voted
ticket.archived - from last week - still in db but not shown on page at all



User joins each session to which they sometimes contribute. If a user appears in Voting Members but is not present one day, the moderator can remove them, and user can re-join next time they're available.


Start daphne with
daphne poynter.config.asgi:application


### Moderator Instructions

- One time: Request that a Space be created for you in the Admin, associated with a given project. The URL for this space will be essentially permanent.

- From the front page, access the space. As the moderator, you will have access to the Moderator Tools table for this space.

- Click Add Ticket and paste in the URL of a ticket to be pointed. The ticket title will be retrieved automatically, if possible. However, Jira does not support standard methods for this - you must enter ticket titles for Jira tickets manually. Continue adding as many tickets as you want to be voted on in the next session.

- Control which ticket is voted on next (now) by clicking the "Make Active" link.

- When you are ready for voting to begin, click "Open voting space"

- When voting is done, optionally click Close voting space

- Provide the space URL to your members and instruct them to log in and click "Join" at the right of the space. As moderator, you can remove any joined members who are not present in a given session.

- When all votes are in for a given ticket, or you simply want to close voting, click Close Voting Space. Closing a space saves all votes to a snapshot, and keeps them available to viewers.

- When you are ready to wipe the slate clean and prepare for the next voting session click Archive Current Tickets for a fresh start. Archived tickets will be saved, but not displayed on the voting board.

- You can manually open or close a single ticket as needed.



Note: While a moderator is techically a "member" of a space, only users who have specifically joined a space can vote. This way, moderators can decide on a per-space basis whether they should also be allowed to vote.


There are three real-time htmx views in this project:

1) Moderator can send a text message alert to everyone in a space (room)
2) When moderator upates the tickets list, it's updated for all watchers in that space
    (we actually have to update two things: The list of tickets AND the "Active Ticket" display)
3) When any member votes, the view of who has voted changes for everyone


### Shared content and the broadcast model

Traditional: I see what I see because I click what I click
Channels: We all see the same thing because a moderator e.g. made a change for everyone, or someone typed into a chat and we all see it.
What we can't do: A channel update is sent but each recipient gets different content, e.g. based on permssions.

We initially enabled a "unicast" approach that would hand the request off to each user of a space, but turned it off due to complexities and the fact that for a popular space, it would spike the query count and potentially cause delays. Hence the separate "Ticket Control" panel for moderators.

### Ticket Control Panel

Moderators only see this panel:

[screenshot]

which allows them to quickly turn tickets on or off from this session, and make any ticket the currently active ticket. This is a separate panel to avoid needing complex solutions for filtering content and permissions inside the broadcast model.

Explain diff bw broadcast and unicast
For example, if the code says `if user in members.space.all` you might be surprised to find that {{user}} evaluates to the moderator's username rather than your username since the moderator last clicked the buttons that updated that widget, using the usual `broadcast` mode which gives everyone the same html in their widget. To solve this, we need to update that one via unicast - that just sends a trigger to all clients, which they can catch and update the widget via their own request. That's more expensive, but essential when dealing with individual user differences that shouldn't be cross-contaminated in code. So to make unicast work, we do two things:

1)


2) In the widget, modify the hx-trigger to be activated both on page load AND when it receives the trigger "refresh" (since we're not broadcsating to it, this is how it knows to refresh itself via the client):
```
<div
    hx-get="{% url 'points:display_voting_row' space.slug %}"
    hx-trigger="load, refresh"
    class="display_voting_row"
    id="display_voting_row">
</div>
```


DEMO:


Member view
- Could start with homepage, or permanent URL

Moderator view
- Follow moderator instructions above to get set up
Multiple users at once
Admin tour
Snapshots
get_votes_for_space

Channels overview and tour of channels components
Tour of HTMX components

Talk about spaces (rooms). One for each project/moderator. Untested but should work!

Start with global page vars, then move to widget-level vars, then pretty soon you realize those aren't being updated because you're no longer redrawing the whole page, so you have to widgetize EVERYthing.
In for a penny, in for a pound.

Show two kinds of functions in htmx_views.py - views for partials, and helper ops that do some logic and then force a redraw of one or more widgets.

Future: Demo updating just one widget, not all of them

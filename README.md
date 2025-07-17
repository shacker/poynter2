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

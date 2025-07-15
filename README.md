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

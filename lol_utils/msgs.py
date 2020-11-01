from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$lol mastery [a-zA-Z]{2,4} .{1,16}', botutils.lol_masteries,
            description='Graph champion mastery for a player')
]

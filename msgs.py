"""
Holds patterns to match message to function
"""
from routing.mapper import Pattern
import botutils


msgpatterns = [
    Pattern(r'^\$poll (\d{1,4}) (.+)', botutils.poll,
            description='Poll function'),

    Pattern(r'^\$word (\d{1,308})( [a-zA-Z_]{0,5})?',
            botutils.num_convert_word,
            description='Converting a number to a word'),

    Pattern(r'^\$reminder (\d+) (.+)', botutils.reminder,
            description='Setting reminders with the reminder function'),

    Pattern(r'^\$toggleyeet$', botutils.autoyeet_toggle,
            description='Toggles spamming the chat with "YEET!"'),
]

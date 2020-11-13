from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$ai gender [a-zA-Z]{1,16}$', botutils.predict_gender,
            description='Guess the gender of a name'),

    Pattern(r'^\$ai model gender$', botutils.get_summary,
            description='Show the architecture of the model'),

    Pattern(r'^\$ai modelv gender$', botutils.get_visualisation,
            description='Show the architecture of the model visually'),
]

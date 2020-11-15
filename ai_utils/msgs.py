from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$ai gender [a-zA-Z]{1,16}$', botutils.predict_gender,
            description='Guess the gender of a name'),

    Pattern(r'^\$ai model gender$', botutils.get_summary_gender,
            description='Show the architecture of the model'),

    Pattern(r'^\$ai modelv gender$', botutils.get_visualisation_gender,
            description='Show the architecture of the model visually'),

    Pattern(r'^\$ai digit', botutils.predict_digit,
            description='Guess the digit in the image'),

    Pattern(r'^\$ai model digit$', botutils.get_summary_digit,
            description='Show the architecture of the model'),

    Pattern(r'^\$ai modelv digit', botutils.get_visualisation_digit,
            description='Show the architecture of the model visually'),
]

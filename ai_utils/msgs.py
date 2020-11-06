from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$ai gender [a-zA-Z]{1,16}$', botutils.predict_gender,
            description='Guess the gender of a name'),
]

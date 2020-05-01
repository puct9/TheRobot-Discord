from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$c4 new$', botutils.new_game,
            description='Force initiate a new game'),

    Pattern(r'^\$c4 test$', botutils.test,
            description='test'),

    Pattern(r'^\$c4 load$', botutils.load_game,
            description='Show the current game'),

    Pattern(r'^\$c4 move ([A-Ga-g])$', botutils.process_move,
            description='Enter move'),

    Pattern(r'^\$c4 go$', botutils.ai_move,
            description='Make the AI play a move')
]

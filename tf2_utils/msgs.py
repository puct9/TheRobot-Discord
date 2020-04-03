from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$tf2$', botutils.get_player_info,
            description='Team Fortress 2 server player info')
]

from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$osu user .+', botutils.osu_userinfo,
            description='Get the stats for an Osu! player')
]

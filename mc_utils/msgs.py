from routing.mapper import Pattern
from . import botutils


msgpatterns = [
    Pattern(r'^\$mc up$', botutils.is_server_up,
            description='Is the Minecraft SkyFactory server up?')
]

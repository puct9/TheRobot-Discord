def parse_game_info(info):
    players = []
    while info:
        # read name
        # read until \x00
        split = info.split(b'\x00')
        info = b'\x00'.join(split[1:])
        name = split[0]
        read_mode = 2

        # read score
        score_len = 0
        for c in info:
            # as we loop through the bytes c will be an int
            if c == 0:
                break
            score_len += 1
        score_len = max(1, score_len)
        score_bytes = info[:score_len]
        info = info[score_len + 8:]
        score_int = 0
        for pos, byte in enumerate(score_bytes):
            score_int |= byte << pos * 8
        players.append((name.decode(), score_int))

    return [e for e in sorted(players, key=lambda x: x[1], reverse=True)
            if e[0]]

from utils import Constants
import time


def get_coefficient(_time):
    if _time < Constants.DAY:
        return 1
    elif _time < Constants.DAY * 2:
        return 0.8
    elif _time < Constants.DAY * 3:
        return 0.6
    elif _time < Constants.DAY * 4:
        return 0.4
    elif _time < Constants.DAY * 5:
        return 0.2
    else:
        return 0


def rank_poll(poll):
    answers = poll.answers.all()
    rank = 0
    for ans in answers:
        c = get_coefficient(time.time() * 1000 - ans.timestamp)
        rank += c
    return rank

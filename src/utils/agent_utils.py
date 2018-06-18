from user_agents import parse
from utils.Constants import WEB, IOS, ANDROID


def get_agent(ua_string):
    try:
        user_agent = parse(ua_string)
        if user_agent.is_pc:
            return WEB
        elif user_agent.is_mobile:
            if user_agent.os.family == 'iOS':
                return IOS
            elif user_agent.os.family == 'Android':
                return ANDROID
            return IOS
        else:
            return WEB
    except Exception as e:
        # TODO: add logger
        return WEB

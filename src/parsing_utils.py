import re


def message_parser_user(message, users):
    # return True if we should delete the message
    if message["author"]["id"] in users:
        return message["author"]["id"]
    return False


def message_parser_regex(message, regex):
    # return True if we should delete the message
    regex_found = re.findall(regex, message["content"].lower())
    if len(regex_found) == 0:
        return False
    return regex_found


def message_parser_regexuser(message, users, regex):
    # return True if we should delete the message
    if message["author"]["id"] in users:
        regex_found = re.findall(regex, message["content"].lower())
        if len(regex_found) == 0:
            return False
        return regex_found
    return False

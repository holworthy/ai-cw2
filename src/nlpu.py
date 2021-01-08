import re
import spacy

def get_times(message):
    times = (re.findall("^.*([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9].*$", message))
    if len(times) == 0:
        return False
    return times
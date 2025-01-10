import re
TONES = {
    "a": "āáǎàa",
    "A": "ĀÁǍÀA",
    "e": "ēéěèe",
    "E": "ĒÉĚÈE",
    "i": "īíǐìi",
    "I": "ĪÍǏÌI",
    "o": "ōóǒòo",
    "O": "ŌÓǑÒO",
    "u": "ūúǔùu",
    "U": "ŪÚǓÙU",
    "v": "ǖǘǚǜü",
    "V": "ǕǗǙǛÜ"
}


def pinyin_converter(match: re.Match) -> str:
    s = match[0]
    idx = int(s[-1])-1
    if len(s) == 2:
        return TONES[s[0]][idx]
    # Special rules
    tmp = s.lower()
    if "a" in tmp:
        loc = tmp.find("a")
    elif "e" in tmp:
        loc = tmp.find("e")
    elif "ou" in tmp:
        loc = tmp.find("o")
    else:
        if tmp[-2] in "aeiouv":
            loc = len(s)-2
        elif tmp[-3] in "aeiouv":
            loc = len(s)-3
        else:
            loc = len(s)-4
    
    new_s = s[:loc] + TONES[s[loc]][idx] + s[loc+1:]
    return new_s[:-1]



def convert_to_pinyin(s: str) -> str:
    """
    Converts s to use pinyin accents.
    """
    return re.sub("[aeiouvAEIOUV]{1,2}[qwrtypsdfghjklzxcvbnm]{0,2}[1234]", pinyin_converter, s)


if __name__ == "__main__":
    print(convert_to_pinyin("Ni3 hao3! Hen3hao3 zheng4"))
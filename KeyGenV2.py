

import string
import secrets
import random

SOUP_POT = [string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
            string.punctuation]

vectors = [2, 3, 3, 4]
length_var = 4

random.shuffle(vectors)


def _make_soup():
    soup = ''
    for run, vector in enumerate(vectors):
        for _ in range(vector):
            soup += secrets.choice(SOUP_POT[run])
    return soup


def _extra_soup(var):
    more_soup = ''
    for _ in range(secrets.randbelow(var + 1)):
        more_soup += secrets.choice(SOUP_POT[secrets.randbelow(len(vectors))])
    return more_soup


def key_gen():
    password = _make_soup() + _extra_soup(length_var)
    password = "".join(random.sample(password, len(password)))
    return password

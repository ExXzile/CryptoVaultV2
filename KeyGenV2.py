import random

lower_keys = "abcdefghijklmnopqrstuwvxyz"
upper_keys = "ABCDEFGHIJKLMNOPQRSTUWVXYZ"
numbers = "1234567890"
spec_chars = r'!"#$%&\'()*+,-./:;<=>?[]^_`|~'

soup_pool = [lower_keys,
             upper_keys,
             numbers,
             spec_chars]

vectors = [2, 3, 3, 4]
length_var = 4

random.shuffle(vectors)


def _make_soup():
    soup = ''
    for vector in vectors:
        for n in range(vector):
            soup += random.choice(soup_pool[n - 1])
    return soup


def _extra_soup(var):
    more_soup = ''
    for n in range(random.randrange(var + 1)):
        more_soup += random.choice(soup_pool[random.randrange(3)])
    return more_soup


def key_gen():
    password = _make_soup() + _extra_soup(length_var)
    password = "".join(random.sample(password, len(password)))
    return password



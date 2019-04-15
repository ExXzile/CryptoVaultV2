import random

_lower_keys = 'abcdefghijklmnopqrstuwvxyz'
_upper_keys = 'ABCDEFGHIJKLMNOPQRSTUWVXYZ'
_numbers = '1234567890'
_spec_chars = r'!"#$%&\'()*+,-./:;<=>?[]^_`|~'

_vector = [2, 3, 3, 4]
random.shuffle(_vector)


def key_gen():
    password = ''
    for _ in range(_vector[0]):
        password += random.choice(_lower_keys)
    for _ in range(_vector[1]):
        password += random.choice(_upper_keys)
    for _ in range(_vector[2]):
        password += random.choice(_numbers)
    for _ in range(_vector[3]):
        password += random.choice(_spec_chars)

    password = ''.join(random.sample(password, len(password)))
    return password

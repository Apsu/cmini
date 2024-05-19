import string
from typing import Dict

# Bot triggers
TRIGGERS = ['!amini', '!bmini', '!cmini', '!dvormini', '!cnini']

# Json type
JSON = Dict[str, any]

# punctuation chars
PUNCT = '()";:,.?!'

# Set of allowed characters
NAME_SET = set(
    string.ascii_letters +
    string.digits +
    " _-'():~"
)

# letter to indicate an empty space
FREE_CHAR = '~'

# letters that must be included on a layout
LETTERS = list('abcdefghijklmnopqrstuvwxyz,.\'')

# row map for standard
FMAP_STANDARD = ['LP', 'LR', 'LM', 'LI', 'LI', 'RI', 'RI', 'RM', 'RR', 'RP']

# row map for angle
FMAP_ANGLE = ['LR', 'LM', 'LI', 'LI', 'LI', 'RI', 'RI', 'RM', 'RR', 'RP']

# finger values as numbers
FINGER_VALUES = {
    'LP': 0,
    'LR': 1,
    'LM': 2,
    'LI': 3,
    'RI': 4,
    'RM': 5,
    'RR': 6,
    'RP': 7, 
    'LT': 8,
    'RT': 9,
    'TB': 9
}

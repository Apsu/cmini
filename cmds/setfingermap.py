from discord import Message

from util import layout, memory, parser
from util.consts import *
from util.returns import *

def exec(message: Message):
    name, string = parser.get_layout(message)
    id = message.author.id
    ll = memory.find(name.lower())

    ll_str = layout.get_matrix_str(ll)
    rows_matrix = [row.replace(' ', '').replace(FREE_CHAR, '') for row in ll_str.split('\n') if row.strip()]
    rows_string = [row.replace(' ', '').replace(FREE_CHAR, '') for row in string.split('\n') if row.strip()]

    if not all(len(row_matrix) == len(row_string) for row_matrix, row_string in zip(rows_matrix, rows_string)) or len(rows_matrix) != len(rows_string):
        return 'Error: improper finger matrix shape provided'

    rows = string.split('\n')

    board = board_value(rows)

    if not board:
        return 'Error: board shape is undefined'

    if not is_rows_valid(string, board=board):
        return 'Error: improper number of rows in matrix definition'

    rows = [x.strip() for x in rows] # remove leading/trailing whitespace

    fingermatrix = {}
    for r, row in enumerate(rows):
        for c, finger in enumerate(row.split()):
            key = next((k for k, v in ll.keys.items() if v.row == r and v.col == c), None)
            if key:
                if r <= 3 and finger in {'8', '9'}:
                    return f'No thumb values are allowed on rows 1-3.'
                if r > 3 and finger not in {'8', '9'}:
                    return f'Only thumb values are allowed on row {r + 1}.'
                fingermatrix[key] = finger_value(finger)

    for key, finger in fingermatrix.items():
        if key != FREE_CHAR and finger == FREE_CHAR:
            return f'Error: cannot provide empty finger value for {key}'
        ll.keys[key].finger = finger

    if not memory.remove(ll.name, id=id):
        return f'Error: you don\'t own a layout named `{ll.name}`'

    ll.board = board
    memory.add(ll)

    return f'Success!\n' + layout.fingermap_to_string(ll)

def use():
    return 'setfingermap [layout name] [FINGERMATRIX]'

def desc():
    return 'set the fingermap of a layout'

def is_rows_valid(string: str, *, board: str) -> bool:
    rows = string.split('\n')

    if board in ['ortho', 'mini']:
        max_rows = 4
    else:
        max_rows = 3

    return len(rows[1:]) <= max_rows

def board_value(rows):
    # calculate amount of leading whitespace for each row
    spaces = []
    for row in rows:
        size = len(row) - len(row.lstrip())
        spaces.append(size)

    # Determine board type with leading whitespace
    if spaces[0] < spaces[1] < spaces[2]:
        return 'stagger'
    elif spaces[0] == spaces[1] and spaces[2] > 1:
        return 'mini'
    elif spaces[0] == spaces[1] < spaces[2]:
        return 'angle'
    elif spaces[0] == spaces[1] == spaces[2]:
        return 'ortho'
    else:
        return

def finger_value(finger):
    replacements = {
        '0': 'LP',
        '1': 'LR',
        '2': 'LM',
        '3': 'LI',
        '4': 'RI',
        '5': 'RM',
        '6': 'RR',
        '7': 'RP',
        '8': 'LT',
        '9': 'RT'
    }
    for k, v in replacements.items():
        finger = finger.replace(k, v)
    return finger.strip()

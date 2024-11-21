from typing import Tuple
from discord import Message
from util.consts import TRIGGERS
from typing import Type, Any

def get_arg(message: Message) -> str:
    args = message.content.split()

    return ' '.join(args[2:] if args[0] in TRIGGERS else args[1:])


def get_args(message: Message) -> list[str]:
    args = message.content.split()
    return args[2:] if args[0] in TRIGGERS else args[1:]


def get_layout(message: Message) -> Tuple[str, str]:
    tokens = message.content.split('```')

    args = tokens[0].split()
    name = '-'.join(args[2:] if args[0] in TRIGGERS else args[1:]).lower()
    lines = [line for line in tokens[1].splitlines() if line.strip() != '']
    min_space = min(len(line) - len(line.lstrip()) for line in lines)
    matrix = '\n'.join([line[min_space:] for line in lines])

    return name, matrix

def get_kwargs(message: Message,
               arg_type: Type[str | list[str]],
               **cmd_kwargs: Type[bool | list | str],
               ) -> tuple[dict[str, str | bool | list[str]],
                          ValueError | None]:
    """
    - message: user's message list[str]
    - arg type: str or list[str]
    - kwargs: arguments with `--` prefix (or `—`, `––`)
    - kwargs type: bool or list (of str)
    - example:
        ```
        # message.content == "this is args --flag this is ignored --text this is kwargs"
        kwargs = get_kwargs(message, str, flag=bool, text=list)
        assert kwargs == {"args": "this is args", "flag": True, "text": ["this", "is", "kwargs"]}
        ```
    - reserved names (CANNOT be kwarg names): `message`, `arg_type`, `args`
    """
    message_as_list = message.content.split()
    command: list[str] = message_as_list[2:] if message_as_list[0] in TRIGGERS else message_as_list[1:]

    words: list[str] = command
    arg_index = 0
    for word in words:
        _is_kwarg, err = is_kwarg_strict(cmd_kwargs, word)
        if err is not None:
            return {}, err

    for word in words:
        if is_kwarg(cmd_kwargs, word):
            break
        arg_index += 1

    # make default dict
    args = words[:arg_index]
    parsed_kwargs: dict[str, str | bool | list[str]] = {'args': ' '.join(args) if arg_type == str else args}
    for kw_name, kw_type in cmd_kwargs.items():
        parsed_kwargs[kw_name] = (False if kw_type == bool
                                  else [] if kw_type == list
                                  else '')

    words = words[arg_index:]
    last_in_list = 0
    last_kwarg_type = list
    last_list_kwarg = ''
    in_list = False
    for index, word in enumerate(words):
        if is_kwarg(cmd_kwargs, word):
            word = remove_kw_prefix(word)
            kw_type = cmd_kwargs[word]

            # Encountered next keyword, stops previous list
            if in_list:
                parsed_kwargs[last_list_kwarg] = (words[last_in_list:index] if last_kwarg_type == list
                                                  else ' '.join(words[i] for i in range(last_in_list, index)))

            in_list = kw_type == list or kw_type == str
            parsed_kwargs[word] = [] if in_list else True

            # Starts a new list after kwarg
            if in_list:
                last_kwarg_type = kw_type
                last_list_kwarg = word
                last_in_list = index + 1

    # Close the last list
    if in_list:
        parsed_kwargs[last_list_kwarg] = (words[last_in_list:] if last_kwarg_type == list
                                          else ' '.join(words[i] for i in range(last_in_list, len(words))))

    return parsed_kwargs, None

# checks double hyphen, em dash, double en dash
def starts_with_kw_prefix(word: str) -> bool:
    return any(word.startswith(prefix) for prefix in ('--', '—', '––'))

def remove_kw_prefix(word: str) -> str:
    for prefix in ('--', '—', '––'):
        word = word.removeprefix(prefix)
    return word.lower()

def is_kwarg_strict(kwargs: dict[str, Any], word: str) -> tuple[bool, ValueError | None]:
    if not starts_with_kw_prefix(word):
        return False, None
    word = remove_kw_prefix(word)
    if word in kwargs:
        return True, None
    return False, ValueError(f"Error: invalid kwarg: `{word}`")

def is_kwarg(kwargs: dict[str, Any], word: str) -> bool:
    if not starts_with_kw_prefix(word):
        return False
    word = remove_kw_prefix(word)
    return word in kwargs

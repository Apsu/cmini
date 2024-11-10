from discord import Message
from importlib import import_module

from util import layout, memory, parser
from core.keyboard import Layout

RESTRICTED = False

def exec(message: Message):
    kwargs, err = parser.get_kwargs(message, str, angle=bool, unangle=bool, mirror=bool, cycle=list, swap=list)
    if err is not None:
        return (f'{str(err)}\n'
                f'```\n'
                f'{use()}\n'
                f'```')
    layout_name = kwargs['args']
    if not layout_name:
        return f'```\n{use()}\n```'

    ll = memory.find(layout_name.lower())
    
    if kwargs['angle'] and kwargs['unangle']:
        kwargs['angle'] = False  # `--angle --unangle` defaults to unanglemodded

    kwargs['cycle'].extend(kwargs['swap'])  # combine cycle with swap alias

    try:
        if kwargs['angle']:
            __modify_layout(ll, 'angle')
        if kwargs['unangle']:
            __modify_layout(ll, 'unangle')
        if kwargs['mirror']:
            __modify_layout(ll, 'mirror')
        if kwargs['cycle']:
            __modify_layout(ll, 'cycle', kwargs['cycle'])
    except ValueError as e:
        return str(e)

    ll.name += ' (modified)'

    return layout.to_string(ll, id=message.author.id)

def use():
    return """
mod layout_name [--kwarg1, --kwarg2, ...]
--angle:
    view the angle modded version of a layout
--unangle:
    view the non angle modded version of a layout
--mirror:
    view the mirrored version of a layout
--cycle:
    cycle a layout's letters around
--swap:
    alias of --cycle
"""

def desc():
    return 'see the stats of a layout with chained modifications'

def __modify_layout(ll: Layout, mode: str, *args):
    mod = import_module(f'cmds.{mode}')
    mod.modify(ll, *args)

def __get_layout_desc(mode: str) -> str:
    mod = import_module(f'cmds.{mode}')
    return mod.desc()

from discord import Colour, Client, Guild

AKL_ID = 807843650717483049

LAYOUT_ROLE_COLOUR = Colour.teal()  # 0x1ABC9C

class CaseInsensitiveStr:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value.__format__(format_spec)

    def __hash__(self):
        return hash(self.value.lower())

    def __eq__(self, other):
        if isinstance(other, CaseInsensitiveStr):
            return self.value.lower() == other.value.lower()
        elif isinstance(other, str):
            return self.value.lower() == other.lower()
        else:
            return False

def exec(bot: Client):
    guild: Guild = bot.get_guild(AKL_ID)
    if not guild:
        return 'Error: Cannot find akl server'
    layout_roles = [role for role in guild.roles if role.colour == LAYOUT_ROLE_COLOUR]
    role_counts = {CaseInsensitiveStr(role.name): len(role.members) for role in layout_roles}

    layout_role_counts: list[tuple[CaseInsensitiveStr, int]] = sorted(
        role_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    layout_role_counts = layout_role_counts[:20]

    res = ['```',
           '--- AKL STATS ---',
           'Layout role count:']
    res.extend(f'    {role_name:<15} ({count} users)' for (role_name, count) in layout_role_counts)
    res.append('```')
    return '\n'.join(res)

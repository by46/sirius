from functools import partial

__author__ = 'benjamin.c.yan'


def group(l, n):
    for i in range(0, len(l), n):
        val = l[i:i + n]
        if len(val) == n:
            yield tuple(val)


group_by_2 = partial(group, n=2)


def parse_list(text, delimiter=';'):
    if text is None:
        return []
    return text.split(delimiter)

import re
import textwrap
import itertools


# borrowed from https://stackoverflow.com/a/1176023
def camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def ensure_single_line_text(text):
    return text.replace("\n", " ")


def wrap_text(text, width):
    if text:
        return "\n".join(
            itertools.chain.from_iterable(
                textwrap.wrap(line, width) for line in text.split("\n")
            )
        )
    else:
        return ""

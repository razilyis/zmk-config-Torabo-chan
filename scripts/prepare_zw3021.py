"""Build a 59-position keymap from the five-key Keymap Editor source.

Only the build output is expanded. Never edit config/torabo_chan.keymap here.
The order of the 54 virtual keys is the pinned ZW3021 driver's ABI.
"""
import argparse
from pathlib import Path
import re

OUTPUT_KEYS = (
    [f"N{i}" for i in range(10)]
    + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    + ["EXCL", "AT", "HASH", "DLLR", "PRCNT", "CARET", "AMPS", "STAR",
       "LPAR", "RPAR", "MINUS", "UNDER", "EQUAL", "PLUS", "DOT", "COMMA",
       "LSHFT", "ENTER"]
)


def masked(text):
    # Preserve offsets while removing comments and quoted strings from parsing.
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',
                  lambda m: re.sub(r'[^\n]', ' ', m.group()), text, flags=re.S)


def closing(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError('Unbalanced keymap braces')


def expand(source):
    clean = masked(source)
    nodes = list(re.finditer(r'\bkeymap\s*\{', clean))
    if len(nodes) != 1:
        raise ValueError('Expected one keymap node')
    begin = clean.index('{', nodes[0].start())
    end = closing(clean, begin)
    edits = []
    pos = begin + 1
    layer = 0
    while pos < end:
        start = clean.find('{', pos, end)
        if start < 0:
            break
        stop = closing(clean, start)
        block = clean[start:stop]
        matches = list(re.finditer(r'\bbindings\s*=\s*<(.*?)>\s*;', block, re.S))
        if len(matches) != 1 or '#' in matches[0][1]:
            raise ValueError('Each layer must have one explicit bindings list')
        binding = matches[0]
        if len(re.findall(r'&[A-Za-z_][A-Za-z_0-9]*', binding[1])) != 5:
            raise ValueError('Expected exactly five physical bindings per layer')
        extra = [f'&kp {key}' for key in OUTPUT_KEYS] if layer == 0 else ['&trans'] * 54
        edits.append((start + binding.end(1), '\n            // Internal fingerprint output keys.\n            '
                      + ' '.join(extra) + '\n        '))
        layer += 1
        pos = stop + 1
    if layer == 0:
        raise ValueError('No keymap layers found')
    result = source
    for offset, addition in reversed(edits):
        result = result[:offset] + addition + result[offset:]
    matrix = ' '.join([f'RC(0,{i})' for i in range(5)] + [f'RC(1,{i})' for i in range(54)])
    return ('// Generated from the current five-key keymap; do not edit.\n'
            '#include <dt-bindings/zmk/keys.h>\n'
            '#include <dt-bindings/zmk/matrix_transform.h>\n' + result
            + '\n&default_transform {\n    rows = <2>;\n    columns = <54>;\n'
            + f'    map = <{matrix}>;\n}};\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = expand(args.source.read_text(encoding='utf-8'))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding='utf-8')
    print(f'Generated {args.output}: 5 physical + 54 virtual positions')

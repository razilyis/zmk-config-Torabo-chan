import re
import unittest
from pathlib import Path
from prepare_zw3021 import expand, OUTPUT_KEYS


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.source = (Path(__file__).resolve().parents[1] / 'config/torabo_chan.keymap').read_text()

    def test_current_bindings_preserved_and_virtual_order(self):
        result = expand(self.source)
        lists = lambda s: re.findall(r'bindings\s*=\s*<(.*?)>\s*;', s, re.S)
        before, after = lists(self.source), lists(result)
        # The scroll hold-tap's bindings property stays untouched.
        self.assertEqual(before[0], after[0])
        self.assertEqual(len(OUTPUT_KEYS), 54)
        for i, (old, new) in enumerate(zip(before[1:], after[1:])):
            self.assertTrue(new.startswith(old))
            self.assertEqual(new.count('&'), 59)
            if i == 0:
                self.assertEqual(re.findall(r'&kp (\w+)', new[len(old):]), OUTPUT_KEYS)
            else:
                self.assertEqual(new[len(old):].count('&trans'), 54)
        self.assertEqual(result.count('RC('), 59)

    def test_new_layer_from_editor_also_expanded(self):
        source = self.source.replace('        layer_2 {',
            '        extra { bindings = <&trans &trans &trans &trans &trans>; };\n        layer_2 {')
        self.assertEqual(expand(source).count('Internal fingerprint output keys.'), 4)

    def test_comments_do_not_create_phantom_keys(self):
        source = self.source.replace('&trans', '/* &kp A { } */ &trans', 1)
        self.assertIn('/* &kp A { } */ &trans', expand(source))

    def test_rejects_non_five_key_layer(self):
        with self.assertRaises(ValueError):
            expand(self.source.replace('&trans', '&trans &kp A', 1))

    def test_rejects_double_expansion(self):
        with self.assertRaises(ValueError):
            expand(expand(self.source))


if __name__ == '__main__':
    unittest.main()

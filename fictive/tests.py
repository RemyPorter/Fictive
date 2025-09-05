from .triggers import *
from .parser import *
from .states import Machine
from .print_helper import statify, scan_for_template
import unittest


class TriggerTests(unittest.TestCase):
    def test_set_key(self):
        d: Statebag = {}
        set_key("test", "value")(None, "", d)
        self.assertEqual(d["test"], "value")

    def test_set_key_templated(self):
        d: Statebag = {"value": "world"}
        s: str = "Hello {value}!"
        set_key("test", s)(None, "", d)
        self.assertEqual(d["test"], "Hello world!")

    def test_key_as_int(self):
        d: Statebag = {"int": 2, "str": "3", "nonnumeric": "abc"}
        self.assertEqual(key_as_int("int", d), 2)
        self.assertEqual(key_as_int("str", d), 3)
        self.assertEqual(key_as_int("nonnumeric", d), 0)

    def test_inc(self):
        d: Statebag = {"key": 5}
        inc("key")(None, "", d)
        inc("noKey")(None, "", d)
        self.assertEqual(d["key"], 6)
        self.assertEqual(d["noKey"], 1)

    def test_dec(self):
        d: Statebag = {"key": 5}
        dec("key")(None, "", d)
        dec("noKey")(None, "", d)
        self.assertEqual(d["key"], 4)
        self.assertEqual(d["noKey"], -1)

    def test_matcher(self):
        match_string = "(test|other)"
        keys = ["op"]
        d: Statebag = {}
        m = on_match(match_string, keys)
        self.assertTrue(m(None, "test", d))
        self.assertEqual(d["op"], "test")
        d = {}
        self.assertFalse(m(None, "invalid", d))
        d = {}
        self.assertTrue(m(None, "other", d))
        self.assertEqual(d["op"], "other")

    def test_on_key(self):
        d: Statebag = {"test": "value"}
        self.assertTrue(on_key("test", "value")(None, "", d))
        self.assertFalse(on_key("no_key", "value")(None, "", d))
        self.assertFalse(on_key("test", "not value")(None, "", d))

    def test_on_key_gt(self):
        d: Statebag = {"int": 5, "str": "3"}
        self.assertTrue(on_key_gt("int", 3)(None, "", d))
        self.assertTrue(on_key_gt("str", 2)(None, "", d))
        self.assertFalse(on_key_gt("nokey", 6)(None, "", d))
        self.assertFalse(on_key_gt("int", 7)(None, "", d))

    def test_on_key_lt(self):
        d: Statebag = {"int": 5, "str": "3"}
        self.assertFalse(on_key_lt("int", 3)(None, "", d))
        self.assertFalse(on_key_lt("str", 2)(None, "", d))
        # this is true, because we've made it so non-existent keys can pass
        self.assertTrue(on_key_lt("nokey", 6)(None, "", d))
        self.assertTrue(on_key_lt("int", 7)(None, "", d))

    def test_key_key_eq(self):
        d: Statebag = {"a": 5, "b": 10, "c": 5}
        self.assertTrue(on_key("a", other="c")(None, "", d))
        self.assertFalse(on_key("a", other="b")(None, "", d))

    def test_key_key_gt(self):
        d: Statebag = {"a": 5, "b": 10, "c": 5}
        self.assertTrue(on_key_gt("b", other="a")(None, "", d))
        self.assertFalse(on_key_gt("a", other="c")(None, "", d))

    def test_key_key_lt(self):
        d: Statebag = {"a": 5, "b": 10, "c": 5}
        self.assertFalse(on_key_lt("b", other="a")(None, "", d))
        self.assertTrue(on_key_lt("a", other="b")(None, "", d))

    def test_key_key_gte(self):
        d: Statebag = {"a": 5, "b": 10, "c": 5}
        self.assertTrue(on_key_gte("b", other="a")(None, "", d))
        self.assertTrue(on_key_gte("a", other="c")(None, "", d))

    def test_key_key_lte(self):
        d: Statebag = {"a": 5, "b": 10, "c": 5}
        self.assertFalse(on_key_lte("b", other="a")(None, "", d))
        self.assertTrue(on_key_lte("a", other="b")(None, "", d))
        self.assertTrue(on_key_lte("a", other="c")(None, "", d))


class ParserTests(unittest.TestCase):
    def test_no_param_function(self):
        f = "revert"
        res = parse_function(f)
        with self.assertRaises(Machine.EnterAndRevert):
            res(None, "", {})

    def test_one_pararm_function(self):
        f = {"banner": "test"}
        res = parse_function(f)

    def test_param_function(self):
        f = {
            "inc": {
                "key": "foo"
            }
        }
        d: Statebag = {"foo": "5"}
        res = parse_function(f)
        res(None, "", d)
        self.assertEqual(d["foo"], 6)

    def test_parse_single_trigger(self):
        f = {
            "on_enter": "revert"
        }
        res = parse_trigger("on_enter", f)
        with self.assertRaises(Machine.EnterAndRevert):
            res(None, "", {})

    def test_parse_multi_trigger(self):
        f = {
            "on_enter": [
                {"inc": {
                    "key": "foo"
                }},
                "revert"
            ]
        }
        res = parse_trigger("on_enter", f)
        d: Statebag = {"foo": "5"}
        with self.assertRaises(Machine.EnterAndRevert):
            res(None, "", d)
        self.assertEqual(d["foo"], 6)

    def test_on_key_value_parser(self):
        f = {
            "on_key": {
                "key": "test",
                "value": 5
            }
        }
        d: Statebag = {"test": 5, "other": 5}
        res = parse_function(f)
        self.assertTrue(res(None, "", d))

    def test_on_key_key_parser(self):
        f = {
            "on_key": {
                "key": "test",
                "other": "other"
            }
        }
        d: Statebag = {"test": 5, "other": 5}
        res = parse_function(f)
        self.assertTrue(res(None, "", d))


class TemplateStringTests(unittest.TestCase):
    def test_scan_no_template(self):
        text = "a simple, untemplated, test string"
        self.assertEqual(scan_for_template(text), None)

    def test_scan_template(self):
        text = "a test string, {template}"
        matched = scan_for_template(text)
        self.assertEqual(matched.start, 15)
        self.assertEqual(matched.end, 25)
        self.assertEqual(matched.key, "template")
        self.assertEqual(text[matched.start:matched.end], "{template}")

    def test_scan_with_escape(self):
        text = "a test string \\{with an escaped {template}"
        matched = scan_for_template(text)
        self.assertEqual(matched.key, "template")

    def test_scan_with_two_templates(self):
        text = "{template0}, {template1}"
        firstMatch = scan_for_template(text)
        secondMatch = scan_for_template(text[firstMatch.end:])
        self.assertEqual(firstMatch.key, "template0")
        self.assertEqual(secondMatch.key, "template1")


class StatifyTests(unittest.TestCase):
    def test_no_template(self):
        no_template = "This is a simple non-templated string."
        self.assertEqual(no_template, statify(no_template, {}))

    def test_template_match(self):
        templated = "This is a {adjective} templated string."
        d = {"adjective": "complex"}
        self.assertEqual("This is a complex templated string.",
                         statify(templated, d))

    def test_template_no_match(self):
        templated = "This is an {adjective} templated string."
        self.assertEqual(
            "This is an <<ERROR: adjective not in state bag>> templated string.", statify(templated, {}))

    def test_template_multi_match(self):
        templated = "{greeting}, {target}!"
        d = {"greeting": "Hello", "target": "World"}
        replaced = statify(templated, d)
        self.assertEqual(replaced, "Hello, World!")

    def test_template_repeated_match(self):
        templated = "{word}, {word}"
        d = {"word": "ahoy"}
        replaced = statify(templated, d)
        self.assertEqual(replaced, "ahoy, ahoy")

    def test_templated_banner(self):
        f = {
            "banner": "{my_template}"
        }
        d: Statebag = {"my_template": "Hello World!"}
        res = parse_function(f)(None, "", d)
        self.assertEqual(d["state.banner"], "Hello World!")

from .triggers import *
import unittest

class TriggerTests(unittest.TestCase):
    def test_set_key(self):
        d:Statebag = {}
        set_key("test", "value")(None, "", d)
        self.assertEqual(d["test"], "value")

    def test_key_as_int(self):
        d:Statebag = {"int": 2, "str": "3", "nonnumeric": "abc"}
        self.assertEqual(key_as_int("int", d), 2)
        self.assertEqual(key_as_int("str", d), 3)
        self.assertEqual(key_as_int("nonnumeric", d), 0)

    def test_inc(self):
        d:Statebag = {"key": 5}
        inc("key")(None, "", d)
        inc("noKey")(None, "", d)
        self.assertEqual(d["key"], 6)
        self.assertEqual(d["noKey"], 1)

    def test_dec(self):
        d:Statebag = {"key": 5}
        dec("key")(None, "", d)
        dec("noKey")(None, "", d)
        self.assertEqual(d["key"], 4)
        self.assertEqual(d["noKey"], -1)

    def test_matcher(self):
        match_string = "(test|other)"
        keys = ["op"]
        d:Statebag = {}
        m = on_match(match_string, keys)
        self.assertTrue(m(None, "test", d))
        self.assertEqual(d["op"], "test")
        d = {}
        self.assertFalse(m(None, "invalid", d))
        d = {}
        self.assertTrue(m(None, "other", d))
        self.assertEqual(d["op"], "other")

    def test_on_key(self):
        d:Statebag = {"test": "value"}
        self.assertTrue(on_key("test", "value")(None, "", d))
        self.assertFalse(on_key("no_key", "value")(None, "", d))
        self.assertFalse(on_key("test", "not value")(None, "", d))

    def test_on_key_gt(self):
        d:Statebag = {"int": 5, "str": "3"}
        self.assertTrue(on_key_gt("int", 3)(None, "", d))
        self.assertTrue(on_key_gt("str", 2)(None, "", d))
        self.assertFalse(on_key_gt("nokey", 6)(None, "", d))
        self.assertFalse(on_key_gt("int", 7)(None, "", d))

    def test_on_key_lt(self):
        d:Statebag = {"int": 5, "str": "3"}
        self.assertFalse(on_key_lt("int", 3)(None, "", d))
        self.assertFalse(on_key_lt("str", 2)(None, "", d))
        self.assertFalse(on_key_lt("nokey", 6)(None, "", d))
        self.assertTrue(on_key_lt("int", 7)(None, "", d))
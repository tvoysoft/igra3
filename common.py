import unittest


class TwoWayDict(dict):
    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dict.__len__(self) // 2


class TwoWayLinkSet:
    """
        Two way links of object with params
    """
    def __init__(self):
        self.__params = {}
        self.__links = {}
        self.__counter = 0

        self.__links_updated = False
        self.__groups_cache = None

    def is_linked(self, key1, key2):
        return key1 in self.__links and key2 in self.__links[key1]

    def __new_link(self, key1, key2):
        self.__links_updated = True
        self.__counter += 1
        if key1 not in self.__links:
            self.__links[key1] = {}
        if key2 not in self.__links:
            self.__links[key2] = {}
        self.__links[key1][key2] = self.__counter
        self.__links[key2][key1] = self.__counter
        return self.__counter

    def set(self, key1, key2, *args):
        self.__links_updated = True
        if self.is_linked(key1, key2):
            link_id = self.__links[key1][key2]
        else:
            link_id = self.__new_link(key1, key2)

        if len(args) == 1:
            self.__params[link_id] = args[0]
        else:
            self.__params[link_id] = args

    def get(self, key1, key2, default=None):
        if self.is_linked(key1, key2):
            return self.__params[self.__links[key1][key2]]
        else:
            return default

    def count(self, key):
        if key not in self.__links:
            return 0
        else:
            return len(self.__links[key])

    def remove(self, key1, key2):
        if self.is_linked(key1, key2):
            self.__links_updated = True
            link_id = self.__links[key1][key2]
            del self.__links[key1][key2]
            del self.__links[key2][key1]
            params = self.__params[link_id]
            del self.__params[link_id]
            return params
        else:
            return False

    @staticmethod
    def __check_link(link_param, link_filter):
        if len(link_filter) > len(link_param):
            return False

        for j, v in enumerate(link_filter):
            if link_param[j] != v:
                return False
        return True

    def get_groups(self):
        """ get groups of linked objects """
        if not self.__links_updated:
            return self.__groups_cache

        if self.__links is None or len(self.__links) == 0:
            self.__groups_cache = []
            self.__links_updated = False
            return self.__groups_cache


        groups = []

        passed = []

        def __check_link(key):
            if key in passed:
                return
            passed.append(key)
            # determine group for key
            group = None
            for g in groups:
                if key in g:
                    group = g
                    break
            if group is None:
                group = set()
                groups.append(group)
            group.add(key)
            for linked_key in dict(self.__links[key]).keys():
                group.add(linked_key)
                __check_link(linked_key)

        for k in self.__links:
            __check_link(k)

        self.__groups_cache = groups
        self.__links_updated = False
        return self.__groups_cache


class TwoWayLinkSetTest(unittest.TestCase):

    def setUp(self):
        self.o = TwoWayLinkSet()
        self.o.set(1, 2, 'one', 'two')
        self.o.set(1, 3, 'one', 'three')
        self.o.set(2, 2, 'two', 'two')
        self.o.set(2, 100, 'two', 'hundred')

        self.o.set(4, 5, 'fotin', 'fiftin')
        self.o.set(4, 6, 'fotin', 'sixtin')

        self.o.set(7, 8, 'seventin', 'eighttin')
        self.o.set(9, 10, 'ninetin', 'twenten')

        self.o.set(1000, 1001)
        self.o.set(1001, 1002)
        self.o.set(1001, 1003)
        self.o.set(1001, 1004)
        self.o.set(1004, 1005)

    def test_groups(self):
        groups = self.o.get_groups()
        self.assertIn({1, 2, 3, 100}, groups)
        self.assertIn({4, 5, 6}, groups)
        self.assertIn({7, 8}, groups)
        self.assertIn({9, 10}, groups)
        self.assertIn({1000, 1001, 1002, 1003, 1004, 1005}, groups)

    def test_count(self):
        self.assertEqual(self.o.count(2), 3)
        self.assertEqual(self.o.count(4), 2)
        self.assertEqual(self.o.count(123), 0)

    def test_correct(self):
        self.assertEqual(self.o.get(1, 2), ('one', 'two'))
        self.assertEqual(self.o.get(2, 1), ('one', 'two'))
        self.assertEqual(self.o.get(2, 2), ('two', 'two'))
        self.assertEqual(self.o.get(3, 1), ('one', 'three'))
        self.assertEqual(self.o.get(1, 3), ('one', 'three'))
        self.assertIsNone(self.o.get(1, 4))
        self.assertIsNone(self.o.get(1, 1))

    def test_add(self):
        self.o.set(5, 6, 'hello')
        self.assertEqual(self.o.get(6, 5), 'hello')
        self.o.set(5, 6, 'hello world')
        self.assertNotEqual(self.o.get(6, 5), 'hello')
        self.assertEqual(self.o.get(6, 5), 'hello world')
        self.o.remove(6, 5)
        self.assertFalse(self.o.is_linked(5, 6))
        self.assertIsNone(self.o.get(5, 6))

    def test_linked(self):
        self.assertTrue(self.o.is_linked(1, 2))
        self.assertTrue(self.o.is_linked(2, 1))
        self.assertTrue(self.o.is_linked(1, 3))
        self.assertTrue(self.o.is_linked(3, 1))
        self.assertTrue(self.o.is_linked(2, 2))

        self.assertFalse(self.o.is_linked(1, 1))
        self.assertFalse(self.o.is_linked(3, 3))
        self.assertFalse(self.o.is_linked(1, 4))
        self.assertFalse(self.o.is_linked(4, 1))

if __name__ == '__main__':
    unittest.main()

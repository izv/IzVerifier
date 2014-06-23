import os
from IzVerifier.izspecs.izconditions import IzConditions
from IzVerifier.izspecs.izstrings import IzStrings
from IzVerifier.izverifier import IzVerifier

__author__ = 'fcanas'

import unittest

path1 = 'data/sample_installer_1/izpack/'



class TestVerifier(unittest.TestCase):
    """
    Basic testing of verifier class.
    """

    def setUp(self):
        args = {
            'installer': path1,
            'sources': []
        }
        self.izv = IzVerifier(args)

    def test_IzPaths(self):
        """
        Testing install.xml path parsing.
        """
        specs = [('variables', 'variables.xml'),
                 ('conditions', 'conditions.xml'),
                 ('dynamicvariables', 'dynamic_variables.xml'),
                 ('resources', 'resources.xml'),
                 ('panels', 'panels.xml'),
                 ('packs', 'packs.xml')]

        self.assertTrue(self.izv != None)
        for spec in specs:
            path = self.izv.paths.get_path(spec[0])
            self.assertTrue(spec[1] in path,
                            msg=path + "!=" + spec[1])

    def test_IzConditions(self):
        """
        Testing the strings container.
        """
        izc = IzConditions(self.izv.paths.get_path('conditions'))
        self.assertTrue(izc != None)

        # Test for number of keys in conditions.xml plus white list
        num = len(izc.get_keys())
        self.assertEquals(num, 3, str(num) + "=3")

    def test_IzStrings(self):
        """
        Testing the strings container.
        """
        izs = IzStrings(self.izv.paths.get_path('strings'))
        self.assertTrue(izs != None)

        # Test for number of keys in conditions.xml plus white list
        num = len(izs.get_keys())
        self.assertEquals(num, 11, str(num) + "=11")

if __name__ == '__main__':
    unittest.main()


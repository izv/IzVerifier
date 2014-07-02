from IzVerifier.izspecs.izpaths import path_format

__author__ = 'fcanas'

import unittest

pom = 'data/sample_installer_iz5/pom.xml'
path1 = 'data/sample_installer_iz5/izpack/'
path2 = 'data/sample_installer_iz5/resources/'
source_path2 = 'data/sample_code_base'

class TestSeeker(unittest.TestCase):
    """
    Basic testing of izpaths class.
    """

    def test_pathFormat(self):
        """
        Tests the path formatting function.
        """
        p1 = 'data//sample_installer_iz5'
        r1 = path_format(p1)
        self.assertEquals('data/sample_installer_iz5/', r1)

        p1 = 'data//sample_installer_iz5/pom.xml'
        r1 = path_format(p1)
        self.assertEquals('data/sample_installer_iz5/pom.xml', r1)

        p1 = 'data///sample_installer_iz5/pom.xml'
        r1 = path_format(p1)
        self.assertEquals('data/sample_installer_iz5/pom.xml', r1)


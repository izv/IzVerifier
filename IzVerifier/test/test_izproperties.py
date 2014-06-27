from IzVerifier.izspecs.izproperties import IzProperties

__author__ = 'fcanas'
import unittest

pom = 'data/sample_installer_iz5/pom.xml'
path1 = 'data/sample_installer_iz5/izpack/'
path2 = 'data/sample_installer_iz5/resources/'
source_path2 = 'data/sample_code_base'

class TestSeeker(unittest.TestCase):
    """
    Basic testing of izproperties class.
    """

    def test_parsePom(self):
        """
        Tests izproperties' ability to parse props from a pom file.
        """
        props = IzProperties(pom)
        self.assertEquals(props['izpack.version'], '5.0.0-rc2-SNAPSHOT')
        self.assertEquals(props['project.build.sourceEncoding'], 'UTF-8')


    def test_parseIzProperties(self):
        """
        Test izpack properties file parsing.
        """
        pass
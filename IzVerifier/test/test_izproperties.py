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
        self.assertEquals(props['izpack.version'], '5.0.0-rc2')
        self.assertEquals(props['project.build.sourceEncoding'], 'UTF-8')


    def test_parseIzProperties(self):
        """
        Test izpack properties file parsing.
        """
        pass

    def test_substituteStrings(self):
        """
        Test the substitution methods.
        """
        props = IzProperties(pom)

        s1 = "${izpack.version}-A.B.C"
        r1 = props.substitute(s1)
        self.assertEquals("5.0.0-rc2-A.B.C", r1)

        s2 = "${project.version}-A.B.C"
        r2 = props.substitute(s2)
        self.assertEquals("5.0.0-rc2-SNAPSHOT-A.B.C", r2)

        s3 = "${undefined.prop}-A.B.C"
        r3 = props.substitute(s3)
        self.assertEquals("${undefined.prop}-A.B.C", r3)

        s4 = "${mistyped.prop-A.B.C"
        r4 = props.substitute(s4)
        self.assertEquals("${mistyped.prop-A.B.C", r4)



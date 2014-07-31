from IzVerifier.izspecs.verifiers.dependencies import depth_first_search

__author__ = 'fcanas'

import unittest

from IzVerifier.izverifier import IzVerifier


path1 = 'data/sample_installer_iz5/izpack/'
path2 = 'data/sample_installer_iz5/resources/'
source_path2 = 'data/sample_code_base'
pom = 'data/sample_installer_iz5/pom.xml'



class TestDependencies(unittest.TestCase):
    """
    Basic testing of verifier class.
    """

    def setUp(self):
        args = {
            'specs_path': path1,
            'sources': [source_path2],
            'resources_path': path2,
            'pom': pom,
            'specs': ['conditions', 'strings', 'variables']
        }
        self.izv = IzVerifier(args)

    def test_verifyAllDependencies(self):
        """
        Run the full dependency verification test.
        """
        self.izv.dependency_verification(verbosity=2, fail_on_undefined_vars=False)

    def test_verifyDPS(self):
        """
        Tests the depth-first search for condition dependency problems.
        """
        conditions = self.izv.get_container('conditions')
        variables = self.izv.get_container('variables')
        depth_first_search(conditions, variables)



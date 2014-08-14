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
        }
        self.izv = IzVerifier(args)

    def test_verifyAllDependencies(self):
        """
        Run the full dependency verification test.
        """
        undefined_deps = {'and.1', 'and.2', 'and.3',
                          'or.cycle.1', 'or.cycle.2', 'or.cycle.3',
                          'some.condition.1', 'some.condition.2',
                          'variable1',
                          'myinstallerclass.condition', 'short.1'}

        results = self.izv.dependency_verification(verbosity=2, fail_on_undefined_vars=True)
        for cond in undefined_deps:
            self.assertTrue(cond in results.keys())

        for cond in results.keys():
            self.assertTrue(cond in undefined_deps)









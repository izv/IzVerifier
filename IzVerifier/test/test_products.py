__author__ = 'fcanas'

import unittest
from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izspecs.verifiers.seeker import Seeker
from IzVerifier.izverifier import IzVerifier
from IzVerifier.izspecs.izproperties import *


path1 = '' # path to specs
path2 = '' # path to resources
path3 = '' # path to pom
source_paths = [''] # paths to code bases
class TestProduct(unittest.TestCase):
    """
    This is a template class used to test the verifier on real izpack projects.
    """

    args = {
            'specs_path': path1,
            'sources': source_paths,
            'resources_path': path2,
            'pom': path3,
            'specs': ['conditions', 'strings', 'variables']
        }

    def setUp(self):
        #self.loadInstaller(self.args)
        pass



    def loadInstaller(self, args):
        """
        Runs the verifications on some installer product.
        """

        self.verifier = IzVerifier(args)
        self.seeker = Seeker(self.verifier.paths)
        self.conditions = IzConditions(self.verifier.paths.get_path('conditions'))
        self.variables = IzVariables(self.verifier.paths.get_path('variables'))
        langpack = self.verifier.paths.get_langpack_path()
        self.strings = IzStrings(langpack)

    def verifyInstaller(self):
        """
        Run verification tests.
        """
        #self.verifier.verify_all(verbosity=1)
        self.verifier.containers.get('classes').print_keys()
        self.verifier.verify('classes', verbosity=2)

    def test_verifyInstaller(self):
        #self.verifyInstaller()
        pass






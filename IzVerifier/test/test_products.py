__author__ = 'fcanas'

import unittest
from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izspecs.verifiers.seeker import Seeker
from IzVerifier.izverifier import IzVerifier
from IzVerifier.izspecs.izproperties import *


path1 = '' # path to install.xml
path2 = '' # path to install.xml
source_paths = [] # paths to code bases
class TestProduct(unittest.TestCase):
    """
    Basic testing of seeker class.
    """

    args = {
            'specs_path': path1,
            'sources': source_paths,
            'resources_path': path2,
            'specs': ['conditions', 'strings', 'variables']
        }

    def setUp(self):
        pass

    def verifyInstaller(self, args):
        """
        Runs the verifications on some installer product.
        """

        self.verifier = IzVerifier(args)
        self.seeker = Seeker(self.verifier.paths)
        langpacks = self.verifier.paths.get_langpacks()
        langpack = langpacks[0]
        self.conditions = IzConditions(self.verifier.paths.get_path('conditions'))
        self.variables = IzVariables(self.verifier.paths.get_path('variables'))
        self.strings = IzStrings(langpack[1])

    def test_verifyInstaller(self):
        pass
        #self.verifyInstaller(self.args)





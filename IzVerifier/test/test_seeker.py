from IzVerifier.izspecs.verifiers.seeker import Seeker

__author__ = 'fcanas'


import unittest
from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izverifier import IzVerifier
from IzVerifier.izspecs.izproperties import *


path1 = 'data/sample_installer_iz5'

class TestSeeker(unittest.TestCase):
    """
    Basic testing of seeker class.
    """

    def setUp(self):
        args = {
            'installer': path1,
            'sources': [],
            'specs': ['conditions', 'strings', 'variables']
        }

        self.izv = IzVerifier(args)
        self.seeker = Seeker(self.izv.paths)

    def test_findStringReference(self):
        """
        Find specified string reference across some spec files.
        """
        langpacks = self.izv.paths.get_langpacks()
        langpack = langpacks[0]
        self.izs = IzStrings(langpack[1])
        props = {
            'path': self.izv.paths.root,
            'id': 'some.user.panel.title',
            'specs': ["izpack/install.xml", "resources/userInputSpec.xml", "resources/langpacks/CustomLangPack.xml"],
            'filter_fn': self.izs.has_reference,
            'attributes': self.izs.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.izs.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.izs.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_all_references(props)
        hits = len(results)
        self.assertEquals(hits, 2, msg=str(hits) + '!=2')

    def test_findAllStrings(self):
        """
        Finds all strings referenced in installer spec files.
        """
        langpacks = self.izv.paths.get_langpacks()
        langpack = langpacks[0]
        self.izs = IzStrings(langpack[1])

        props = {
            'path': self.izv.paths.root,
            'specs': self.izs.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.izs.has_reference,
            'attributes': self.izs.properties[ATTRIBUTES],
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) != 0)
__author__ = 'fcanas'

import unittest
from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izspecs.verifiers.seeker import Seeker
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

        self.verifier = IzVerifier(args)
        self.seeker = Seeker(self.verifier.paths)
        langpacks = self.verifier.paths.get_langpacks()
        langpack = langpacks[0]
        self.conditions = IzConditions(self.verifier.paths.get_path('conditions'))
        self.variables = IzVariables(self.verifier.paths.get_path('variables'))
        self.strings = IzStrings(langpack[1])

    def test_findStringReference(self):
        """
        Find specified string reference across some spec files.
        """
        props = {
            'path': self.verifier.paths.root,
            'id': 'some.user.panel.title',
            'specs': ["izpack/install.xml", "resources/userInputSpec.xml", "resources/langpacks/CustomLangPack.xml"],
            'filter_fn': self.strings.has_reference,
            'attributes': self.strings.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.strings.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.strings.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_id_references(props)
        hits = len(results)
        self.assertEquals(hits, 2, msg=str(hits) + '!=2')

    def test_findConditionReference(self):
        """
        Find specified condition reference across some spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'id': 'some.condition.1',
            'specs': self.conditions.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.conditions.has_reference,
            'attributes': self.conditions.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.conditions.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.strings.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_id_references(props)
        hits = len(results)
        self.assertEquals(hits, 1, msg=str(hits) + '!=1')

    def test_findVariableReference(self):
        """
        Find specified variable reference across some spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'id': 'some.user.password',
            'specs': self.variables.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.variables.has_reference,
            'attributes': self.variables.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.variables.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.strings.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_id_references(props)
        hits = len(results)
        self.assertEquals(hits, 1, msg=str(hits) + '!=1')

    def test_findAllStrings(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': self.strings.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.strings.has_reference,
            'attributes': self.strings.properties[ATTRIBUTES],
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) != 0)

    def test_findAllConditions(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': self.conditions.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.conditions.has_reference,
            'attributes': self.conditions.properties[ATTRIBUTES],
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) == 1)


    def test_findAllVariables(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': self.variables.properties[REFERENCE_SPEC_FILES],
            'filter_fn': self.variables.has_reference,
            'attributes': self.variables.properties[ATTRIBUTES],
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) == 2)
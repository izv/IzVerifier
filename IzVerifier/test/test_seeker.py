from IzVerifier.izspecs.izproperties import IzProperties

__author__ = 'fcanas'

import unittest

from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izspecs.verifiers.seeker import Seeker
from IzVerifier.izverifier import IzVerifier
from IzVerifier.izspecs.containers.constants import *


path1 = 'data/sample_installer_iz5/izpack/'
path2 = 'data/sample_installer_iz5/resources/'
source_path2 = 'data/sample_code_base'
pom = 'data/sample_installer_iz5/pom.xml'


class TestSeeker(unittest.TestCase):
    """
    Basic testing of seeker class.
    """

    def setUp(self):
        args = {
            'specs_path': path1,
            'sources': [source_path2],
            'resources_path': path2,
            'pom': pom,
            'specs': ['conditions', 'strings', 'variables']
        }
        self.verifier = IzVerifier(args)
        self.seeker = Seeker(self.verifier.paths)
        langpack = self.verifier.paths.get_langpack_path()
        self.conditions = IzConditions(self.verifier.paths.get_path('conditions'))
        self.variables = IzVariables(self.verifier.paths.get_path('variables'))
        self.strings = IzStrings(langpack)

    def test_findStringReference(self):
        """
        Find specified string reference across some spec files.
        """
        props = {
            'path': self.verifier.paths.root,
            'id': 'some.user.panel.title',
            'specs': ['data/sample_installer_iz5/izpack/install.xml',
                      'data/sample_installer_iz5/resources/userInputSpec.xml'],
            'filter_fn': self.strings.has_reference,
            'attributes': self.strings.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.strings.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.strings.properties[WHITE_LIST_PATTERNS]
        }
        results = self.seeker.find_id_references(props)
        hits = len(results)
        self.assertEquals(hits, 1, msg=str(hits) + '!=1')

    def test_findConditionReference(self):
        """
        Find specified condition reference across some spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'id': 'some.condition.1',
            'specs': map(self.verifier.paths.get_path, self.conditions.properties[REFERENCE_SPEC_FILES]),
            'filter_fn': self.conditions.has_reference,
            'attributes': self.conditions.properties[ATTRIBUTES],
            'transformer': lambda x: x,
            'patterns': self.conditions.properties[PATTERNS],
            'source_paths': [],
            'white_list_patterns': self.conditions.properties[WHITE_LIST_PATTERNS]
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
            'specs': map(self.verifier.paths.get_path, self.variables.properties[REFERENCE_SPEC_FILES]),
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

    def test_findAllStringsInSpecs(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': map(self.verifier.paths.get_path, self.strings.properties[REFERENCE_SPEC_FILES]),
            'filter_fn': self.strings.has_reference,
            'attributes': self.strings.properties[ATTRIBUTES],
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) == 7, msg=str(len(hits)) + '!=7')

    def test_findAllConditionsInSpecs(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': map(self.verifier.paths.get_path, self.conditions.properties[REFERENCE_SPEC_FILES]),
            'filter_fn': self.conditions.has_reference,
            'attributes': self.conditions.properties[ATTRIBUTES],
            'white_list_patterns': []
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) == 4)


    def test_findAllVariablesInSpecs(self):
        """
        Finds all strings referenced in installer spec files.
        """

        props = {
            'path': self.verifier.paths.root,
            'specs': map(self.verifier.paths.get_path, self.variables.properties[REFERENCE_SPEC_FILES]),
            'filter_fn': self.variables.has_reference,
            'attributes': self.variables.properties[ATTRIBUTES],
            'white_list_patterns': []
        }

        hits = self.seeker.search_specs_for_attributes(props)
        self.assertTrue(len(hits) == 2)

    def test_findAllStringsInSource(self):
        """
        Search source code for izpack string references.
        """
        hits = self.seeker.find_references_in_source(
            patterns=self.strings.properties[PATTERNS],
            path_list=[source_path2],
            white_list_patterns=self.strings.properties[WHITE_LIST_PATTERNS]
        )
        num = len(hits)
        self.assertTrue(num == 8)

    def test_processKeys(self):
        """
        Test the process_keys method.
        """
        # hits list: (key from source, location, expected output)
        hits = [('idata.getString("string.key.1"', 'path/to/file.java', 'string.key.1'),
                ('System.out.println(idata.getString("string.key.2"', 'path/to/file.java', 'string.key.2'),
                ('"string.key.3"', 'path/to/file.java', 'string.key.3'),
                ('somevar + "string.key.4"', 'path/to/file.java', None),
                ('key1', 'data/sample_code_base/src/com/sample/installer/Foo.java', 'some.string.1')
        ]

        seeker = Seeker(None)
        for hit in hits:
            key = seeker.process_key(hit, ['string.in.whitelist'], 'idata.getString\(.*|System.*.println\(.*')
            if key is None:
                print str(hit[2]) + " => " + str(key)
                self.assertEquals(hit[2], key)
            else:
                print str(hit[2]) + " => " + str(key[0])
                self.assertEquals(hit[2], key[0])



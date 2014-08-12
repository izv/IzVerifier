from bs4 import BeautifulSoup

from IzVerifier.izspecs.containers.izcontainer import IzContainer
from IzVerifier.izspecs.containers.constants import *


IZPACK_LANG_PATH = 'izpack_lang_path'


class IzStrings(IzContainer):
    """
    Container for izpack strings from langpack files.
    """
    properties = {
        NAME: 'strings',
        DEFINITION_SPEC_FILES: ['eng.xml'],
        REFERENCE_SPEC_FILES: ["install",
                               "userInputSpec",
                               "ProcessPanel.Spec",
                               "core-packs"],
        SOURCE_SEARCH_PATTERN: 'langpack.getString(',
        CHECK_KEY_PATTERN: 'langpack.getString\(\"(.*?)\"\)',
        ATTRIBUTES: ['id', 'tooltip', 'variable'],
        SPEC_ELEMENT: '<str id=\"{0}\" txt=\"{1}\"/>',
        PATTERNS: [
            ('langpack.getString\({0}', 'langpack.getString\(({0})\)'),
            ('setError\({0}', 'setError\(({0})\)'),
            ('setMessage\({0}', 'setMessage\(({0})\)'),
            ('System.*.println\({0}', 'System.*.println\(({0})\)'),
            ('setErrorMessageId\({0}', 'setErrorMessageId\(({0})\)')],
        WHITE_LIST_PATTERNS: ['^.*\(\(String\) conn\);.*$',
                              '^UserInputPanel.*$'],  # for some weirdness in a console helper :)

        PARENT_OPENING_TAG: '<langpack>',
        PARENT_CLOSING_TAG: '</langpack>',
    }

    def parse_izpack_strings(self, path):
        """
        Parse izpack's built-in langpack strings.
        """
        self.soup_izpack = BeautifulSoup(open(path), 'xml')
        self.parse(self.soup_izpack)

    def parse(self, soup):
        """
        Extracts all strings from the soup document.
        """
        strings = soup.find_all(self.has_definition)
        for st in strings:
            self.container[str(st['id'])] = st

    def has_definition(self, element):
        """
        Return true if the given element contains an izpack string definition.
        """
        return str(element.name) == 'str' and element.has_attr('id') and element.has_attr('txt')

    def has_reference(self, element):
        """
        Return true if the given element contains an izpack string reference.
        This method is used to define all the rules that allow the verifier to find
        references to the type of iz entity being searched for.
        """

        # panels never contain strings directly as attributes. Their 'id' is the
        # panel id.
        if str(element.name) == 'panel':
            return False

        # Validators directly under panels have id's that are not strings.
        if str(element.parent.name) == 'panel' and str(element.name) == 'validator':
            return False

        # Elements with ids that start with the word 'port' in them are not strings either.
        if element.has_attr('id'):
            if element['id'].startswith('port') or 'maximum.offset.variable' in element.name:
                return False

        # for special case variables that are shown in summary panel and therefore require
        # their own eng string key:
        if element.name == 'field' and element.has_attr('variable') and not element['type'] == 'rule':
            if element.has_attr('summarize') and 'false' in element['summarize']:
                return False
            if element.has_attr('autoPrompt') and 'true' in element['autoPrompt']:
                return False
            return True

        # rule elements don't use strings
        if element.has_attr('type') and 'rule' in element['type']:
            return False

        if 'executeForPack' in element.name and element.has_attr('id'):
            return False

        # Otherwise, check if this element contains one of the attributes used to
        # hold string ids and return true if it does.
        for atty in IzStrings.properties['attributes']:
            if element.has_attr(atty):
                return True

        return False

    def get_keys(self):
        """
        """
        return self.container.keys()

    def count(self):
        """
        """
        return len(self.container.keys())

    def get_spec_elements(self):
        """
        Returns a set of xml elements defining each condition.
        """
        return set(self.container.values())

    @staticmethod
    def ref_transformer(reference):
        """
        Identity function.
        """
        return reference

    @staticmethod
    def element_sort_key(element):
        """
        Returns the key to use when sorting elements of this container.
        """
        return element['id'].lower()

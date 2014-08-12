from IzVerifier.izspecs.containers.izcontainer import IzContainer
from IzVerifier.izspecs.containers.constants import *


class IzVariables(IzContainer):
    """
    Container for parsing and storing IzPack variables from variables.xml.
    """

    properties = {
        NAME: "variables",
        DEFINITION_SPEC_FILES: ['variables.xml'],
        REFERENCE_SPEC_FILES: ["install",
                               "userInputSpec",
                               "ProcessPanel.Spec",
                               "core-packs",
                               "conditions",
                               "variables",
                               "dynamic_variables"],
        ATTRIBUTES: ['variable'],
        SPEC_ELEMENT: '<variable name=\"{0}\" value=\"{1}\"/>',
        PARENT_OPENING_TAG: '<xfragment>',
        PARENT_CLOSING_TAG: '</xfragment>',
        WHITE_LIST: ['izpack.linuxinstall', 'JAVA_HOME', 'INSTALL_PATH', 'IzPanel.LayoutType',
                     'APP_NAME', 'APP_URL', 'APP_VER', 'INSTALL_GROUP', 'UNINSTALLER_CONDITION',
                     'USER_NAME', 'USER_HOME', 'ISO3_LANG', 'IP_ADDRESS', 'HOST_NAME',
                     'FILE_SEPARATOR', 'DesktopShortcutCheckboxEnabled', 'InstallerFrame.logfilePath'],
        PATTERNS: [('getVariable\({0}', 'getVariable\(({0})\)'),
                   ('setVariable\({0}', 'setVariable\(({0}),({0})\)')],
        READ_PATTERNS: [('getVariable({0}', 'getVariable\(({0})\)')],
        WRITE_PATTERNS: [('setVariable({0}', 'setVariable\(({0}),({0})\)')],
        WHITE_LIST_PATTERNS: []
    }

    def parse(self, soup):
        """
        Extracts all variable definitions from variables.xml doc.
        """
        variables = soup.find_all('variable')
        for var in variables:
            self.container[str(var['name'])] = var

    def get_keys(self):
        """
        Returns a set of all the keys for defined variables.
        """
        return set(self.container.keys()) | set(self.properties[WHITE_LIST])

    def count(self):
        """
        Return number of vars found in definition file.
        """
        return len(self.container.keys())

    def get_spec_elements(self):
        """
        Returns a set of xml elements defining each variable.
        """
        return set(self.container.values())

    def has_reference(self, element):
        """
        Return true if the given element contains an izpack var reference.
        """
        for atty in self.properties['attributes']:
            if element.has_attr(atty):
                return True

        return False

    def to_string(self):
        return str(self.container)

    @staticmethod
    def print_keys():
        """
        Prints all of the variable keys found in definition spec.
        """
        pass

    @staticmethod
    def element_sort_key(element):
        """
        Returns the key to use when sorting elements of this container.
        """
        return element['name'].lower()

    @staticmethod
    def get_identifier(element):
        """
        Returns the identifying value for this element.
        """
        return element['name']

    @staticmethod
    def get_value(element):
        """
        Returns the main 'value' for this element.
        In the case of variables, its value is its value.
        """
        return element['value']

    @staticmethod
    def ref_transformer(ref):
        """
        Wraps reference into list.
        """
        return [ref]

    @staticmethod
    def has_definition(self, element):
        """
        Determines if element is a string definition.
        """
        return 'str' == element.name and element.has_attr('key') and element.has_attr('id')


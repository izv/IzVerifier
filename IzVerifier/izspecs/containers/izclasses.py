from IzVerifier.izspecs.containers.izcontainer import IzContainer
from IzVerifier.izspecs.containers.constants import *
from os import walk

__author__ = 'fcanas'


class IzClasses(IzContainer):
    """
    Container for parsing and storing custom classes used in izpack installers.
    """

    properties = {
        NAME: "classes",
        DEFINITION_SPEC_FILES: [],
        REFERENCE_SPEC_FILES: [
            "install",
            "userInputSpec",
            "ProcessPanel.Spec",
            "core-packs"],
        ATTRIBUTES: ['class', 'name', 'classname', 'installer'],
        SPEC_ELEMENT: '',
        PARENT_OPENING_TAG: '',
        PARENT_CLOSING_TAG: '',
        WHITE_LIST: [],
        PATTERNS: [],
        READ_PATTERNS: [],
        WRITE_PATTERNS: [],
        WHITE_LIST_PATTERNS: ['^com.izforge.izpack.*$']
    }

    def __init__(self, path=None):
        """
        Initializes the container from the path to the root of custom source code.
        Note: does not make use of parent class __init__.
        """
        self.container = {}
        self.referenced = {}
        if path:
            self.parse(path)

    def parse(self, root):
        """
        Izclasses are not pre-defined anywhere. All we can do is make a collection of
        all custom classes used in source code and index that.
        """
        for paths, dirs, files in walk(root):
            for f in files:
                if '.java' in f:
                    path = paths + '/' + f
                    name = self.path_to_id(root, path)
                    self.container[name] = path

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

    def print_keys(self):
        """
        Prints all of the variable keys found in definition spec.
        """
        for key in self.container.keys():
            print key

    def get_spec_elements(self):
        """
        Returns a set of xml elements defining each variable.
        """
        return set(self.container.values())

    def to_string(self):
        return str(self.container)

    def has_reference(self, element):
        """
        Return true if the given element contains an izpack var reference.
        """

        def is_izpack_class(classname):
            """
            Determines if this references an izpack built-in class.
            """
            if type(classname) is list:
                classname = classname[0]
            return not '.' in classname

        if element.has_attr('name') and element.name == 'executeclass':
            return not is_izpack_class(element['name'])
        if element.has_attr('class'):
            return not is_izpack_class(element['class'])
        if element.has_attr('classname'):
            return not is_izpack_class(element['classname'])
        if element.has_attr('installer') and element.name == 'listener':
            return not is_izpack_class(element['installer'])

        return False

    def has_definition(self, element):
        """
        Custom izpack classes are not defined by xml descriptors, so this method is unused.
        """
        pass

    @staticmethod
    def path_to_id(root, path):
        """
        Transforms a classpath to a class id.
        """
        return path.replace(root, '').replace('/', '.').replace('.java', '')

    @staticmethod
    def element_sort_key(element):
        """
        Returns the key to use when sorting elements of this container.
        """
        return element['class'].lower()

    @staticmethod
    def get_identifier(element):
        """
        Returns the identifying value for this element.
        """
        return element['class']

    @staticmethod
    def get_value(element):
        """
        Returns the main 'value' for this element.
        """
        return element

    @staticmethod
    def ref_transformer(ref):
        """
        Unwraps the ref if necessary.
        """
        return [ref]

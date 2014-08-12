from bs4 import BeautifulSoup
from abc import abstractmethod
from IzVerifier.exceptions.IzVerifierException import MissingFileException


class IzContainer():
    """
    Abstract class responsible for containing some izpack spec resource.

    For example implementers, see:
    izconditions (for izpack conditions)
    izstrings (for izpack localized strings)
    izvariables (for izpack variables)
    """

    def __init__(self, path):
        self.container = {}
        self.referenced = {}
        try:
            self.soup = BeautifulSoup(open(path), 'xml')
        except IOError:
            raise MissingFileException("spec not found at: " + path)
        self.parse(self.soup)

    def get_referenced(self):
        """
        Return a dict containing all referenced entities and the location of their references:
        {
            'id1' => [file1, file2, ...],
            ...
        }
        """
        return self.referenced

    @abstractmethod
    def parse(self, soup):
        """
        Parse the xml soup generated from the izpack descriptor file.
        """
        pass

    @abstractmethod
    def get_keys(self):
        """
        Return all unique keys found for the container's entity.
        """
        pass

    @abstractmethod
    def count(self):
        """
        Return a count of all unique keys found for the container's entity.
        """
        pass

    @abstractmethod
    def has_definition(self, element):
        """
        Return true if the given element contains an izpack definition for the container item.
        """
        pass

    @abstractmethod
    def has_reference(self, element):
        """
        Return true if the given element contains an izpack string reference.
        This method is used to define all the rules that allow the verifier to find
        references to the type of izpack entity being searched for.
        """
        pass

    @abstractmethod
    def get_spec_elements(self):
        """
        Returns a set of the elements defining each of the container's entities.
        """
        pass

    @abstractmethod
    def element_sort_key(self):
        """
        Returns the key to use when sorting elements for this container.
        """
        pass

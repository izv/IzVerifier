from bs4 import BeautifulSoup

__author__ = 'fcanas'


class IzPaths():
    """
    Class responsible for providing paths to specific IzPack resources and spec files.
    """
    specs = ['variables', 'conditions', 'dynamicvariables', 'resources', 'panels', 'packs']

    def __init__(self, path):
        """
        Initialize the installer's root path.
        """
        self.root = path
        self.parse_paths()


    def parse_paths(self):
        """
        Extracts paths to available izpack resources and spec files from the
        installer's install.xml spec.
        """
        self.paths = {}
        self.soup = BeautifulSoup(open(self.root + 'install.xml'))
        for spec in self.specs:
            self.paths[spec] = self.find_path(spec)


    def find_path(self, spec):
        """
        Find the path for the spec in the install.xml file.
        """
        path = None
        element = self.soup.find(spec)
        if element:
            child = element.find('xi:include')
            path = child['href']
        return path

    def get_path(self, spec):
        """
        Returns a path to the spec file, or None if there isn't any.
        """
        return self.root + self.paths[spec]







from bs4 import BeautifulSoup

__author__ = 'fcanas'


class IzPaths():
    """
    Class responsible for providing paths to specific IzPack resources and spec files.
    """
    specs = {
        'variables': 'variables.xml',
        'conditions': 'conditions.xml',
        'dynamicvariables': 'dynamic_variables.xml',
        'resources': 'resources.xml',
        'panels': 'panels.xml',
        'packs': 'packs.xml'
    }
    
    def __init__(self, path):
        """
        Initialize the installer's root path.
        """

        self.set_paths(path)
        self.parse_paths()
        self.find_resources()

    def set_paths(self, path):
        """
        Takes a path to an install.xml file and sets paths to spec files, resources, and root.
        """
        self.install = path
        self.izpack = path.replace('install.xml', '')
        self.root = path.replace('izpack/install.xml', '')
        self.res_path = path.replace('izpack/install.xml', 'resources/')


    def parse_paths(self):
        """
        Extracts paths to available izpack resources and spec files from the
        installer's install.xml spec.
        """
        self.paths = {}
        self.soup = BeautifulSoup(open(self.install))
        for spec in self.specs.keys():
            spec_file = self.find_path(spec)
            if spec_file:
                # If spec file exists
                self.paths[spec] = self.izpack + spec_file
            else:
                # If specs are held inside install.xml
                self.paths[spec] = self.install


    def find_path(self, spec):
        """
        Find the path for the spec in the install.xml file.
        """
        path = None
        element = self.soup.find(spec)
        if element:
            child = element.find('xi:include')
            if child: # if xi:include exists, specs are external.
                path = child['href']
            else:
                # Internal specs.
                path = None
        else:
            # No spec defined in file, assume default location.
            path = self.specs[spec]
        return path

    def get_path(self, spec):
        """
        Returns a path to the spec file, or None if there isn't any.
        """
        if not self.paths[spec]:
            return None
        else:
            return self.paths[spec]

    def find_resources(self):
        """
        Parse the install.xml resources and extract paths to available resource files.
        """
        self.resources = {}
        path = self.get_path('resources')

        if not path:
            rsoup = self.soup
        else:
            rsoup = BeautifulSoup(open(path))

        self.find_langpacks(rsoup)

    def find_langpacks(self, soup):
        langpacks = []

        for res in soup.find_all('res'):
            self.paths[res['id']] = self.res_path + res['src']
            if 'CustomLangPack.xml' in res['id']:
                langpacks.append((res['id'], self.res_path + res['src']))
        self.resources['langpacks'] = langpacks
        self.paths['strings'] = langpacks[0][1]


    def get_langpacks(self):
        """
        Returns a list of found langpacks in the form:
        [
            (langpack_id, langpack_path),
            ...
        ]
        """
        return self.resources['langpacks']



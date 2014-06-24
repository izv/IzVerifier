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
        self.izpack = path + '/izpack/'
        self.res_path = path + '/resources/'
        self.parse_paths()
        self.find_resources()


    def parse_paths(self):
        """
        Extracts paths to available izpack resources and spec files from the
        installer's install.xml spec.
        """
        self.paths = {}
        self.soup = BeautifulSoup(open(self.izpack + 'install.xml'))
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
        if not self.paths[spec]:
            return None
        else:
            return self.izpack + self.paths[spec]

    def get_resource_path(self, res):
        """
        Return path to a resource file or None if it doesn't exist.
        """
        if not self.paths[res]:
            return None
        else:
            return self.res_path + self.paths[res]

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
            self.paths[res['id']] = res['src']
            if 'CustomLangPack.xml' in res['id']:
                langpacks.append((res['id'], self.res_path + res['src']))
        self.resources['langpacks'] = langpacks


    def get_langpacks(self):
        """
        Returns a list of found langpacks in the form:
        [
            (langpack_id, langpack_path),
            ...
        ]
        """
        return self.resources['langpacks']



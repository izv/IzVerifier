import os
from os.path import dirname
from bs4 import BeautifulSoup
import re
from IzVerifier.exceptions.IzVerifierException import MissingFileException

__author__ = 'fcanas'


class IzPaths():
    """
    Class responsible for providing paths to specific IzPack resources and spec files.
    """
    
    def __init__(self, specs, resources, properties=None):
        """
        Initialize the installer's root path.
        """
        if not properties:
            properties = {}
        self.init_collections()
        self.properties = properties
        self.set_paths(specs, resources)
        self.parse_paths()
        self.find_resources()

    def init_collections(self):
        """
        Initialize collections to their default values.
        """
        # Default paths to spec files relative to specs folder.
        self.specs = {
            'BASE': '',
            'variables': 'variables.xml',
            'conditions': 'conditions.xml',
            'dynamicvariables': 'dynamic_variables.xml',
            'dynamic_variables': 'dynamic_variables.xml',
            'resources': 'resources.xml',
            'panels': 'panels.xml',
            'packs': 'packs.xml',
            'install': 'install.xml',
            'ProcessPanel.Spec': 'ProcessPanel.Spec.xml',
            'core-packs': 'packs.xml'
        }

        # Default paths to resource files relative to specs folder.
        self.resources = {
            'BASE': '',
            'userInputSpec': 'userInputSpec.xml',
            'strings': 'CustomLangPack.xml'
        }

        self.langpacks = {}

    def set_paths(self, specs, resources):
        """
        Takes base paths to specs and resources.
        """
        self.install = 'install.xml'
        self.specs_path = path_format(specs)
        self.root = path_format(dirname(dirname(self.specs_path)) + '/')
        self.res_path = path_format(resources)
        self.resources['BASE'] = self.res_path
        self.specs['BASE'] = self.specs_path

    def parse_paths(self):
        """
        Extracts paths to available izpack resources and spec files from the
        installer's install.xml spec.
        """
        self.soup = BeautifulSoup(open(self.get_path('install')))
        for spec in self.specs.keys():
            spec_file = self.find_specs_path(spec)
            if spec_file:
                # If spec file exists
                self.specs[spec] = path_format(spec_file)
            else:
                # If specs are held inside install.xml
                self.specs[spec] = self.install

    def find_specs_path(self, spec):
        """
        Find the path for the spec in the install.xml file.
        """
        element = self.soup.find(spec)
        if element:
            child = element.find('xi:include')
            if child:  # if xi:include exists, specs are external.
                path = self.properties.substitute(child['href'])
            else:
                # Internal specs.
                path = None
        else:
            # No spec defined in file, assume default location.
            path = self.specs[spec]
        return path

    def get_path(self, name):
        """
        Returns a path to the spec or resources file, or None if there isn't any.
        """
        for col in [self.specs, self.resources]:
            if name in col:
                return force_absolute(col['BASE'], col[name])
        raise MissingFileException(name)

    def find_resources(self):
        """
        Parse the install.xml resources and extract paths to available resource files.
        """
        path = self.get_path('resources')

        if not path:
            rsoup = self.soup
        else:
            rsoup = BeautifulSoup(open(path))

        self.parse_resources(rsoup)

    def parse_resources(self, soup):
        """
        Parse the install.xml (or resources.xml) soup to find all available resources.
        """
        for res in soup.find_all('res'):
            if 'customlangpack' in res['id'].lower():
                self.find_langpack_path(res)
            else:
                rid = remove_xml(res['id'])
                self.resources[rid] = path_format(self.properties.substitute(res['src']))

    def find_langpack_path(self, langpack):
        """
        Finds a langpack path from the given xml langpack element
        """
        lid = langpack['id']
        src = path_format(self.properties.substitute(langpack['src']))
        if '.xml_' in lid:
            self.langpacks[lid[-3:]] = src

        if not 'default' in self.langpacks:
            self.langpacks['default'] = src
            self.resources['strings'] = src

    def get_langpacks(self):
        """
        Returns a dict of found langpacks in the form:
        {
            'id', 'src'
            ...
        }
        """
        return self.langpacks

    def get_langpack_path(self, lid='default'):
        """
        Returns the path to the langpack with the given localization id.
        """
        path = self.langpacks[lid]
        return force_absolute(self.res_path, path)


def remove_xml(rid):
    """
    Removes the .xml from a resource or spec id.
    """
    if '.xml' in rid[-4:]:
        return rid[:-4]
    else:
        return rid


def force_absolute(base, path):
    """
    Ensures that the base path is not appended to an absolute path.
    """
    if base in path:
        return path
    else:
        return path_format(base + path)


def path_format(path):
    """
    Ensures the path is formatted correctly:

    Folder ends in a '/', and a path to a file does not.

    Removes any double '//'.
    """
    if os.path.isdir(path):
        if path[-1] != '/':
            path += '/'
    return re.sub(r'/+/', '/', path)




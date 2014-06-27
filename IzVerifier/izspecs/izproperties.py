from UserDict import UserDict
from bs4 import BeautifulSoup

__author__ = 'fcanas'

class IzProperties(dict):
    """
    Responsible for parsing and containing any properties used by IzPack's installation spec files.
    """
    def __init__(self, path):
        """
        Initialize paths to properties and begin parsing.
        """
        dict.__init__(self)
        if 'pom.xml' in path:
            self.parse_pom_properties(path)
        else:
            self.parse_properties(path)


    def parse_properties(self, path):
        """
        Finds properties defined in properties file at specified path adds them to map.
        """
        soup = BeautifulSoup(open(path,'r'))
        properties = soup.find_all('properties')

        for props in properties:
            for prop in props.find_all('property'):
                try:
                    self[prop['name']] = prop['value']
                except Exception:
                    continue

    def parse_pom_properties(self, path):
        """
        Special parser for pom.xml file properties.
        """
        soup = BeautifulSoup(open(path,'r'), 'xml')
        properties = soup.find_all('properties')

        # add the basedir property
        self['basedir'] = path.replace('pom.xml','')

        for props in properties:
            for prop in props.find_all(recursive=False):
                try:
                    self[str(prop.name)] = str(prop.string)
                except Exception, e:
                    continue

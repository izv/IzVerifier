from bs4 import BeautifulSoup
import re

__author__ = 'fcanas'


class IzProperties(dict):
    """
    Responsible for parsing and containing any properties used by IzPack's installation spec files.
    """
    def __init__(self, path):
        """
        Initialize paths to properties and begin parsing.
        """
        # noinspection PyTypeChecker
        dict.__init__(self)
        if 'pom.xml' in path:
            self.parse_pom_properties(path)
        else:
            self.parse_properties(path)

    def parse_properties(self, path):
        """
        Finds properties defined in properties file at specified path adds them to map.
        """
        soup = BeautifulSoup(open(path, 'r'))
        properties = soup.find_all('properties')

        for props in properties:
            for prop in props.find_all('property'):
                try:
                    self[prop['name']] = prop['value']
                except KeyError:
                    continue

    def parse_pom_properties(self, path):
        """
        Special parser for pom.xml file properties.
        """
        soup = BeautifulSoup(open(path, 'r'), 'xml')
        properties = soup.find_all('properties')

        # add the basedir property
        self['basedir'] = path.replace('pom.xml', '')

        for props in properties:
            for prop in props.find_all(recursive=False):
                try:
                    self[str(prop.name)] = str(prop.string)
                except KeyError:
                    continue

    def substitute(self, string):
        """
        Puts the given string through variable substitution: replacing all incidences of
        ${key} for the key's value if it exists. If key doesn't exist, it returns
        the unsubstituted variable. The substitution is performed iteratively until all
        possible variables have been subbed.
        """
        while True:
            old_string = string
            matches = re.findall('\$\{.*\}', string)

            if not matches:
                break

            for match in matches:
                value = self._substitute(match)
                if not value is match:
                    string = str.replace(string, match, value)

            if string is old_string:
                break
        return string

    def _substitute(self, key):
        """
        Substitutes a given key for its value. If the value doesn't exist,
        return the key.

        Key is in the form ${some.key}
        """
        stripped_key = key[2:-1]
        if stripped_key in self:
            return self[stripped_key]
        else:
            return key

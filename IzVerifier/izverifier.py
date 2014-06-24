__author__ = 'fcanas'

from IzVerifier.exceptions.IzVerifierException import IzArgumentsException
from IzVerifier.izspecs.izpaths import IzPaths


class IzVerifier():
    """
    Responsible for parsing an IzPack installer's spec files and any user-specified source code,
    and finding inconsistencies with izpack's conditions, variables, strings, process panel jobs,
    etc.
    """

    def __init__(self, args):
        """
        Main entry point for IzVerifier. Args is a dictionary in this form:

        args = {
            'installer': path                   # Path to installer's root folder.
            'sources': [path1, path2, ...]      # Path(s) to associated source code roots.
        }
        """
        self.installer = args.get('installer', None)
        self.sources = args.get('sources', [])

        if not self.installer:
            raise IzArgumentsException("No Path to Installer Specified")
            exit(1)

        self.paths = IzPaths(self.installer)






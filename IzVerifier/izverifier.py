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
            'specs': [spec1, spec2, ...]        # Spec files to subject to verification process.
        }
        """
        validate_arguments(args)
        self.installer = args.get('installer')
        self.sources = args.get('sources', [])
        self.paths = IzPaths(self.installer)


def validate_arguments(args):
    """
    Throws exceptions if required args are missing or invalid.
    """
    if not args.has_key('installer'):
         raise IzArgumentsException("No Path to Installer Specified")
         exit(1)
    if not args.has_key('specs'):
         raise IzArgumentsException("No Spec files Specified for Verification")
         exit(1)


def undefined(key_set, tup_set):
    """
    Returns the subset of keys from tup_set not present in key_set.
    key_set is a simple set of string keys.
    up_set is a set of tuples: tup[0] is the key of that tuple.
    """
    return set([tup for tup in tup_set if not quote_remover(tup[0]) in key_set])


def unused(key_set, tup_set):
    """
    Returns the subset of key_set not present in tup_set.
    key_set is a simple set of string keys.
    up_set is a set of tuples: tup[0] is the key of that tuple.
    """
    if not tup_set:
        return key_set
    return set([key for key in key_set if not key in zip(*tup_set)[0]])


def quote_remover(key):
    """
    Extracts the actual key of the item passed in.
    TODO: seriously do this minus recursion, idiot.
    """
    if key.startswith('"') and key.endswith('"'):
        return key[1:-1]
    if '=' in key:
        key = quote_remover(''.join(key.split('=')[1:]))
    return key

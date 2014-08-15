from IzVerifier.izspecs.containers.izclasses import IzClasses

__author__ = 'fcanas'

import unittest

from IzVerifier.izspecs.containers.izconditions import IzConditions
from IzVerifier.izspecs.containers.izstrings import IzStrings
from IzVerifier.izspecs.containers.izvariables import IzVariables
from IzVerifier.izverifier import IzVerifier
from IzVerifier.izspecs.containers.constants import *


path1 = 'data/sample_installer_iz5/izpack/'
path2 = 'data/sample_installer_iz5/resources/'
source_path2 = 'data/sample_code_base/src/'
pom = 'data/sample_installer_iz5/pom.xml'


class TestVerifier(unittest.TestCase):
    """
    Basic testing of verifier class.
    """

    def setUp(self):
        args = {
            'specs_path': path1,
            'sources': [source_path2],
            'resources_path': path2,
            'pom': pom,
            'specs': ['conditions', 'strings', 'variables']
        }
        self.izv = IzVerifier(args)
        self.izv.reporter.set_terminal_width()  # Sets width to width of terminal

    def test_IzPaths(self):
        """
        Testing install.xml path parsing.
        """
        specs = [('variables', 'variables.xml'),
                 ('conditions', 'conditions.xml'),
                 ('dynamicvariables', 'dynamic_variables.xml'),
                 ('resources', 'resources.xml'),
                 ('panels', 'panels.xml'),
                 ('packs', 'packs.xml')]

        self.assertTrue(self.izv != None)
        for spec in specs:
            path = self.izv.paths.get_path(spec[0])
            self.assertTrue(spec[1] in path,
                            msg=path + "!=" + spec[1])

    def test_IzConditions(self):
        """
        Testing the strings container.
        """
        conditions = self.izv.paths.get_path('conditions')
        self.assertEquals(conditions, 'data/sample_installer_iz5/izpack/conditions.xml')

        izc = IzConditions(conditions)
        self.assertTrue(izc != None)

        # Test for number of keys in conditions.xml plus white list
        num = len(izc.get_keys()) - len(izc.properties[WHITE_LIST])
        print num
        self.assertEquals(num, 12, str(num) + "!=12")

    def test_langpack_paths(self):
        """
        Test that we parsed the langpack paths from resources.xml
        """
        langpacks = [('default', 'data/sample_installer_iz5/resources/langpacks/CustomLangPack.xml'),
                     ('eng', 'data/sample_installer_iz5/resources/langpacks/CustomLangPack.xml')]

        for tpack, fpack in zip(langpacks, self.izv.paths.get_langpacks().keys()):
            self.assertEquals(tpack[1], self.izv.paths.get_langpack_path(tpack[0]))


    def test_IzStrings(self):
        """
        Testing the strings container.
        """
        langpack = self.izv.paths.get_langpack_path()

        izs = IzStrings(langpack)
        self.assertTrue(izs != None)

        # Test for number of strings
        num = len(izs.get_keys())
        self.assertEquals(num, 4, str(num) + '!=4')

    def test_IzVariables(self):
        """
        Testing the variables container.
        """
        variables = self.izv.paths.get_path('variables')
        self.assertEquals(variables, 'data/sample_installer_iz5/izpack/variables.xml')

        izv = IzVariables(variables)
        self.assertTrue(izv != None)
        num = len(izv.get_keys()) - len(izv.properties[WHITE_LIST])
        self.assertEquals(num, 3, str(num) + '!=3')

    def test_verifyStrings(self):
        """
        Verify strings in sample installer
        """
        hits = self.izv.verify('strings', verbosity=2)
        undefined_strings = {'some.string.4',
                             'my.error.message.id.test',
                             'password.empty',
                             'password.not.equal',
                             'some.user',
                             'some.user.panel.info',
                             'some.user.password',
                             'some.user.password.confirm',
                             'some.string.5',
                             'some.string.6',
                             'hello.world'}

        non_strings = {'db.driver'}

        found_strings, location = zip(*hits)
        for id in undefined_strings:
            self.assertTrue(id in found_strings)

        for id in non_strings:
            self.assertTrue(id not in found_strings)



    def test_verifyConditions(self):
        """
        Verify conditions in sample installer.
        """
        hits = self.izv.verify('conditions', verbosity=2)

        undefined_conditions = {'myinstallerclass.condition',
                                'some.condition.2',
                                'some.condition.1'}

        found_conditions, location = zip(*hits)

        for id in undefined_conditions:
            self.assertTrue(id in found_conditions)

    def test_verifyVariables(self):
        """
        Verify conditions in sample installer.
        """
        hits = self.izv.verify('variables', verbosity=1)
        num = len(hits)
        self.assertTrue(num == 5)

    def test_verifyAll(self):
        """
        Verify all specs on sample installer.
        """
        hits = self.izv.verify_all(verbosity=1)
        num = len(hits)
        assert (num != 0)

    def test_findReference(self):
        """
        Find some references to items in source code and specs.
        """
        hits = self.izv.find_references('some.user.password', verbosity=2)
        self.assertEquals(len(hits), 2)

        hits = self.izv.find_references('password.empty', verbosity=2)
        self.assertEquals(len(hits), 1)

        # Ref in code
        hits = self.izv.find_references('some.string.3', verbosity=2)
        self.assertEquals(len(hits), 1)

        # var substitution not yet implemented for find references, so this
        # test will miss the ref in Foo.java
        hits = self.izv.find_references('some.condition.1', verbosity=2)
        self.assertEquals(len(hits), 1)

    def test_verifyClasses(self):
        """
        Testing the izclasses container.
        """
        classes = IzClasses(source_path2)
        classes.print_keys()
        self.assertEquals(len(classes.get_keys()), 1)

        hits = self.izv.verify('classes', verbosity=2)
        self.assertEquals(len(hits), 5)

        referenced = self.izv.get_referenced('classes')
        self.assertTrue(referenced.has_key('com.sample.installer.Foo'))
        self.assertTrue(referenced.has_key('com.sample.installer.SuperValidator'))
        self.assertTrue(referenced.has_key('com.sample.installer.SuperDuperValidator'))
        self.assertTrue(referenced.has_key('com.sample.installer.BarListener'))


if __name__ == '__main__':
    unittest.main()


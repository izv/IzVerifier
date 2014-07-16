__author__ = 'fcanas'

import termhelper

class Reporter:
    """
    Responsible for displaying results and recording them to log files.
    """

    def __init__(self):
        self.set_terminal_width()  # default width of terminal

    templates = {
        'test': '[ {0:.<{2}}{1:.>{3}} ]',
        'set_tuples': '{0:.<{2}}{1:.>{3}}',
        'set_items': '{0:.<{1}}'
    }

    def report_test(self, test, items):
        """
        Report header for specification results.
        """
        template = self.templates['test']
        test_width = self.width - 4  # Test tuple is wrapped in [  ], which is 4 characters
        print template.format(test, len(items), 0, test_width - len(test), len(test))
        self.report_set(items)

    def report_set(self, entities):
        """
        Human-readable report for a set of unverified entities.
        """
        for item in sorted(entities):
            if type(item) is tuple:
                template = self.templates['set_tuples']
                tuple_padding = self.get_tuple_padding(item)
                print template.format(item[0], item[1], tuple_padding, len(item[1]))
            else:
                template = self.templates['set_items']
                print template.format(item, self.width)

    def set_terminal_width(self):
        """
        Overwrites default terminal width with the width of the current terminal window.
        """
        height, width = termhelper.terminal_height_width()
        self.width = max(width, 40)

    def get_tuple_padding(self, item):
        """
        Returns the proper length of padding for a tuple.
        The first item is allocated at least 30 characters of space.
        The second item is allocated up to 50 characters.
        """

        # Default padding, used when both items fit in their own allocated space without shifting the padding
        # and when a line break is unavoidable (default padding keeps the output more readable than no padding
        # in the case of a very short first item with a very long second item)
        tuple_padding = max(30, self.width - 50, len(item[0]) + 1)

        # If the combined length of the items is short enough to fit on one line, avoid a line break
        if len(item[0]) + len(item[1]) < self.width:

            # If the first item fills up its allocated space, pad by 1 character
            if len(item[0]) >= max(30, self.width - 50):
                tuple_padding = len(item[0]) + 1

            # If the second item is longer than its allocated space, shorten the padding to avoid a line break
            elif len(item[1]) > min(self.width - 30, 50):
                tuple_padding = self.width - len(item[1])

        return tuple_padding

def display_paths(paths):
    """
    Human readable output for displaying dependency paths.
    """

    for path in paths:
        tab = 0
        for node in path:
            if type(node[0]) is tuple:
                id = node[0][0]
            else:
                id = node[0]
            if tab:
                branch = u'\u02ea\u2192 '
            else:
                branch = ''
            tab += 3
            print " " * tab + branch + str(id) + " : (" + str(node[1]) + ")"
    print
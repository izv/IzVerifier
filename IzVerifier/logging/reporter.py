__author__ = 'fcanas'

import termhelper


class Reporter:
    """
    Responsible for displaying results and recording them to log files.
    """

    def __init__(self, warg=0):
        self.width = warg
        self.set_terminal_width(warg)  # default width of terminal

    templates = {
        'test': '[ {0:.<{2}}{1:.>{3}} ]',
        'set_tuples': '{0:.<{2}}{1:.>{3}}',
        'set_items': '{0:.<{1}}',
        'path_display': '[ {0:.<{1}}FAIL ]'
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

    def set_terminal_width(self, warg=-1):
        """
        Overwrites default terminal width with the width of the current terminal window or the width arg passed
        in by user (if any and positive).
        """
        if warg <= 0:
            height, width = termhelper.terminal_height_width()
            self.width = max(width, 100)

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


    def display_paths(self, paths_dict):
        """
        Human readable output for displaying dependency paths.
        """
        def node_type(node):
            return " (type: {0})".format(str(node[1]))

        template = self.templates['path_display']

        for condition_id in paths_dict:
            for path_index, path in enumerate(list(paths_dict[condition_id])):
                tab = len(condition_id)
                for node_index, node in enumerate(path):
                    if node_index == 0:
                        if path_index == 0:
                            print template.format(condition_id + node_type(node), self.width - len('[ FAIL ]'))
                        else:
                            continue
                    else:
                        add_to_tab = 0
                        if type(node[0]) is tuple:
                            cid = node[0][0]
                            add_to_tab += len(cid)
                        else:
                            cid = node[0]
                            add_to_tab += len(cid)
                        if tab:
                            branch = u'\u02ea\u2192 depends on '
                            add_to_tab += len(branch)
                        else:
                            branch = ''

                        print " " * tab + branch + str(cid) + node_type(node)
                        tab += add_to_tab
            print
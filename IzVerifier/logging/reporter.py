__author__ = 'fcanas'

class Reporter:
    """
    Responsible for displaying results and recording them to log files.
    """
    templates = {
        'specs': ' [ {0:.<40}missing in specs{1:.>40} ] ',
        'code': ' [ {0:.<40}missing in code{1:.>40} ] ',
        'set_tuples': ' [ {0:.<40}{1:.>40} ] ',
        'set_items': ' [ {0:.<80} ] '
    }

    def report_header(self, specification, source, items):
        """
        Report header for specification results.
        """
        template = self.templates[source]
        print template.format(specification, len(items))
        self.report_set(items)

    def report_set(self, entities):
        """
        Human-readable report for a set of unverified entities.
        """
        for item in sorted(entities):
            if type(item) is tuple:
                template = self.templates['set_tuples']
                print template.format(item[0], item[1])
            else:
                template = self.templates['set_items']
                print template.format(item)


def display_paths(paths):
    """
    Human readable output for displaying dependency paths.
    """
    def node_printer(node):
        return str(node[0]) + "(" + node[1] + ")"

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
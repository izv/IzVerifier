import subprocess
import re
from bs4 import BeautifulSoup


class Seeker:
    """
    Responsible for finding references to specified izpack entities in an installer's spec xml files
    or in source code.
    """
    grep_location_pattern = "(.*?):"
    grep_comment_pattern = '^\s*[(//)*].+.*$'
    comment_matcher = re.compile(grep_comment_pattern)
    grep_whitelist_patterns = []

    def __init__(self, paths):
        self.paths = paths

    def search_specs_for_attributes(self, args):
        """
        Searches each spec file for any elements that pass the filter_fn, then
        finds occurrences of the given attributes in those elements, Returns a
        set of all values returned by the transform_fn when the found attribute values
        are its parameters.

        args = {
             'path': path to root of installer folder,
             'specs': a list of paths to spec files to search through,
             'filter_fn': a filtering function for xml elements,
             'attributes': a list of the attributes to extract from matching elements,
             'value_fn': a function that filters the extracted values,
             'transform_fn': a function to transform matching values to some form.
        }

         For example:
         in:
         specs = paths to the xml specs we are searching
         filter_fn = element.has_attr('condition') or element.has_attr('conditionid')
         attributes = ['condition','conditionid']
         transform_fn = izconditions.split_compound_conditions

         out:set(all the individual condition ids referenced by spec files, including those
         referenced as compound conditions like condA+condB, etc)

         the default transform_fn is just the identify function: ie it doesn't transform, just
         returns the input value.
        """
        values_found_for_attributes = set()

        specs = args['specs']
        filter_fn = args['filter_fn']
        attributes = args['attributes']
        value_fn = args.get('value_fn', lambda x: True)
        transform_fn = args.get('transform_fn', lambda x: x)
        white_list = args.get('white_list_patterns', [])

        # Search each of the spec files required for elements that pass the filters
        for spec in specs:
            hits = self.search_specs(filter_fn, spec)

            for tag in attributes:
                values = self.extract_attributes(hits, tag)

                # For each found value, transform it and add the result to the set
                for value in values:
                    transformation = transform_fn(value)
                    if isinstance(transformation, set) or isinstance(transformation, list):
                        for transformed_value in transformation:
                            if value_fn(transformed_value):
                                if not self.in_grep_whitelist(transformed_value, white_list):
                                    values_found_for_attributes.add((transformed_value, spec))
                    else:
                        if value_fn(transformation):
                            if not self.in_grep_whitelist(transformation, white_list):
                                values_found_for_attributes.add((transformation, spec))

        return values_found_for_attributes

    def search_specs_for_value(self, args):
        """
        Searches the given spec files for any instances of elements that pass the element_filter
        which hold attributes specified in the specs_list which in turn have the sought after
        value.

        Will return a set of tuples of the form (value, spec file) after transforming the value
        using the transform_fn.

        See description of args above.
        """
        value = args['id']

        def value_matcher(val):
            matcher = re.compile(value)
            return not matcher.match(val) is None

        args['value_fn'] = value_matcher

        hits = self.search_specs_for_attributes(args)
        return hits

    def find_id_references(self, args):
        """
        Performs a search for some entity defined by the search_properties argument.
        Search_properties is a dict, containing the following:

        id              : A string value we are looking for.
        specs           : A list of spec files to search.
        element_matcher : A function that takes an element as input, returns true if
                            this element is a target element.
        attributes      : A list of attributes to search for id in.
        transformer     : A function to transform the value, when found (can be identity function)
        patterns        : A list of grep string patterns for the target in source code, of the form:
                            (find_pattern, key_extract_pattern)
        source paths    : A list of source code paths to search.

        Returns all references found.
        """
        spec_hits = set()

        hits = self.search_specs_for_value(args)
        spec_hits |= hits

        source_hits = self.find_references_in_source(patterns=args['patterns'],
                                                     path_list=args['source_paths'],
                                                     vid=args['id'],
                                                     white_list_patterns=args['white_list_patterns'])

        return spec_hits | source_hits

    def find_references_in_source(self, patterns, path_list, white_list_patterns, vid=None):
        """
        Find all occurrences of these patterns at the source code in the given paths.
        """
        hits = set()
        if len(patterns) != 0:
            searches, extractors = zip(*patterns)
            combined_search_pattern = '|'.join(searches)
            combined_extract_pattern = '|'.join(extractors)

            for path in path_list:
                if vid:
                    search_pattern = combined_search_pattern.format('"' + vid + '"')
                    extract_pattern = combined_extract_pattern.format('"' + vid + '"')
                else:
                    search_pattern = combined_search_pattern.format('.*?')
                    extract_pattern = combined_extract_pattern.format('.*?')

                hits |= self.search_source_for_pattern(path,
                                                       search_pattern,
                                                       extract_pattern,
                                                       white_list_patterns)

        return set(hits)

    @staticmethod
    def match_literal(key):
        # "some literal string";
        literal_string = '^"[\w].*"$'
        literal_matcher = re.compile(literal_string)
        return literal_matcher.match(key)

    @staticmethod
    def match_compound(key):
        # ie. someVariable + "some literal";
        compound_mix = '^[\"\w].*[\+].+[\w].*$'
        compound_matcher = re.compile(compound_mix)
        return compound_matcher.match(key)

    @staticmethod
    def match_variable(key):
        # someVariable;
        variable = '^[\w]+$'
        variable_matcher = re.compile(variable)
        return variable_matcher.match(key)

    @staticmethod
    def match_method(key, pattern):
        method_matcher = re.search(pattern, key)
        return method_matcher

    @staticmethod
    def extract_key_from_method(key):
        extract_method = '\((.*)'
        extract_method_pattern = re.compile(extract_method)
        matched = re.search(extract_method_pattern, key)
        return matched.group(1)

    def process_key(self, key_and_location, white_list, search_pattern):
        """
        Input: a tuple of  (key, file location), and white_list of keys, and a search pattern
        Output: a tuple of a processed key and the location.
        """

        key = key_and_location[0]
        location = key_and_location[1]

        while self.match_method(key, search_pattern):
            key = self.extract_key_from_method(key)

        # this is a tricky key using strings and variables, probably runtime.
        if self.match_compound(key):
            return None
        elif self.match_literal(key):
            key = self.strip_quotes(key)
            return key, location
        # otherwise it's hopefully just a variable, likely runtime, but we can look for it.
        elif self.match_variable(key):
            key = self.find_variable_value(key, location, white_list)
            if key is not None:
                return key, location
        else:
            return None

    @staticmethod
    def strip_quotes(key):
        return key[1:-1]  # strip quotes

    def find_variable_value(self, variable, location, white_list):
        """
        Given a variable and its location, attempt to substitute it for its value. The white_list is
        compared against.
        """
        search_pattern = 'String {0} = \"'.format(variable)
        extract_pattern = 'String {0} = (\".*?\")'.format(variable)

        hits = list(self.search_source_for_pattern(location, search_pattern, extract_pattern, white_list))

        if hits:

            return hits[0][0]  # first hit
        else:
            return None  # unable to id this, so it's runtime.

    def extract_pattern_and_location_from_grep(self, line, extract_pattern):
        """
        Given a line of output from grep, extracts the pattern from the line and
        returns it as  a tuples holding the pattern and its location.
        """

        tuple_ = self.parse_grep_output(line, extract_pattern)
        if not tuple_ is None:
            return tuple_

    def is_valid_output(self, line, white_list):
        """
        Given a line of input from grep, checks to see if line is valid line of code.
        Rejects output in white_list and comments
        """
        if self.is_comment(line):
            return False
        elif self.in_grep_whitelist(line, white_list):
            return False
        else:
            return True

    def is_comment(self, output):
        """
        Filter out any lines that are parts of comments.
        """
        if ':' in output:
            loc, hit = output.split(':', 1)
        else:
            return False

        if self.comment_matcher.match(hit):
            return True
        else:
            return False

    def parse_grep_output(self, output, extract_pattern):
        """
        Given a line of output from a grep output, returns a tuple
        holding the key of the element and the file it was found in.
        """
        match_key = re.search(extract_pattern, output)
        match_loc = re.search(self.grep_location_pattern, output)
        if match_key and match_loc:
            for match in match_key.groups():
                if match is not None:
                    return match, match_loc.group(1)
        if match_key and not match_loc:
            for match in match_key.groups():
                if match is not None:
                    return match, "UNKNOWN"
        else:
            return None

    @staticmethod
    def search_specs(search_fn, path):
        """
        Scrapes the xml spec file given in path and returns a set of all elements meeting the
        search_fn condition.
        """
        try:
            soup = BeautifulSoup(open(path), 'xml')
        except IOError:
            return set()
        return soup.find_all(search_fn)

    @staticmethod
    def extract_attributes(elements, attribute):
        """
        Given a list of html elements, returns a set of the values of the given attribute.
        """
        values = set()
        for ele in elements:
            if ele.has_attr(attribute):
                atty = ele[attribute]
                if type(atty) is list:
                    for a in atty:
                        values.add(a)
                else:
                    values.add(atty)
        return values

    def search_source_for_pattern(self, path, search_pattern, extract_pattern, white_list):
        """
        Searches all files recursively from given path for the search_pattern.
        Returns a set of all lines containing that pattern.
        """
        keys = set()
        cmd_string = "grep -P -R -e '{0}' {1}".format(search_pattern, path)
        cmd = [cmd_string]
        try:
            output = subprocess.check_output(cmd, shell=True)
            for line in output.split("\n"):
                check_line = self.is_valid_output(line, white_list)
                if check_line is False:
                    key_and_location = None
                else:
                    key_and_location = self.extract_pattern_and_location_from_grep(line, extract_pattern)
                if key_and_location is None:
                    continue
                stripped_key_and_location = self.process_key(key_and_location, white_list, search_pattern)
                if stripped_key_and_location is not None:
                    keys.add(stripped_key_and_location)
        except subprocess.CalledProcessError:
            # no hits were found
            pass
        return keys

    def in_grep_whitelist(self, line, white_list_patterns):
        """
        Tests whether an output line from grep matches whitelist patterns,
        for example if it's a commented line.
        """
        for pat in self.grep_whitelist_patterns + white_list_patterns:
            if re.match(pat, line):
                return True
        return False









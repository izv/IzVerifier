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
            return (not matcher.match(val) == None)

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

        for path in path_list:
            for pattern in patterns:
                if vid:
                    key_pattern = pattern[0].format('"' + vid + '"')
                    extract_pattern = pattern[1].format('"' + vid + '"')
                else:
                    key_pattern = pattern[0].format('')
                    extract_pattern = pattern[1].format('.*?')

                hits |= self.search_source_for_pattern(path,
                                                       key_pattern,
                                                       extract_pattern,
                                                       white_list_patterns)

        # process the keys
        hits = self.strip_source_hits(hits, white_list_patterns)
        return set(hits)

    def strip_source_hits(self, hits, white_list):
        """
        Removes extra quotes from the keys of hits in source matches.
        ie. "uninstaller.warning" => uninstaller.warning

        Input: [(key, location),(key, location) ,...]

        Output: [(key, location),(key, location) ,...] with quotes stripped out of keys.
        """
        stripped = []
        for hit in hits:
            processed = self.process_key(hit[0], hit[1], white_list)
            if processed:
                stripped.append((processed, hit[1]))
        return stripped

    def process_key(self, key, location, white_list):
        """
        Input: a key, file location, and white_list of keys
        Output: a key with quotes removed, if necessary.
        """
        # "some literal string";
        literal_string = '^"[\w].*"$'
        literal_matcher = re.compile(literal_string)

        # ie. someVariable + "some literal";
        compound_mix = '^[\"\w].*[\+].+[\w].*$'
        compound_matcher = re.compile(compound_mix)

        # someVariable;
        variable = '^[\w].*$'
        variable_matcher = re.compile(variable)

        # this is a tricky key using strings and variables, probably runtime.
        if compound_matcher.match(key):
            return None
        elif literal_matcher.match(key):
            pass
        # otherwise it's hopefully just a variable, likely runtime, but we can look for it.
        elif variable_matcher.match(key):
            key = self.find_variable_value(key, location, white_list)
        return key

    def find_variable_value(self, variable, location, white_list):
        """
        Given a variable and its location, attempt to substitute it for its value. The white_list is
        compared against.
        """
        search_pattern = 'String {0} = \"'.format(variable)
        extract_pattern = 'String {0} = (\".*?\")'.format(variable)

        hits = list(self.search_source_for_pattern(location, search_pattern, extract_pattern, white_list))

        if hits:
            return variable + "=" + hits[0][0] # first hit
        else:
            return None  # unable to id this, so it's runtime.

    def search_source_for_pattern(self, path, search_pattern, key_pattern, white_list):
        """
        Searches source code for references to search_pattern, and returns a set
        of tuples of the form (key_pattern, location_in_source)
        """
        hits = self.search_source(search_pattern, path)
        keys_and_locations = self.extract_pattern_and_location_from_grep(hits, key_pattern, white_list)
        return keys_and_locations

    def extract_pattern_and_location_from_grep(self, lines, pattern, white_list):
        """
        Given a set of lines that are output from grep, extracts the pattern from each and
        returns it as  a set of tuples holding the pattern and its location.
        """
        tuples = set()
        for line in lines:
            if self.is_comment(line):
                continue
            if self.in_grep_whitelist(line, white_list):
                continue
            tuple_ = self.parse_grep_output(line, pattern)
            if not tuple_ is None:
                tuples.add(tuple_)
        return tuples

    def is_comment(self, output):
        """
        Filter out any lines that are parts of comments.
        """
        if ':' in output:
            loc,hit = output.split(':', 1)
        else:
            return False

        if self.comment_matcher.match(hit):
            return True
        else:
            return False

    def parse_grep_output(self, output, key):
        """
        Given a line of output from a grep output, returns a tuple
        holding the key of the condition and the file it was found in.
        """
        match_key = re.search(key, output)
        match_loc = re.search(self.grep_location_pattern, output)
        if match_key and match_loc:
            return match_key.group(1), match_loc.group(1)
        if match_key and not match_loc:
            return match_key.group(1), "UNKNOWN"
        else:
            return None

    @staticmethod
    def search_specs(search_fn, path):
        """
        Scrapes the xml spec file given in path and returns a set of all elements meeting the
        search_fn condition.
        """
        try:
            soup = BeautifulSoup(open(path))
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
                values.add(str(ele[attribute]))
        return values

    @staticmethod
    def search_source(search_pattern, path):
        """
        Searches all files recursively from given path for the search_pattern.
        Returns a set of all lines containing that pattern.
        """
        keys = set()
        cmd_string = "grep -R -e '{0}' {1}".format(search_pattern, path)
        cmd = [cmd_string]
        try:
            output = subprocess.check_output(cmd, shell=True)
            for line in output.split("\n"):
                keys.add(line)
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









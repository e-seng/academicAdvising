# An HTML parser which finds the links to program details.

from html.parser import HTMLParser
from src.majors import Major
from src.course import Course
from src.year import Year

class HomepageParser(HTMLParser):

    path_map = {}

    current_link = ""
    is_major = False
    current_title = ""
    current_class = ""

    new_year = False
    in_table = False

    data_index = 0
    year_index = 0

    def __init__(self):
        self.reset()
        self.strict = True
        self.convert_charrefs = True

        self.is_major = False
        self.new_year = False

        self.data_index = 0
        self.year_index = 0
        self.path_map = {}


    def handle_starttag(self, tag, attrs):
        """ Figure out if it's a new header or if int's just another course 
        within the current header. If it is the latter, then save the link
        unless it is otherwise not relevant
        """
        course_tags = ["a", "p"]
        title_tags = ["span"]

        if tag == "span" and attrs:
            self.is_major = True
        else:
            self.is_major = False

        if tag == "tbody": self.in_table = True
        if tag == "strong": self.new_year = True
        if tag == "td": self.data_index += 1

        if tag not in course_tags or not self.in_table: return

        for attr in attrs:
            if attr[0] != "href": continue
            if "#" not in attr[1]: continue

            self.current_link = attr[1]
            print("Found link -", self.current_link)


    def handle_data(self, data):
        """ Retrieve the overall header for each class - allows to sort between
        courses relatively easily
        """
        has_words = data.split()

        if self.new_year and "Year" in has_words:
            self.path_map[self.current_title].year_list.append(Year())
            self.year_index += 1
            print(data)
        else: self.new_year = False

        if self.current_link and has_words: self.current_class = data

        if self.is_major and has_words:
            self.current_title = data
            self.path_map[self.current_title] = Major()
            print("Found title -", self.current_title)
            self.year_index = 0
            self.data_index = 0


    def handle_endtag(self, tag):
        """ At the very end of every link, save the link in the corresponding
        major.
        """
        if not self.in_table and self.year_index < 1: return

        TERM_LIST = ["fall", "winter"]

        if tag == "tbody": 
            self.in_table = False
            self.current_link = ""

        if tag == "strong": self.new_year = False

        acceptable_tags = ["a"]
        link_has_words = self.current_link.split()
        title_has_words = self.current_title.split()

        if tag == "tr": self.data_index = 0

        if not link_has_words or not title_has_words: return

        if tag not in acceptable_tags: return

        new_course = Course(self.current_link)
        #self.path_map[self.current_title].append_course(new_course)

        term = TERM_LIST[self.data_index - 1]
        #self.path_map[self.current_title].set_term_course(new_course, term, self.year_index)
        self.path_map[self.current_title].set_term_course(self.current_class, term, self.year_index)


    def get_path_map(self):
        return self.path_map

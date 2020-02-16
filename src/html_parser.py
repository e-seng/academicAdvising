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
        course_tags = ["a"]
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

        if self.is_major and has_words:
            self.current_title = data
            self.path_map[self.current_title] = Major()
            print("Found title -", self.current_title)


    def handle_endtag(self, tag):
        """ At the very end of every link, save the link in the corresponding
        major.
        """
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
        self.path_map[self.current_title].append_course(new_course)

        term = TERM_LIST[self.data_index - 1]
        self.path_map[self.current_title].set_term_course(new_course, term, self.year_index)
        #pass


    def get_path_map(self):
        return self.path_map


class CourseParser(HTMLParser):
    current_course = None

    req_link = ""
    req_type = ""
    in_course = False
    found_title = False

    def __init__(self, course):
        self.reset()
        self.strict = True
        self.convert_charrefs = True
        is_title = False

        self.current_course = course
        self.set_couse_id()

    def set_couse_id(self):
        id_tag = self.current_course.link.split("#")[1]
        self.current_course.key = id_tag

    def get_req_id(self, link):
        id_tag = link.split("#")[1]
        return id_tag

    def handle_starttag(self, tag, attrs):
        acceptable_tags = ["a", "span"]

        if tag not in acceptable_tags: return

        for attr in attrs:
            #print(attr)
            if attr[0] == "name":
                if self.current_course.key == attr[1]: 
                    print("Found course with key", self.current_course.key)
                    self.in_course = True
                elif self.in_course:
                    print("Done parsing course")
                    self.in_course = False
                else:
                    self.req_link = ""
                    return

            if not self.in_course: return

            if tag == "span":
                if attr[1] == "course-code": self.found_title = True
                else: self.found_title = False

                self.req_type = attr[1]
                if "req" not in attr[1] or "course" not in attr[1]: 
                    self.req_type = ""
                    continue

            if tag == "a":
                if "href" in attr[0]: 
                    self.req_link = self.get_req_id(attr[1])
                    #continue


    def handle_data(self, data):
        if self.found_title: 
            title_data = data.split()

            if not title_data: return
            title_data = " ".join(title_data)
            if title_data in self.current_course.title: return
            self.current_course.title += (title_data + " ")


    def handle_endtag(self, tag):
        if tag != "a": return

        link_has_words = self.req_link.split()
        if not link_has_words: return

        if self.req_type == "course-prereq":
            self.current_course.append_prereq(self.req_link)
        if self.req_type == "course-coreq":
            self.current_course.append_coreq(self.req_link)
        if self.req_type == "course-antireq":
            self.current_course.append_antireq(self.req_link)

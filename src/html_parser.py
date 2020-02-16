# An HTML parser which finds the links to program details.

from html.parser import HTMLParser
from src.majors import Major
from src.course import Course

class HomepageParser(HTMLParser):

    path_map = {}

    current_link = ""
    is_major = False
    current_title = ""

    def __init__(self):
        self.reset()
        self.strict = True
        self.convert_charrefs = True
        self.is_major = False

        self.path_map = {}


    def handle_starttag(self, tag, attrs):
        """ Figure out if it's a new header or if int's just another course 
        within the current header. If it is the latter, then save the link
        unless it is otherwise not relevant
        """
        course_tags = ["a"]
        title_tags = ["span", "strong"]

        if tag == "span":
            self.is_major = True
        else:
            self.is_major = False

        if tag not in course_tags: return

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
        if "Concentration" in has_words: self.is_major = True

        if self.is_major and has_words:
            self.current_title = data
            self.path_map[self.current_title] = Major()
            print("Found title -", self.current_title)


    def handle_endtag(self, tag):
        """ At the very end of every link, save the link in the corresponding
        major.
        """
        acceptable_tags = ["a"]
        link_has_words = self.current_link.split()
        title_has_words = self.current_title.split()

        if not link_has_words or not title_has_words: return
        if tag not in acceptable_tags: return

        new_course = Course(self.current_link)
        self.path_map[self.current_title].append_course(new_course)
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

# A class defining each possible major path available
# Contains the prerequisites and anti-requisites of each path

class Major:
    course_reqs = []
    year_list = []

    def __init__(self):
        self.course_reqs = []
        self.year_list = []


    def append_course(self, course):
        """ Appends a given course into the list of course_requisites
        Prevents any duplicate courses from entering

        PARAMETERS
        ----------
            course - Course object
                A course which is required to complete the course path
        """
        for saved_course in self.course_reqs:
            if course.link == saved_course.link: return

        print("Saved -", course.link)
        self.course_reqs.append(course)


    def set_term_course(self, course, term, year):
        print("appended", course, "into", term, year)

        if year < 1: return

        print(year, self.year_list)
        self.year_list[year - 1].append_course(course, term)
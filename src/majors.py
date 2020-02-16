# A class defining each possible major path available
# Contains the prerequisites and anti-requisites of each path

class Major:
    course_reqs = []

    def __init__(self):
        self.course_reqs = []


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
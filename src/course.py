# Course details

class Course:
    title = ""
    key = 0
    prereq = []
    coreq = []
    antireq = []
    link = ""

    def __init__(self, l):
        self.link = l
        self.prereq = []
        self.coreq = []
        self.antireq = []

    def append_prereq(self, course_title):
        """ Appends a prerequisite to the current course

        PARAMETERS
        ----------
            course_title - String
                The title of the prerequisite
        """
        self.prereq.append(course_title)


    def append_antireq(self, course_title):
        """ Appends an antirequisite to the current course

        PARAMETERS
        ----------
            course_title - String
                The title of the antirequisite
        """
        self.antireq.append(course_title)

    def append_coreq(self, course_title):
        """ Appends a corequisite to the current course

        PARAMETERS
        ----------
            course_title - String
                The title of the corequisite
        """
        self.coreq.append(course_title)

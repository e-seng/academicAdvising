class Year:
    term_map = {"fall" : [],
        "winter" : []}
        #"spring" : [],
        #"summer" : []}

    def __init__(self):
        self.term_map = {"fall" : [],
            "winter" : []}
        #self.term_map["spring"] = []
        #self.term_map["summer"] = []


    def append_course(self, course, term):
        self.term_map[term].append(course)
#!/usr/bin/env python3

import os
import requests
import csv
import sys
import time

from src.html_parser import HomepageParser

def get_req_data(link):
    """ Gets the data from the homepage of a particular major found at the
    specified www.ucalgary.ca link

    Returns a list of majors and their corresponding course requisite links 
    gathered from the provided homepage

    PARAMETERS
    ----------
        link : String
            The link to the UCalgary homepage of the desired course
            specifically from the UCalgary Calendar
    """
    hp_parser = HomepageParser()

    print("Connecting to link...")
    resp = requests.get(link)
    content = resp.content.decode("utf-8")
    hp_parser.feed(content)

    path_map = hp_parser.get_path_map()
    hp_parser.close()

    resp.close()

    pop_list = []

    for key, major in path_map.items():
        req_list = major.course_reqs
        year_list = major.year_list

        if req_list or year_list: continue

        pop_list.append(key)

    for key in pop_list:
        print("Nothing found for key:", key, "\ndeleting...")
        path_map.pop(key)

    return path_map


def double_degree(discipline_map, major1, major2, max_courses_per_year):
    major1_field = major1[0]
    major1_name = major1[1]

    major2_field = major2[0]
    major2_name = major2[1]

    focus_major = discipline_map[major1_field][major1_name]
    second_major = discipline_map[major2_field][major2_name]

    for alt_year in second_major.year_list:
        for term, course_list in alt_year.term_map.items():
            for course in course_list:
                for year in focus_major.year_list:
                    for term, courses in year.term_map.items():
                        if len(courses) >= max_courses_per_year: continue
                        print("Appened", course, "to", major1_name)
                        courses.append(course)



def export_to_csv(discipline_map, max_courses_per_year):
    """ Exports the saved data from the UCalgary website into a comma separated
    value file. This file can then be accessible through a program such as
    Microsoft Excel.

    Parameters:
        discipline_map : Dict
            A dictionary containing all listed paths within a 
            discipline as specified by a specified website. Each 
            major should already contain course requirements and the 
            requisites to them.
    """
    file_exists = False

    for path, direct, file in os.walk("./"):
        if file == "out.csv": file_exists = True

    if file_exists: os.remove("./out.csv")

    with open("./out.csv", "+w", newline="") as csv_file:
        fieldnames = ["Field:",
            "Major:",
            "Year:",
            "Term:",
            "Courses:"
            ]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for field, major_map in discipline_map.items():
            csv_writer.writerow({"Field:" : field})
            for major_name, major in major_map.items():
                csv_writer.writerow({"Major:" : major_name})
                for index, year in enumerate(major.year_list):
                    csv_writer.writerow({"Year:" : index + 1})
                    for term, course_list in year.term_map.items():
                        csv_writer.writerow({"Term:" : term})
                        for course in range(max_courses_per_year):
                            
                            if course >= len(course_list):
                                course_name = "Open for Options"
                            else:
                                course_name = course_list[course]
                            csv_writer.writerow({"Courses:" : course_name})


def main():
    """
    Parameters:
        --test : runs a testing benchmark, not the actual thing.

    Note:
        This will require lots of time to complete and likely a really good,
        stable internet connection. This may be seen as a DoS attack on the host
        so it is best to use the school's wifi... probably
    """
    MAIN_LINK = "https://www.ucalgary.ca/pubs/calendar/current/{}"
    discipline_map = {}

    course_counter = 0

    # In a finished product, these will be user inputs
    discipline_exts = {"ENGG" : "en-4-1.html",
        "ELEC" : "en-4-4.html",
        "SE" : "en-4-9.html", 
        "COMP_SCI" : "sc-4-3-1.html"}

    max_courses_per_year = 5
    major2 = ("COMP_SCI", "Recommended Program Sequence BSc (Majors and Honours)")
    major1 = ("ELEC", "Electrical Engineering, Regular Program")

    if "--test" in sys.argv:
        discipline_exts = {"COMP_SCI" : "sc-4-3-1.html"}

        counter = 0
        for name, ext in discipline_exts.items():
            counter += 1
            link = MAIN_LINK.format(ext)
            print(name, link)
            discipline_map[name] = get_req_data(link)

        #test_course = discipline_map["COMP_SCI"]['Required Courses - BSc Major Program'].course_reqs[1]
        #get_course_info(test_course, MAIN_LINK)

        #print("Course Name:", test_course.title)
        #print("Course Key:", test_course.key)
        #print("Prereq:", test_course.prereq)
        #print("Coreq:", test_course.coreq)
        #print("Antireq:", test_course.antireq)
        return discipline_map

    start_time = time.time()

    for name, ext in discipline_exts.items():
        path_map = {}
        link = MAIN_LINK.format(ext)
        path_map = get_req_data(link)
        discipline_map[name] = path_map
        course_counter += 1

    #for name, path_map in discipline_map.items(): # ha this nesting
    #    for path, major in path_map.items():
    #        print("Switching to", name, path)
    #        for course in major.course_reqs: 
    #            get_course_info(course, MAIN_LINK)
    #            course_counter += 1

    double_degree(discipline_map, major1, major2, max_courses_per_year)
    export_to_csv(discipline_map, max_courses_per_year)
    end_time = time.time()

    sec_elapsed = end_time - start_time

    minutes = int(sec_elapsed / 60)
    seconds = sec_elapsed - minutes * 60

    time_elapsed = (str(minutes) + ":" + str(seconds))
    print("Finished parsing", course_counter, "fields in", time_elapsed)

    return discipline_map


if __name__ == "__main__":
    main()
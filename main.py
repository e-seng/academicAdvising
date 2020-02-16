#!/usr/bin/env python3

import os
import requests
import csv
import sys
import time

from src.html_parser import HomepageParser, CourseParser

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


def get_course_info(course, MAIN_LINK):
    """ Gets the remaining information of the course from the course's link
    attribute

    PARAMETERS
    ----------
        course : Course Object
            The course which information will be filled
    """
    course_parser = CourseParser(course)
    link_ext = course.link

    link = MAIN_LINK.format(link_ext)

    print("Connecting to link...")
    resp = requests.get(link)
    content = resp.content.decode("utf-8")

    course_parser.feed(content)
    course_parser.close()
    resp.close()


def find_conflicts(current_course, current_dis, discipline_map):
    """ Finds if any antirequisites conflict with other courses.

    Parameters:
        course : Course object
            the current course which that is being analyzed to see if there
            is any conflict with other courses
        discipline_map : Dict
            all of the other disciplines listed here
    """
    conflicts = []
    conflict_string = ""

    for name, path_map in discipline_map.items():
        if current_dis == name: continue
        for path, major in path_map.items():
            if current_course in major.course_reqs: continue
            for course in major.course_reqs:
                if course.key not in current_course.antireq: continue
                if name in conflicts: continue
                print("Found conflict with", name)
                conflicts.append(path + " : " + course.title)

    for course in conflicts:
        conflict_string += (course + " -- ")

    return conflict_string


def export_to_csv(discipline_map):
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
        fieldnames = ["Discipline:",
            "Path:",
            "Course Name:",
            "Course Key:", 
            "Prerequisites:", 
            "Corequisites:", 
            "Antirequisites:",
            "Conflicts With:"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for discipline, path_map in discipline_map.items():
            for path, major in path_map.items():
                for course in major.course_reqs:
                    print("Writing", course.title)
                    conflicts = find_conflicts(course, discipline,discipline_map)

                    csv_writer.writerow(
                        {"Discipline:" : discipline,
                        "Path:" : path,
                        "Course Name:" : course.title,
                        "Course Key:" : course.key,
                        "Prerequisites:" : course.prereq,
                        "Corequisites:" : course.coreq,
                        "Antirequisites:" : course.antireq,
                        "Conflicts With:" : conflicts
                        })


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

    discipline_exts = {"ENGG" : "en-4-1.html",
        "ELEC" : "en-4-4.html",
        "SE" : "en-4-9.html", 
        "COMP_SCI" : "sc-4-3-1.html"}

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
    course_counter = 0

    for name, ext in discipline_exts.items():
        path_map = {}
        link = MAIN_LINK.format(ext)
        path_map = get_req_data(link)
        discipline_map[name] = path_map

    for name, path_map in discipline_map.items(): # ha this nesting
        for path, major in path_map.items():
            print("Switching to", name, path)
            for course in major.course_reqs: 
                get_course_info(course, MAIN_LINK)
                course_counter += 1

    #export_to_csv(discipline_map)
    end_time = time.time()

    sec_elapsed = end_time - start_time

    minutes = int(sec_elapsed / 60)
    seconds = sec_elapsed - minutes * 60

    time_elapsed = (str(minutes) + ":" + str(seconds))
    print("Finished parsing", course_counter, "courses in", time_elapsed)

    return discipline_map


if __name__ == "__main__":
    main()
import difflib
from datetime import datetime
from pydriller import repository
import json
import typing
import re


# Return the size of a single commit
# The size is calculated by the added lines plus deleted lines
# Probably separate the size by SLOC e.g 1-100, 100-200, ....
def get_commit_size(files):
    """
    return the size of a commit
    :param files: files that has been modified in that commit
    :return: the size of the commit
    """

    commit_size = 0
    for m in files:
        # print(m.added_lines, m.deleted_lines)
        temp = m.added_lines + m.deleted_lines
        commit_size += temp

    return commit_size


# determine whether a file is a test file by checking if the code has import test libraries
# this method has not been run or tested
# the regex exp follows (Borle,2016)
def has_import_statement(file):
    regexStr = """(org\.junit)|
                (org\.junit\.Test)|
                (junit\.framework\.\*)|
                (junit\.framework\.Test)|
                (junit\.framework\.TestCase)|
                (org\.testng\.*)|
                (android\.test\.*)$"""

    matchObj = None

    try:
        if file.source_code is not None:
            matchObj = re.search(regexStr, file.source_code)
    except:
        with open("ErrorMsg.txt", "a") as text_file:
            text_file.write(regexStr + ", " + file.filename)
        # print(regexStr, file.source_code)
    finally:
        if matchObj is not None:
            return True
        else:
            return False


# find the creation of all test files
# and store filename and commit time into json file
def parse_repo(filename):
    """
    parse the repository by extracting the file name and the date of creation
    :parameter filename is the target json file where data are stored
    """
    file_date = {}
    for commit in repository.Repository("repos/" + filename, only_no_merge=True,
                                        only_modifications_with_file_types=['.java']).traverse_commits():  #
        print(commit.committer_date)
        for file in commit.modified_files:
            if file.filename in file_date.keys():
                continue
            else:
                commit_size = get_commit_size(commit.modified_files)  # calculate the size of the commit
                print(commit_size)
                file_date[file.filename] = [str(commit.committer_date), commit_size, has_import_statement(file)]

    file = open(filename + ".json", 'w')
    temp = json.dumps(file_date)
    file.write(temp)
    file.close()
    return 0


def read_json(filename):
    """
    read json file to dictionary
    :parameter filename is the target json file where data are stored
    :return a dictionary eg. {filename : [date, commit size]}
    """
    file = open(filename + ".json", 'r')
    content = json.loads(file.read())
    return content


def sanitize_files_list(dictionary):
    """
    remove all files that are not .java
    :parameter dictionary is the source dictionary that lists all filename and date of creation
    :return a dictionary eg. {filename : [date, commit size]}
    """
    sanitized_list = {}
    for key in dictionary:
        if ".java" in key:
            sanitized_list[key] = dictionary[key]
    return sanitized_list


def test_class_correspond(dictionary):
    """
    iterate the dictionary and find all class and their corresponding test class
    :parameter dictionary is the source dictionary that lists all filename and date of creation
    :return a dictionary of all matching tests and classes eg. {class : [test_class, commit size of class, commit size of test class]}
    """
    all_tests = {}
    result = {}
    for key in dictionary:  # creat a list that contains only test classes
        if "test" in key.lower():  # this is a test class
            all_tests[key] = dictionary[key]
    # print(all_tests)

    for key in all_tests:
        dictionary.pop(key)  # remove test file from the original list

    for key in all_tests:  # key is the current filename of the test class
        for temp in dictionary:  # temp is the filename of the original file list
            # get all test file with a regex match
            # difflib.SequenceMatcher(isjunk=None, a=temp, b=key)
            striped = key.lower().replace("test", "").lstrip("_-").replace(".java", "").rstrip(
                "_-") + ".java"  # name of the test file
            # print(striped)
            if striped == temp.lower():  # current filename of source code
                result[temp] = [key, dictionary[temp][0], all_tests[key][0], dictionary[temp][1], all_tests[key][1]]
    return result


# parse_repo("hbase")  # read the repository and list all files and creation date to json
# parse_repo("dolphinscheduler")  # read the repository and list all files and creation date to json
# parse_repo("druid")  # read the repository and list all files and creation date to json
# parse_repo("hudi")  # read the repository and list all files and creation date to json
# parse_repo("phoenix")  # read the repository and list all files and creation date to json
# parse_repo("ignite")  # read the repository and list all files and creation date to json
# parse_repo("activemq")  # read the repository and list all files and creation date to json
# parse_repo("ozone")  # read the repository and list all files and creation date to json
# parse_repo("hive")  # read the repository and list all files and creation date to json
# parse_repo("accumulo")  # read the repository and list all files and creation date to json
# parse_repo("cassandra")  # read the repository and list all files and creation date to json
# parse_repo("asterixdb")  # read the repository and list all files and creation date to json
# parse_repo("geode")  # read the repository and list all files and creation date to json
# parse_repo("cxf")  # read the repository and list all files and creation date to json
# parse_repo("iceberg")  # read the repository and list all files and creation date to json
# parse_repo("kafka")  # read the repository and list all files and creation date to json

file_dictionary = sanitize_files_list(read_json("hbase"))  # read json, remove any file that are not .java
# print(file_dictionary)
test_correspond = test_class_correspond(file_dictionary)  # find all corresponding test classes in json
print(test_correspond)


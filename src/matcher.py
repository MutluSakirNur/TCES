import os
import logging

from database import getCoursesBySchoolAndDept

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def jaccard_similarity(str, str2):
    """returning jaccard similarity ratio of two string"""
    inters = len(set.intersection(*[set(str), set(str2)]))
    union = len(set.union(*[set(str), set(str2)]))
    if (union != 0):
        return (inters / float(union))
    else:
        return 0


def clean_text(str):
    word_list = []
    str = str.lower()
    str = clean_stop_word(str)
    str = clean_delimiters(str)
    word_list = most_freq_words_list(str)
    return word_list


def clean_delimiters(str):
    delimiter = [",", ".", "'", '"', "?", "!", "#", "*", "/", "\\", "(", ")", "=", "&", "-", "1", "2", "3", "4", "5",
                 "6", "7", "8", "9", "0"]
    for i in range(len(delimiter)):
        str = str.replace("{}".format(delimiter[i]), "")
    return str


def clean_stop_word(str):
    with open(current_path + '/stop_words_turkish') as f:
        for line in f:
            for word in line.split():
                str = str.replace("{}".format(word), "")
    return str


def create_freq_list(str):
    word_list = str.split()
    freq_list = [0] * len(word_list)
    for i in range(len(word_list)):
        for j in range(len(word_list)):
            if (word_list[i] == word_list[j]):
                freq_list[i] = freq_list[i] + 1
    return freq_list, word_list


def most_freq_words_list(str):
    freq_list, word_list = create_freq_list(str)
    most_freq_list = [0] * len(freq_list)
    for i in range(len(freq_list)):
        if (freq_list[i] >= 2):
            most_freq_list.insert(i, word_list[i])
    most_freq_list = list(filter(lambda a: a != 0, most_freq_list))  # remove zeros from list
    if (len(most_freq_list) != 0):  ##set function shown in output if list is empty,this line hide it
        most_freq_list = set(most_freq_list)  # remove duplicates from list
    return most_freq_list


def get_similarity(course, course2):
    result = language_checking(course['lang'], course2['lang'])
    if (result):
        str = clean_text(course['desc'])
        str2 = clean_text(course2['desc'])
        result = jaccard_similarity(str, str2)
        return result
    else:
        #print(course["name"]+" != " + course2['name'])

        return 0

def language_checking(lang, lang2):
    """comparing two  course objects languages """
    lang = lang.lower()
    lang2 = lang2.lower()
    if (lang == lang2):
        return True
    else:
        return False


def find_equivalent_course(course_list, course_list2):
    """find equivalent courses and print them"""

    equivalent_courses = {}

    for course in course_list:
        eq_course = {}
        similarity = 0
        for course2 in course_list2:           
            if (course['name'] == course2['name']):
                similarity = 1
                eq_course = course2
                break
            temp = get_similarity(course, course2)
            if(temp > similarity):
                similarity = temp
                eq_course = course2
        if(similarity > 0.2):
            if course['desc'] != None and eq_course['desc'] != None:
                equivalent_courses[course['name']] = [eq_course['name'], similarity]

    return equivalent_courses
    

if __name__ == '__main__':
    #examples
    course = getCoursesBySchoolAndDept("deu", "Bilgisayar Mühendisliği")
    course2 = getCoursesBySchoolAndDept("marmara", "Bilgisayar Mühendisliği (İngilizce)")
    #get_similarity(course[5], course[5])
    find_equivalent_course(course,course2)
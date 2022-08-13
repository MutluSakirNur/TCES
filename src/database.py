import os.path
import logging

from tinydb import TinyDB, Query

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

db = TinyDB(current_path + '/ctes.db')

schools = db.table('schools')
courses = db.table('courses')
departments = db.table('departments')

School = Query()
Course = Query()
Department = Query()

class unicode_tr(str):
    CHARMAP = {
        "to_upper": {
            u"ı": u"I",
            u"i": u"İ",
        },
        "to_lower": {
            u"I": u"ı",
            u"İ": u"i",
        }
    }
    
    def lower(self):
        for key, value in self.CHARMAP.get("to_lower").items():
            self = self.replace(key, value)
        return self.lower()

    def upper(self):
        for key, value in self.CHARMAP.get("to_upper").items():
            self = self.replace(key, value)
        return self.upper()


def main():
    printAllUniversities()


def printAllUniversities():
    for school in schools:
        print(school['university_name'] + " - " + school['short_name'] 
              + " - " + school['link'])
        

def addUniversity(university_name, short_name, link):
    if not schools.contains(School.short_name == short_name):
        schools.insert({
            'university_name' : university_name,
            'short_name' : short_name,
            'link' : link
        })


def getUniversityLink(short_name):
    result = schools.get(School.short_name == short_name)
    if result:
        return result['link']
    return result


def addCourseContent(course):
    if not course.lang:
        course.lang = ""
    if not course.name:
        course.name = ""

    code = course.code
    name = unicode_tr(course.name).lower().strip()
    lang = unicode_tr(course.lang).lower()
    ects = course.ects
    desc = course.desc
    weekly_desc = course.weekly_desc
    school_short_name = course.school_short_name
    dept = course.dept

    courses.upsert({
            'code' : code,
            'name' : name,
            'lang' : lang,
            'ects' : ects,
            'desc' : desc,
            'weekly_desc' : weekly_desc,
            'school_short_name' : school_short_name,
            'dept' : dept
        }, (Course.code == code) & (Course.school_short_name == school_short_name)
            & (Course.dept == dept))


def getCoursesBySchoolAndDept(school_short_name, dept):
    result = courses.search((Course.school_short_name == school_short_name) 
                            & (Course.dept == dept))
    return result


def getSchoolNames():
    school_names = []
    for school in schools:
        school_names.append(school['university_name'])
    
    return school_names


def populateUniversities():
    universities = [
        ["Ege Üniversitesi", "ege", "https://ebys.ege.edu.tr/ogrenci/ebp/organizasyon.aspx?kultur=tr-tr&Mod=1"]
        ,["Dokuz Eylül Üniversitesi", "deu", "http://debis.deu.edu.tr/ders-katalog/2017-2018/tr/tr-c3.html"]
        ,["İzmir Ekonomi Üniversitesi", "izmir_ekon", "http://www.ieu.edu.tr/tr/#academic"]
        ,["Gazi Üniversitesi", "gazi", "http://gbp.gazi.edu.tr//?dr=0&lang=0&ac=4&baslik=1"]
        ,["Orta Doğu Teknik Üniversitesi", "odtu", "https://catalog.metu.edu.tr/"]
        ,["Yıldız Teknik Üniversitesi", "ytu", "http://www.bologna.yildiz.edu.tr/index.php?r=program/bachelor"]
        ,["Uludağ Üniversitesi", "uludag", "http://bilgipaketi.uludag.edu.tr/Programlar/Index/33"]
        ,["Hacettepe Üniversitesi", "hacettepe", "http://akts.hacettepe.edu.tr/programlar.php?program_duzey=2&submenuheader=1"]
        ,["Anadolu Üniversitesi", "anadolu", "http://abp.anadolu.edu.tr/tr/akademik/lisans"]
        ,["Kadir Has Üniversitesi", "khas", "http://bologna.khas.edu.tr/lisans"]
        ,["Marmara Üniversitesi", "marmara", "http://llp.marmara.edu.tr/organizasyon.aspx?kultur=tr-tr&Mod=1"]
        ,["İstanbul Üniversitesi", "istanbul", "http://ebs.istanbul.edu.tr/home/lisans"]
        ,["Ondokuz Mayıs Üniversitesi", "ondokuz", "http://ebs.omu.edu.tr/ebs/index.php?dil=tr&mod=1"]
    ]

    for school in universities:
        addUniversity(school[0], school[1], school[2])


def addDepartmentList(school_short_name, department_list):
    if department_list:
        for dept in department_list:
            if not departments.contains((Department.school_short_name == school_short_name)
                    & (Department.department_name == dept)):
                departments.insert({
                    'school_short_name' : school_short_name,
                    'department_name' : dept
                })


def getDepartmentsBySchool(school_name):
    school_short_name = getShortNameByName(school_name)
    result = departments.search(Department.school_short_name == school_short_name)
    department_list = []
    for dept in result:
        department_list.append(dept['department_name'])
    return department_list


def getShortNameByName(school_name):
    result = schools.get(School.university_name == school_name)
    if result:
        return result['short_name']
    return result
    
def getCourseContentByName(school_short_name, dept_name, course_name):
    course = courses.search((Course.school_short_name == school_short_name) 
                            & (Course.dept == dept_name) & (Course.name == course_name))
    if course:
        return course
    else:
        logging.info("No course found with  " + str(school_short_name) + " - " + str(dept_name) + " - " + str(course_name))
        return None

if __name__ == '__main__':
    main()
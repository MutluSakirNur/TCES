import os.path
import logging

from lxml import html
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import database

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

logging.basicConfig(format='%(module)s:%(levelname)s:%(message)s', filename=current_path + '/ctes.log', 
                    filemode='w', level=logging.INFO)

class Course():
    def __init__(self, code, name, lang, ects, desc, weekly_desc
                 , school_short_name, dept):
        self.code = code
        self.name = name
        self.lang = lang
        self.ects = ects
        self.desc = desc
        self.weekly_desc = weekly_desc
        self.school_short_name = school_short_name
        self.dept = dept


def main():
    # initializeDatabase()
    # downloadAllEgeContents()
    downloadAllMarmaraContents()
    downloadAllDeuContents()

    #database.printAllUniversities()
    #getOdtuCourseContents("Biology")
    #print(database.getDepartmentsBySchool("Marmara Üniversitesi"))
    #getAnadoluCourseContents("Mimarlık Bölümü", "Mühendislik Fakültesi")
    #getHacettepeCourseContents("Bilgisayar Mühendisliği Programı (İng.)")
    # getIzmirEkonomiCourseContents("Bilgisayar Mühendisliği")
    #getEgeCourseContents('Bilgisayar Mühendisliği')
    #getDeuCourseContents("Bilgisayar Mühendisliği")
    #getYildizCourseContents("Bilgisayar Mühendisliği Lisans Programı")
    #getKhasCourseContents("Psikoloji")
    #print(database.getCoursesBySchoolAndDept("khas", "Psikoloji"))
    #getMarmaraCourseContents("Fransızca Öğretmenliği")
    #print(getDepartmentPath('marmara', 'Kimya'))    
    #print(database.getCoursesBySchoolAndDept("deu", "Bilgisayar Mühendisliği"))
    #printCourseList("uludag", "Biyoloji")
    # printCourseList("istanbul", "BİLGİSAYAR MÜHENDİSLİĞİ, LİSANS PROGRAMI, (ÖRGÜN ÖĞRETİM)")
    # print(database.getCourseContentByName("ytu", "İktisat Lisans Programı", "mali tablolar analizi"))
    # print(database.getCourseContentByName("uludag", "İktisat", "iktisadi planlama"))
    # print(database.getCourseContentByName("istanbul", "İŞLETM, LİSANS PROGRAMI, (ÖRGÜN ÖĞRETİM)", "yaşam bilimlerinde disiplinler arası araştırma ve geliştirme"))
    #getUludagCourseContents("Biyoloji")
    # getIstanbulCourseContents("BİLGİSAYAR MÜHENDİSLİĞİ, LİSANS PROGRAMI, (ÖRGÜN ÖĞRETİM)")


def downloadAllEgeContents():
    ## Su ürünleri yetiştiriciliği sonrasını çekmeyebilir.
    department_list = getDepartmentsList('ege')
    for dept in department_list:
        if not dept.startswith('#'):
            getEgeCourseContents(dept)

def downloadAllMarmaraContents():
    department_list = getDepartmentsList('marmara')
    for dept in department_list:
        getMarmaraCourseContents(dept)

def downloadAllDeuContents():
    department_list = getDepartmentsList('deu')
    for dept in department_list:
        getDeuCourseContents(dept)

def getDepartmentPath(school_name, department_name):
    ''' Gets path for ege, deu, izmir_ekon, ytu, hacettepe, khas, marmara '''

    university_link = database.getUniversityLink(school_name)
    if university_link:
        page = requests.get(university_link)
        tree = html.fromstring(page.content)

        department_link = tree.xpath('//a[text()="{}"]/@href'.format(department_name))
        if department_link:
            if school_name == 'marmara' and len(department_link)>1:
                return department_link[1]

            return department_link[0]
        else:
            raise Exception('No department found with that name')
    else:
        raise Exception('No university found with that name')


def getDepartmentsList(school_name):

    search_keys = {
            'ege': '//*[@id="organizasyonTree"]/ul[@class="rtUL rtLines"]//a/text()',
            'deu' : '//*[@id="onlisans"]/li//a/text()',
            'izmir_ekon' : '//*[@id="Container"]/div[@class="mix category-2"]/div/div/div/ul/li/a/text()',
            'uludag' : '//div[@class="container"]/div[@class="panel panel-primary"]//tr[@class="mouseIconEl"]//td/text()',
            'ytu' : '//div[@id="content"]/ul//a/text()',
            'hacettepe' : '//div[@class="icerik"]//ul/li/a/text()',
            'khas' : '//div[@class="container"]//div[@class="col-md-12"]//ul[@class="list-icons"]/li//a/text()',
            'odtu' : '//*[@id="maincontent"]//table[@class="genel"]//tr//td[@class="tbright"]//a/text()',
            'anadolu' : '//aside[@class="col-md-9 content"]//ul[@class="list-group akademik-list"]//li[@class="bolum"]/a/text()',
            'marmara' : '//div[@id="ctl00_ContentPlaceHolder_organizasyonTree"]/ul[@class="rtUL rtLines"]//li[@class="rtLI"]//div[@class="rtMid" or @class="rtTop"]//a/text()',
            'ondokuz' : '//div[@id="icerik"]//ul//a/text()',
            'gazi' : '//div[@class="column1-unit"]//a/text()'}

    university_name = school_name
    university_link = database.getUniversityLink(university_name)

    if school_name == 'odtu':
        university_link = 'http://www.metu.edu.tr/undergraduate-programs-and-degrees'
    elif school_name == 'anadolu':
        university_link = 'http://abp.anadolu.edu.tr/tr/akademik/lisans'
    elif school_name == 'gazi':
        university_link = 'http://gbp.gazi.edu.tr//?dr=0&lang=0&ac=4&baslik=1'

    if university_link:
        page = requests.get(university_link)
        tree = html.fromstring(page.content)

        search_key = search_keys[university_name]
        department_list = tree.xpath(search_key)

        if (university_name == 'uludag' or university_name == 'anadolu' or university_name == 'deu'):
            new_dept_list = cleanWhiteSpaceFromList(department_list)
            department_list = new_dept_list
        if (university_name == 'gazi'):
            new_dept_list = removeFacultyFromList(department_list)
            department_list = new_dept_list
        ## This is for departments which has no dept_link in Marmara.
        ## Checking every department slows down initialization.

        # elif university_name == 'marmara':
        #     new_dept_list = []
        #     for dept in department_list:
        #         if getDepartmentPath("marmara", dept) != 'javascript:':
        #             new_dept_list.append(dept)
        #     department_list = new_dept_list

        database.addDepartmentList(university_name, department_list)
        return department_list
    else:
        raise Exception(university_name)


def getEgeCourseContents(department_name):
    university_name = 'ege'
    university_root_link = "https://ebys.ege.edu.tr/ogrenci/ebp/"
    department_path = getDepartmentPath(university_name, department_name)
    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)
        codes = tree.xpath('//div[@id="ltlMufredat"]//a/text()')
        links = tree.xpath('//div[@id="ltlMufredat"]//a/@href')

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))

        codes = tree.xpath('//div[@id="ltlSecmeliDersGruplari"]//td/a/text()')
        links = tree.xpath('//div[@id="ltlSecmeliDersGruplari"]//td/a/@href')
        department_courses.update(dict(zip(codes, links)))
        logging.info(str(university_name) + " / " + str(department_name) + " ders içeriği indiriliyor")
        for code, link in department_courses.items():
            ## If course is mandatory
            if link.startswith("course"):
                course_page = requests.get(university_root_link + link)
                course_tree = html.fromstring(course_page.content)

                course_content = course_tree.xpath('//td[text()="Dersin İçeriği"]')
                if course_content:
                    course_name = course_tree.xpath("//td[text()='{}']".format(code))[0].getnext().text
                    course_content = course_content[0].getparent().getnext().xpath('./td[@class="Value"]/text()')

                    course_akts = course_tree.xpath("//td[@class = 'AltSatir']/text()")
                    if course_akts:
                        course_akts = int(course_akts[5])
                    else:
                        course_akts = -1
                    course_language = course_tree.xpath('//*[contains(text(),"Dersin Sunulduğu Dil")]')
                    course_language = course_language[0].getparent().getnext().xpath("./td/text()")
                    if course_language:
                        course_language = course_language[0]
                    else:
                        course_language = ""

                    if course_content:
                        c = Course(code, course_name, course_language, course_akts, course_content[0],
                                   "", university_name, department_name)
                        database.addCourseContent(c)
        

def getDeuCourseContents(department_name):
    university_name = 'deu'
    university_root_link = "http://debis.deu.edu.tr/ders-katalog/2017-2018/tr/"
    department_path = getDepartmentPath(university_name, ' ' + department_name + ' ')
    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)
        codes = tree.xpath('//table/tbody/tr/td/a/text()')
        links = tree.xpath('//table/tbody/tr/td/a/@href')

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))
        logging.info(str(university_name) + " / " + str(department_name) + " ders içeriği indiriliyor")
        for code, link in department_courses.items():
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)
            course_content = course_tree.xpath('//h4[text()="Ders İçeriği"]')

            if course_content:

                course_akts = course_tree.xpath('//*[contains(text()," AKTS ")]')[0].getparent().getnext()
                course_akts = course_akts.xpath("./td/text()")
                if course_akts:
                    course_akts = int(course_akts[6])
                else:
                    course_akts = -1

                course_language = course_tree.xpath('//h4[text()="Dersin Öğretim Dili"]')[0].getparent().getparent()
                course_language = course_language.getnext().xpath("./td/p/text()")
                if course_language:
                    course_language = course_language[0]

                course_name = course_tree.xpath("//h1[text()='DERS ADI']")[0].getnext().text[2:]
                course_content = course_content[0].getparent().getparent().getnext().xpath('.//table//tr/td[2]/text()')

                temp_course_content = ''
                for i in course_content:
                    temp_course_content += ''.join(i)
                course_content = temp_course_content
                c = Course(code, course_name, course_language, course_akts, course_content,
                           "", university_name, department_name)
                database.addCourseContent(c)


def getIzmirEkonomiCourseContents(department_name):
    university_name = 'izmir_ekon'
    department_path = getDepartmentPath(university_name, department_name)
    if department_path:
        # This does not work for Faculty of Medicine since they did not publish curriculum
        department_curr_path = department_path + "/curr"
        page = requests.get(department_curr_path)
        tree = html.fromstring(page.content)
        codes = tree.xpath('//div[@class="col-xs-12 col-sm-12 col-md-9 col-lg-9"]//table//a/text()')
        codes = codes[:-1]
        links = tree.xpath('//div[@class="col-xs-12 col-sm-12 col-md-9 col-lg-9"]//table//a/@href')
        links = links[:-1]

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))

        for code, link in department_courses.items():
            # codes and links includes elective courses
            # but we don't want elective courses pointers.
            if not code.startswith("ELEC"):
                course_page = requests.get(department_path + "/" + link)
                course_tree = html.fromstring(course_page.content)
                course_content = course_tree.xpath('//*[text()="Dersin Amacı"]')
                if course_content:
                    course_akts = course_tree.xpath('//div[ @id = "ects_credit"] / text()')
                    course_language = course_tree.xpath('//div [@id = "course_lang" ] / text()')
                    course_name = course_tree.xpath("//div[@id='course_name']/text()")[0].strip()
                    course_content = course_content[0].getparent().getnext().text
                    # Write course content to text file with courses name
                    if course_content:
                        c = Course(code, course_name, course_language[0], course_akts[0], course_content,
                                   "", university_name, department_name)
                        database.addCourseContent(c)
 

## GAZI UNIVERSITY
def getGaziDepartmentPath(department_name):
    university_name = 'gazi'
    course_list_key = "Dersler - AKTS Kredileri"
    university_link = database.getUniversityLink(university_name)
    if university_link:
        page = requests.get(university_link)
        tree = html.fromstring(page.content)
        department_link = tree.xpath('//a[text()="{}"]/@href'.format(department_name))
        if department_link:
            page = requests.get(department_link[0])
            tree = html.fromstring(page.content)
            department_link = tree.xpath('//a[text()="{}"]/@href'.format(course_list_key))
            return department_link[0],university_name
        else:
            raise Exception('No department found with that name')

    else:
        raise Exception('No university found with that name')


def getGaziCourseContents(department_name):
    department_path,university_name = getGaziDepartmentPath(department_name)
    if department_path:
        page = requests.get(department_path)
        tree = html.fromstring(page.content)
        codes = tree.xpath('//div[@class="column1-unit"]//a/text()')
        links = tree.xpath('//div[@class="column1-unit"]//a/@href')
        links = links[:-1]

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))

        for code, link in department_courses.items():
            course_page = requests.get(link)
            course_tree = html.fromstring(course_page.content)
            ##getting course content
            course_content = course_tree.xpath('//*[contains(text(),"ÖĞRENME ÇIKTILARI")]')
            if (course_content):
                course_name = code
                course_content = course_content[0].getparent().getparent().getparent().getnext().xpath('.//text()')
                course_content = course_content[1:]
                temp_course_content = ''
                temp_course_content = ' '.join(course_content)
                course_content = temp_course_content
                ##getting course language
                course_language = course_tree.xpath('//*[contains(text(),"DERSİN DİLİ")]')
                if(course_language):
                    course_language = course_language[
                        0].getparent().getparent().getparent().getnext().xpath('.//text()')
                    course_language = course_language[1]
                    course_language = course_language.replace("{}".format(u"\xa0\xa0"), u"")

                else:
                    course_language = ""
                ##get course akts
                course_akts = course_tree.xpath('//*[contains(text(),"Ders AKTS")]')
                if(course_akts):
                    course_akts = int(course_akts[0].getparent().getnext().xpath('.//font/text()')[0])
                else:
                    course_akts = -1
                ##adding to database
                if course_content:
                    c = Course(code, course_name, course_language, course_akts, course_content,
                               "", university_name, department_name)
                    database.addCourseContent(c)


##MIDDLE EAST TECHNICAL UNIVERSITY
def getOdtuDepartmentPath(department_name):
    university_name = 'odtu'
    departments_with_faculties ={"Music and Fine Arts":"Departments Reporting to President's Office",
                                 "Turkish Language":"Departments Reporting to President's Office",
                                 "Architecture":"Faculty of Architecture",
                                 "City and Regional Planning":"Faculty of Architecture",
                                 "Industrial Design":"Faculty of Architecture",
                                 "Biology":"Faculty of Arts and Sciences",
                                 "Molecular Biology and Genetics": "Faculty of Arts and Sciences",
                                 "Chemistry":"Faculty of Arts and Sciences",
                                 "History":"Faculty of Arts and Sciences",
                                 "Mathematics":"Faculty of Arts and Sciences",
                                 "Philosophy":"Faculty of Arts and Sciences",
                                 "Physics":"Faculty of Arts and Sciences",
                                 "Psychology":"Faculty of Arts and Sciences",
                                 "Sociology":"Faculty of Arts and Sciences",
                                 "Statistics":"Faculty of Arts and Sciences",
                                 "Business Administration":"Faculty of Economic and Administrative Sciences",
                                 "Business Administration (METU-SUNY International Joint Program)":"Faculty of Economic and Administrative Sciences",
                                 "Economics":"Faculty of Economic and Administrative Sciences",
                                 "Global and International Affairs (METU-SUNY International Joint Program)":"Faculty of Economic and Administrative Sciences",
                                 "International Relations":"Faculty of Economic and Administrative Sciences",
                                 "Political Science and Public Administration":"Faculty of Economic and Administrative Sciences",
                                 "Chemistry Education":"Faculty of Education",
                                 "Physics Education":"Faculty of Education",
                                 "Early Childhood Education": "Faculty of Education",
                                 "Elementary Mathematics Education": "Faculty of Education",
                                 "Elementary Science Education": "Faculty of Education",
                                 "Elementary Education": "Faculty of Education",
                                 "English Language Teaching": "Faculty of Education",
                                 'English Language Teaching / "Liberal Studies" (METU-SUNY New Paltz)':"Faculty of Education",
                                 "Biology Education": "Faculty of Education",
                                 "Computer Education and Instructional Technology": "Faculty of Education",
                                 "Educational Sciences": "Faculty of Education",
                                 "Mathematics Education": "Faculty of Education",
                                 "Mathematics and Science Education": "Faculty of Education",
                                 "Physical Education and Sports": "Faculty of Education",
                                 "Aerospace Engineering":"Faculty of Engineering",
                                 "Chemical Engineering":"Faculty of Engineering",
                                 "Civil Engineering":"Faculty of Engineering",
                                 "Computer Engineering":"Faculty of Engineering",
                                 "Electrical and Electronics Engineering":"Faculty of Engineering",
                                 "Engineering Sciences":"Faculty of Engineering",
                                 "Environmental Engineering":"Faculty of Engineering",
                                 "Food Engineering":"Faculty of Engineering",
                                 "Geological Engineering":"Faculty of Engineering",
                                 "Industrial Engineering":"Faculty of Engineering",
                                 "Mechanical Engineering":"Faculty of Engineering",
                                 "Metallurgical and Materials Engineering":"Faculty of Engineering",
                                 "Mining Engineering":"Faculty of Engineering",
                                 "Petroleum and Natural Gas Engineering":"Faculty of Engineering",
                                 }
    faculty_name = departments_with_faculties[department_name]
    university_root_link = 'https://catalog.metu.edu.tr/'
    university_link = database.getUniversityLink(university_name)
    if university_link:
        page = requests.get(university_link)
        tree = html.fromstring(page.content)
        faculty_link = tree.xpath('//a[text()="{}"]/@href'.format(faculty_name))
        # Checking Faculty page
        if faculty_link:
            page = requests.get(university_root_link + faculty_link[0])
            tree = html.fromstring(page.content)
            department_link = tree.xpath('//a[text()="{}"]/@href'.format(department_name))
            # Checking department page
            if department_link:
                return university_root_link + department_link[0]
            else:
                raise Exception('No department found with that name')
        else:
            raise Exception('No faculty found with that name')

    else:
        raise Exception('No university found with that name')


def getOdtuCourseContents(department_name):
    university_name = "odtu"
    department_path = getOdtuDepartmentPath(department_name)
    if department_path:
        page = requests.get(department_path)
        tree = html.fromstring(page.content)
        codes = tree.xpath('//td[@class="short_course"]//a/text()')
        links = tree.xpath('//td[@class="short_course"]//a/@href')

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))

        for code, link in department_courses.items():
            university_link = database.getUniversityLink(university_name)
            course_page = requests.get(university_link + link)
            course_tree = html.fromstring(course_page.content)
            if course_page:
                course_content = course_tree.xpath('// *[ @ id = "content"] / div[2] / div / div / text()')
                course_language = course_tree.xpath('//*[contains(text(),"Language of Instruction")]')[0].getnext().text
                course_akts = course_tree.xpath('//*[contains(text(),"ECTS")]')[0].getnext().text
                course_name = course_tree.xpath('// *[ @ id = "content"] / div[2] / div / div / h2')[0].text
                course_name = course_name.split()
                course_name = " ".join(course_name[1:])

                if course_content:
                    c = Course(code, course_name, course_language, course_akts, course_content[4],
                               "", university_name, department_name)
                    database.addCourseContent(c)
                else:
                    print("course has no content!")


## ULUDAG UNIVERSITY
def getUludagDepartmentPath(department_name):
    university_name = "uludag"
    university_link = database.getUniversityLink(university_name)
    if university_link:
        page = requests.get(university_link)
        tree = html.fromstring(page.content)
        department_link = tree.xpath('//*[contains(text(), "{}")]'.format(department_name))
        if department_link:
            department_link = department_link[0].getparent().xpath('./@onclick')[0]
            department_link = department_link[15:-1]
            return department_link,university_name
        else:
            raise Exception('No department found with that name')
    else:
        raise Exception('No university found with that name')


def getUludagCourseContents(department_name):
    university_root_link = "http://bilgipaketi.uludag.edu.tr"
    department_path,university_name = getUludagDepartmentPath(department_name)

    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)

        links = tree.xpath('//div[@id="Dersler"]//tr/@onclick')
        elective_links = tree.xpath('//div[@class="aciklamaKutu"]/div[@id="divListe"]/div//tr/@onclick')
        links = links + elective_links

        for link in links:
            link = link[15:-1]
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)

            code = course_tree.xpath('//tr/td[text()="Dersin Kodu:"]')
            if code:
                code = code[0].getnext().text
                course_content = course_tree.xpath('//tr/td[text()="Dersin Amacı"]')
                course_akts = course_tree.xpath('//tr/td[text()="Dersin AKTS Kredisi:"]')
                if(course_akts):
                    course_akts = course_akts[0].getnext().text
                else:
                    course_akts = -1
                course_language = course_tree.xpath('//tr/td[text()="Dersin Dili:"]')
                if(course_language):
                    course_language = course_language[0].getnext().text
                else:
                    course_language = ""
                if course_content:
                    course_content = course_content[0].getnext().text
                    course_name = course_tree.xpath("//tr/td[text()='Dersin Adı:']")
                    if course_name:
                        course_name = course_name[0].getnext().text
                        if course_content is None:
                            course_content = " "
                        c = Course(code, course_name, course_language, course_akts, course_content,
                                   "", university_name, department_name)
                        database.addCourseContent(c)
    
## YILDIZ TECHNICAL UNIVERSITY
def getYildizCourseContents(department_name):
    university_name = 'ytu'
    department_path = getDepartmentPath(university_name, department_name)
    university_root_link = "http://www.bologna.yildiz.edu.tr/"
    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)

        codes = tree.xpath('//div[@id="semesters"]//a/text()')
        links = tree.xpath('//div[@id="semesters"]//a/@href')

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))

        for code, link in department_courses.items():
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)
            if course_page:
                course_content = course_tree.xpath('//*[text()="Dersin İçeriği"]')[0].getnext().text
                if course_content:
                    course_name = course_tree.xpath('// *[ @ id = "title"] / strong /text()')[0]
                    course_akts = course_tree.xpath('//*[@id="courseshortinfo"]/td[4]')
                    if(course_akts):
                        course_akts = course_akts[0].text
                    else:
                        course_akts = -1
                    course_language = course_tree.xpath('//*[contains(text(),"Dersin Dili")]/following-sibling::*')
                    if(course_language):
                        course_language = course_language[0].text
                    else:
                        course_language = ""
                    if course_content:
                        c = Course(code, course_name, course_language, course_akts, course_content,
                                   "", university_name, department_name)
                        database.addCourseContent(c)

## HACETTEPE UNIVERSITY
def getHacettepeCourseContents(department_name):
    university_name = 'hacettepe'
    department_path = getDepartmentPath(university_name, department_name)
    university_root_link = 'http://akts.hacettepe.edu.tr/'
    # path to which you download web drivers

    driver = webdriver.PhantomJS()

    driver.get(university_root_link + department_path)
    driver.find_element_by_xpath('//*[ @ id = "ust1"]/div[3]/ul/li[8]/a').click()
    codes_and_links = driver.find_elements_by_xpath('//a[@class="secmeli"]')
    codes = []
    for i in codes_and_links:
        codes.append(i.get_attribute("text"))
    allelements = len(codes)
    for i in range(allelements):
        driver.find_element_by_link_text(codes[i]).click()
        course_content = driver.find_elements_by_xpath('//*[contains(text(),"Dersin içeriği")]/following-sibling::td')[
            0].text
        try:

            course_akts = driver.find_element_by_xpath('//*[@id="sag"]/div/table[1]/tbody/tr[2]/td[7]')
            course_language = driver.find_element_by_xpath('//*[contains(text(),"Dersin Dili")]/following-sibling::td')
            course_name = driver.find_element_by_xpath('//*[@id="sag"]/div/table[1]/tbody/tr[2]/td[1]')
        except NoSuchElementException:
            pass

        if course_content:
            if codes[i]:
                c = Course(codes[i],course_name.text , course_language.text, course_akts.text, course_content,
                           "", university_name, department_name)
                database.addCourseContent(c)
        driver.back()

    driver.close()


## ANADOLU UNIVERSTY
def getAnadoluDepartmentPath(department_name):
    university_name = 'anadolu'
    university_root_link = "https://www.anadolu.edu.tr"
    university_link = database.getUniversityLink(university_name)
    if university_link:
            page = requests.get(university_link)
            tree = html.fromstring(page.content)
            department_link = tree.xpath('//a[text()=" {}"]/@href'.format(department_name))
            if department_link:
                department_link = department_link[0][:-4]
                dept_code = department_link.split('/')[-1]
                department_link = department_link.split('/')
                department_link[-2] = "dersler"
                department_link = '/'.join(department_link)
                return department_link,university_name
            else:
                raise Exception('No department found with that name')
    else:
        raise Exception('No university found with that name')


def getAnadoluCourseContents(department_name):
    logging.info("Getting anadolu university course content")
    department_path, university_name = getAnadoluDepartmentPath(department_name)
    if department_path:
        page = requests.get(department_path)
        tree = html.fromstring(page.content)
        names = tree.xpath('//aside/table//td/a/text()')
        links = tree.xpath('//aside/table//td/a/@href')
        codes = []
        for name in names:
            codes.append(name.getparent().getparent().getprevious().text)
        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))
        course_names_codes = dict(zip(codes, names))

        for code, link in department_courses.items():
            content_link = link.split('/')
            if content_link[-1] == '2':
                content_link = content_link[:-1]
            content_link[-1] = '49'
            content_link[-3] = 'ogrenimCikti'
            content_link = '/'.join(content_link)
            ##get course akts and language
            course_page = requests.get(link)
            course_tree = html.fromstring(course_page.content)
            course_akts = course_tree.xpath('//*[@id="main-content"]/aside/table[1]/tbody/tr/td[5]')
            if (course_akts):
                course_akts = course_akts[0].text
                course_akts = (course_akts.split("."))[0]
            else:
                course_akts = -1
            course_language = course_tree.xpath('//*[contains(text(),"Ders Dili")]')
            if (course_language):
                course_language = course_language[0].getnext().text
            else:
                course_language = ""
            ##getting ders content
            course_page = requests.get(content_link)
            course_tree = html.fromstring(course_page.content)

            if course_page:
                course_content = course_tree.xpath('//aside//ul[@class="list-group default-list"]//text()')
                course_content = cleanWhiteSpaceFromList(course_content)
                course_content = " ".join(course_content)
                course_name = course_names_codes[code]
                if course_name:
                    if course_content is None:
                        course_content = " "
                    c = Course(code, course_name, course_language, course_akts, course_content,
                               "", university_name, department_name)
                    # logging.info(code + " " + course_name + " " + course_language 
                    #             + " " + course_akts + " " + course_content + " "
                    #             + university_name + " " + department_name)
                    database.addCourseContent(c)

## KADIR HAS UNIVERSITY
def getKhasCourseContents(department_name):
    university_name = "khas"
    department_path = getDepartmentPath(university_name, department_name)
    university_root_link = "http://bologna.khas.edu.tr/"
    if department_path:
        page = requests.get(university_root_link + department_path + "/ders-plani-sap")
        tree = html.fromstring(page.content)

        codes = tree.xpath('//div[@class="col-md-12"]//table[@class="table table-bordered table-striped table-hover"]//a/text()')
        links = tree.xpath('//div[@class="col-md-12"]//table[@class="table table-bordered table-striped table-hover"]//a/@href')
        new_links = []
        new_codes = []
        for link in links:
            if(link != "javascript:void(0);"):
                code = link.getparent().text
                new_links.append(link)
                new_codes.append(code)

        assert (len(new_codes) == len(new_links))
        department_courses = dict(zip(new_codes, new_links))
        
        for code, link in department_courses.items():
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)
            if course_page:
                course_content = course_tree.xpath('//*[text()="Dersin Öğrenme Çıktıları (ÖÇ):"]')[0].getnext().xpath('.//text()')
                temp_course_content = ""
                for i in course_content:
                    temp_course_content = temp_course_content + i
                course_content = temp_course_content
                if course_content:
                    course_name = course_tree.xpath('// *[text()="Dersin Adı"]')[0].getparent().getnext().xpath('.//td[1]//text()')[0]
                    course_akts = course_tree.xpath('// *[text()="Dersin Adı"]')[0].getparent().getnext().xpath('.//td[7]//text()')[0]
                    course_akts = course_akts[0]
                    course_language = course_tree.xpath('//*[(text()="Öğrenim Dili:")]')[0].getnext().text
                    
                    c = Course(code,course_name,course_language,course_akts,course_content, "",university_name,department_name)
                    database.addCourseContent(c)

## MARMARA UNIVERSITY
def getMarmaraCourseContents(department_name):
    university_name = 'marmara'
    department_path = getDepartmentPath(university_name, department_name)
    university_root_link = 'http://llp.marmara.edu.tr/'
    
    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)

        codes = tree.xpath('//div[@id="ContentPlaceHolder_divZorunluDersListesi" or @id="ContentPlaceHolder_divSecmeliDersListesi"]//table[@class="ContentTable"]/tbody/tr/td[2]/a/text()')
        temp_codes = []
        ## Clean selective courses from codes list
        for code in codes:
            if '-' not in code and 'x' not in code:
                temp_codes.append(code)
        codes = temp_codes

        links = tree.xpath('//div[@id="ContentPlaceHolder_divZorunluDersListesi" or @id="ContentPlaceHolder_divSecmeliDersListesi"]//table[@class="ContentTable"]/tbody/tr/td[2]/a/@href')
        temp_links = []
        ## Clean selective courses from links list
        for link in links:
            if not link.startswith('#'):
                temp_links.append(link)
        links = temp_links
        
        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))
        logging.info(str(university_name) + " / " + str(department_name) + " ders içeriği indiriliyor")
        
        for code, link in department_courses.items():
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)
            if course_page:
                course_content = course_tree.xpath('//div[@id="ContentPlaceHolder_divDersIcerik"]//div[@class="contentdiv"]/text()')
                if course_content:
                    course_content = course_content[0].strip()
                    course_name = course_tree.xpath('//span[@id="ContentPlaceHolder_lblDersAdi"]/text()')[0]
                    course_akts = course_tree.xpath('//span[@id="ContentPlaceHolder_lblEcts"]/text()')[0]
                    course_language = course_tree.xpath('//div[@id="ContentPlaceHolder_divderDilIcerik"]//div[@class="contentdiv"]/text()')[0]                    
                    course_language = course_language.strip()
                    
                    c = Course(code,course_name,course_language,course_akts,course_content, "",university_name,department_name)
                    database.addCourseContent(c)                   

## ISTANBUL UNIVERSITY
def getIstanbulDepartmentPath(department_name,faculty_name):
    university_link = database.getUniversityLink("istanbul")
    driver = webdriver.PhantomJS()
    driver.get(university_link)
    try:
        driver.find_element_by_xpath('//*[text()="{}"]/span'.format(faculty_name)).click()
        driver.find_element_by_xpath('//*[text()="{}"]'.format(department_name)).click()
        department_link = driver.find_element_by_xpath('//*[text()="{}"]'.format(" Ders Programı")).get_attribute("href")
        return department_link
    except NoSuchElementException:
        print("Can not found department")

def getIstanbulCourseContents(department_name):
    university_name = "istanbul"
    try:
        faculty_name = findIstanbulFacultyName(department_name)
        if faculty_name is None:
            raise Exception("Faculty name is not found")
        department_path = getIstanbulDepartmentPath(department_name,faculty_name)
        university_root_link = "http://ebs.istanbul.edu.tr"
        if department_path:
            page = requests.get(department_path)
            tree = html.fromstring(page.content)
            codes = tree.xpath('//td[@class="hidden-sm hidden-xs"]/text()')
            links = tree.xpath('//div[@class="col-lg-9 col-md-9"] // a / @href')
            assert (len(codes) == len(links))
            department_courses = dict(zip(codes, links))

            for code, link in department_courses.items():
                course_page = requests.get(university_root_link + link)
                course_tree = html.fromstring(course_page.content)
                course_content = course_tree.xpath('//h4[text()="İçerik"]')[0].getparent().getnext()\
                    .xpath('.// p / text()')
                course_akts = course_tree.xpath('/html/body/div/div/div/div/div[2]/div/div[1]/div[2]/table/tbody/tr[2]/td[4] /text()')[0]
                course_language = course_tree.xpath('//*[contains(text(),"Ders Dili")]')[0].getparent().getnext().text
                course_name = course_tree.xpath('//*[contains(text(),"Ders Adı")]')[0].getparent().getnext().text
                if course_content:
                    c = Course(code, course_name, course_language, course_akts, course_content[0],
                            "", university_name, department_name)
                    database.addCourseContent(c)
        else:
            raise Exception("Department name does not exists.")
    
    except Exception as err:
        logging.critical(err)

def getIstanbulDepartmentsList():
    university_name = 'istanbul'
    university_link = database.getUniversityLink(university_name)

    driver = webdriver.PhantomJS()
    driver.get(university_link)

    faculty_names = driver.find_elements_by_xpath('//li[@class="list-group-item node-tree"]')
    temp_faculty_names = []
    for faculty_name in faculty_names:
        temp_faculty_names.append(faculty_name.text)
    faculty_names = temp_faculty_names

    for faculty_name in faculty_names:
        driver.find_element_by_xpath('//*[contains(text(),"{0}")]/span'.format(faculty_name)).click()
    
    departments = driver.find_elements_by_xpath('//li[@class="list-group-item node-tree"]')
    department_names = []
    for dept in departments:
        if dept.text not in faculty_names:
            department_names.append(dept.text)
    database.addDepartmentList(university_name, department_names)

    return department_names  

def findIstanbulFacultyName(department_name):
    university_name = 'istanbul'
    university_link = database.getUniversityLink(university_name)

    driver = webdriver.PhantomJS()
    driver.get(university_link)

    faculty_names = driver.find_elements_by_xpath('//li[@class="list-group-item node-tree"]')
    temp_faculty_names = []
    for faculty_name in faculty_names:
        temp_faculty_names.append(faculty_name.text)
    faculty_names = temp_faculty_names

    for faculty_name in faculty_names:
        driver.find_element_by_xpath('//*[contains(text(),"{0}")]/span'.format(faculty_name)).click()
        try:
            dept = driver.find_element_by_xpath('//*[contains(text(),"{0}")]'.format(department_name))
            if dept:
                # print(department_name + " is in " + faculty_name)
                return faculty_name
        except NoSuchElementException:
            pass
    
    return None


## SAMSUN ONDOKUZ MAYIS UNIVERSITY
def getOndokuzCourseContents(department_name):
    university_name = "ondokuz"
    department_path = getDepartmentPath(university_name, department_name)
    university_root_link = "http://ebs.omu.edu.tr/ebs/"

    if department_path:
        page = requests.get(university_root_link + department_path)
        tree = html.fromstring(page.content)

        codes = tree.xpath('//table[@class="mufredat"] // a / text()')
        links = tree.xpath('//table[@class="mufredat"] // a / @href')

        assert (len(codes) == len(links))
        department_courses = dict(zip(codes, links))
        
        for code, link in department_courses.items():
            course_page = requests.get(university_root_link + link)
            course_tree = html.fromstring(course_page.content)
            if course_page:
                course_content = course_tree.xpath('//*[text()="Dersin İçeriği"]')
                if course_content:
                    course_content = course_content[0].getnext().text
                if course_content:
                    course_name = course_tree.xpath('//*[@class = "AltSatir" ] / td / text()')[1]
                    course_akts = course_tree.xpath('//*[@class = "AltSatir" ] / td / text()')[5]
                    course_language = course_tree.xpath('//*[contains(text(),"Dersin Sunulduğu Dil")]')
                    course_language = course_language[0].getnext().xpath("./td/text()")
                    if course_language:
                        course_language = course_language[0]
                    else:
                        course_language = ""

                c = Course(code,course_name, course_language, course_akts,course_content, "",university_name,department_name)
                database.addCourseContent(c)

def printCourseList(school_short_name, department_name):
    courses = database.getCoursesBySchoolAndDept(school_short_name, department_name)
    logging.info("*** School: " + school_short_name + " Dept: " + department_name + " ***")
    for course in courses:
        print(course['name'] + " /// " + course['lang'])
        logging.info(course['name'] + " /// " + course['lang'])


def initializeDatabase():
    ''' Populates universities and departments list '''

    database.populateUniversities()

    school_list = ['ege', 'deu', 'izmir_ekon', 'uludag', 'ytu', 'hacettepe'
            , 'khas', 'odtu', 'anadolu', 'marmara', 'ondokuz', 'gazi']
    for school in school_list:
        getDepartmentsList(school)
    getIstanbulDepartmentsList()


def cleanWhiteSpaceFromList(elements):
    new_list = []
    for element in elements:
        new_element = element.strip()
        if new_element:
            new_list.append(new_element)
    
    return new_list

def removeFacultyFromList(elements):
    new_list = []
    for element in elements:
        if 'FAKÜLTESİ' not in element:
            new_list.append(element)
    
    return new_list    

if __name__ == '__main__':
    main()
    
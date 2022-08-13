import sys
import logging
import http.client as httplib
import textwrap
from subprocess import call

from PySide.QtCore import *
from PySide.QtGui import *

from ui_mainWindow import Ui_MainWindow
from ui_equ_courses_disp import Ui_equi_course_disp
import helpers
import database
import matcher

class Equi_Courses(QMainWindow,Ui_equi_course_disp):
   
    equivalent_courses = None
        
    def __init__(self,parent=None):
        super(Equi_Courses,self).__init__(parent)
        self.setupUi(self)
        #self.commandLinkButton.clicked.connect(self.otherwindow)
        self.commandLinkButton.clicked.connect(self.commandbutton_clicked)
        self.close_button.clicked.connect(self.closebutton_clicked)
    def closebutton_clicked(self):
        ret = app.exec_()
        sys.exit(ret)
    def commandbutton_clicked(self):
        #self.hide()
        self.close()
        #self.exit()
        call("/usr/bin/python3" + " /home/mutlu/Lessons/TEZ/repo/tces/src/core.py", shell=True)
        
        
    def otherwindow(self):
        self.ui = MainWindow()
        self.ui.show()
        
        
    def show_lessons(self):
        if not self.content_button.isVisible():
            self.content_button.show()
        if self.back_button.isVisible():
            self.back_button.hide()

        if Equi_Courses.equivalent_courses:
            self.textBrowser.clear()
            self.textBrowser_2.clear()
            logging.info(Equi_Courses.equivalent_courses)
            for key, values in Equi_Courses.equivalent_courses.items():
                course1 = key
                course2 = values[0]
                similarity = values[1]

                self.textBrowser.addItem(course1)
                self.textBrowser_2.addItem(course2)
                ## TODO: Print similarity in different way
                # self.textBrowser_2.addItem(course2 + " {0:.2f}".format(similarity))
            self.content_button.clicked.connect(self.getCourseContentFromDB)
        else:
            self.textBrowser.addItem("Denk olan ders bulunmamaktadır.")
            self.textBrowser_2.addItem("Denk olan ders bulunmamaktadır.")

    def getCourseContentFromDB(self):
        self.content_button.hide()
        self.back_button.show()
        self.back_button.clicked.connect(self.show_lessons)
        current_row = self.textBrowser.currentRow()
        course1_name = self.textBrowser.item(current_row).text()
        course2_name = self.textBrowser_2.item(current_row).text()
        logging.info(course1_name)
        logging.info(course2_name)
        
        self.textBrowser.clear()
        self.textBrowser_2.clear()

        school1_short_name = database.getShortNameByName(self.school1_label.text())
        school2_short_name = database.getShortNameByName(self.school2_label.text())        
        
        course1 = database.getCourseContentByName(school1_short_name, self.dept1_label.text(), course1_name)
        course2 = database.getCourseContentByName(school2_short_name, self.dept2_label.text(), course2_name)
        
        if course1:
            course1 = course1[0]
            # logging.info(course1)
            course1_content = course1['desc']
            course1_lang = course1['lang']
            course1_ects = course1['ects']

            course1_content = '\n'.join(textwrap.wrap(course1_content, 80))
        else:
            logging.error("Cant find course by course name: " + course1_name)
        
        if course2:
            course2 = course2[0]
            # logging.info(course2)
            course2_content = course2['desc']
            course2_lang = course2['lang']
            course2_ects = course2['ects']

            course2_content = '\n'.join(textwrap.wrap(course2_content, 80))
        else:
            logging.error("Cant find course by course name: " + course2_name)
        
        course1_info = "Dersin adı: " + course1_name + "\nDersin dili: " + course1_lang +\
            "\nAKTS kredisi: " + str(course1_ects)
        self.textBrowser.addItem(course1_info)
        self.textBrowser.addItem("Dersin içeriği: " + course1_content)

        course2_info = "Dersin adı: " + course2_name + "\nDersin dili: " + course2_lang +\
            "\nAKTS kredisi: " + str(course2_ects)
        self.textBrowser_2.addItem(course2_info)
        self.textBrowser_2.addItem("Dersin içeriği: " + course2_content)
        

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow,self).__init__()
        self.school1_name = None
        self.school2_name = None
        self.dept1_name = None
        self.dept2_name = None

        self.setupUi(self)
        self.assignWidgets()
        self.show()        

        self.worker = None
        self.compare_button.clicked.connect(self.compareButton_clicked)
        self.dialog = Equi_Courses(self)

    def compareButton_clicked(self):

        school_course = {'Ege Üniversitesi' : 'getEgeCourseContents', 'Dokuz Eylül Üniversitesi' : 'getDeuCourseContents',
                         'İzmir Ekonomi Üniversitesi' : 'getIzmirEkonomiCourseContents', 'Orta Doğu Teknik Üniversitesi' : 'getOdtuCourseContents',
                         'Uludağ Üniversitesi' : 'getUludagCourseContents', 'Yıldız Teknik Üniversitesi' : 'getYildizCourseContents',
                         'Hacettepe Üniversitesi' : 'getHacettepeCourseContents', 'Anadolu Üniversitesi' : 'getAnadoluCourseContents',
                         'Kadir Has Üniversitesi' : 'getKhasCourseContents', 'Marmara Üniversitesi' : 'getMarmaraCourseContents',
                         'Ondokuz Mayıs Üniversitesi' : 'getOndokuzCourseContents', 'İstanbul Üniversitesi' : 'getIstanbulCourseContents',
                         'Gazi Üniversitesi' : 'getGaziCourseContents'}

        self.school1_name = self.school1_list.currentText()
        self.school2_name = self.school2_list.currentText()

        self.dept1_name = self.dept1_list.currentText()
        self.dept2_name = self.dept2_list.currentText()

        if self.school1_name == "Seçiniz" or self.school2_name == "Seçiniz":
            self.progress_label.setText("Okul Seçin")
        elif self.dept1_name == "Seçiniz" or self.dept2_name == "Seçiniz":
            self.progress_label.setText("Bölüm Seçin")
        else:
            school1_short_name = database.getShortNameByName(self.school1_name)
            school2_short_name = database.getShortNameByName(self.school2_name)

            course_list1 = database.getCoursesBySchoolAndDept(school1_short_name, self.dept1_name)
            course_list2 = database.getCoursesBySchoolAndDept(school2_short_name, self.dept2_name)

            self.worker = Worker(self.school1_name, self.school2_name, self.dept1_name, self.dept2_name)
            self.worker.progress.connect(self.getData, Qt.QueuedConnection)
            self.worker.finished.connect(self.openEquiCoursesWindow)
            self.worker.start()

    def getData(self, data):
        logging.info(data)        
        self.data = self.progress_label.text() + '\n' + data
        self.progress_label.setText(self.data)
        

    def assignWidgets(self):

        school_names = database.getSchoolNames()
        school_names = ["Seçiniz"] + school_names
        self.school1_list.addItems(school_names)
        self.school1_list.currentIndexChanged.connect(self.school1Changed)

        self.school2_list.addItems(school_names)
        self.school2_list.currentIndexChanged.connect(self.school2Changed)

    def school1Changed(self, index):
        self.dept1_list.clear()
        school_name = self.school1_list.itemText(index)
        logging.info("Currently selected on school1_list: {}".format(school_name))

        dept_list = database.getDepartmentsBySchool(school_name)
        if dept_list:
            dept_list = ["Seçiniz"] + dept_list
            self.dept1_list.addItems(dept_list)
        else:
            logging.info("There is no department found in selected university")
        
    def school2Changed(self, index):
        self.dept2_list.clear()
        school_name = self.school2_list.itemText(index)
        logging.info("Currently selected on school2_list: {}".format(school_name))

        dept_list = database.getDepartmentsBySchool(school_name)
        if dept_list:
            dept_list = ["Seçiniz"] + dept_list
            self.dept2_list.addItems(dept_list)
        else:
            logging.info("There is no department found in selected university")

    def openEquiCoursesWindow(self):
        self.dialog.school1_label.setText(self.school1_name)
        self.dialog.school2_label.setText(self.school2_name)
        self.dialog.dept1_label.setText(self.dept1_name)
        self.dialog.dept2_label.setText(self.dept2_name)
        
        self.close()
        self.dialog.show()
        self.dialog.show_lessons()
    

class Worker(QThread):

    progress = Signal(str)

    def __init__(self, school1_name, school2_name, dept1_name, dept2_name, parent=None):
        QThread.__init__(self, parent)
        self.school1_name = school1_name
        self.school2_name = school2_name
        self.dept1_name = dept1_name
        self.dept2_name = dept2_name

    def run(self):
        school_course = {'Ege Üniversitesi' : 'getEgeCourseContents', 'Dokuz Eylül Üniversitesi' : 'getDeuCourseContents',
                        'İzmir Ekonomi Üniversitesi' : 'getIzmirEkonomiCourseContents', 'Orta Doğu Teknik Üniversitesi' : 'getOdtuCourseContents',
                        'Uludağ Üniversitesi' : 'getUludagCourseContents', 'Yıldız Teknik Üniversitesi' : 'getYildizCourseContents',
                        'Hacettepe Üniversitesi' : 'getHacettepeCourseContents', 'Anadolu Üniversitesi' : 'getAnadoluCourseContents',
                        'Kadir Has Üniversitesi' : 'getKhasCourseContents', 'Marmara Üniversitesi' : 'getMarmaraCourseContents',
                        'Ondokuz Mayıs Üniversitesi' : 'getOndokuzCourseContents', 'İstanbul Üniversitesi' : 'getIstanbulCourseContents',
                        'Gazi Üniversitesi' : 'getGaziCourseContents'}
        school1_short_name = database.getShortNameByName(self.school1_name)
        school2_short_name = database.getShortNameByName(self.school2_name)

        course_list1 = database.getCoursesBySchoolAndDept(school1_short_name, self.dept1_name)
        course_list2 = database.getCoursesBySchoolAndDept(school2_short_name, self.dept2_name)
        try:
            ## Get first  school/course content
            if not course_list1:
                internet_connection = checkNetworkConnection()
                if not internet_connection:
                    raise ConnectionAbortedError("İnternet bağlantısı olmadığı için ders içerikleri alınamadı.")
                method_to_call = getattr(helpers, school_course[self.school1_name])
                print(str(method_to_call) + "is calling for " + self.dept1_name)
                self.progress.emit("-> " + self.school1_name + " ders içerikleri çekiliyor.")             
                method_to_call(self.dept1_name)
                course_list1 = database.getCoursesBySchoolAndDept(school1_short_name, self.dept1_name)
            else:
                self.progress.emit("-> " + self.school1_name + " / " +  self.dept1_name + " ders içerikleri mevcut.  \u2713")
            ## Get seconds school/course content    
            if not course_list2:
                internet_connection = checkNetworkConnection()
                if not internet_connection:
                    raise ConnectionAbortedError("İnternet bağlantısı olmadığı için ders içerikleri alınamadı.")
                method_to_call = getattr(helpers, school_course[self.school2_name])
                self.progress.emit("-> " + self.school2_name + " ders içerikleri çekiliyor.")                              
                print(str(method_to_call) + "is calling for " + self.dept2_name)            
                method_to_call(self.dept2_name)
                course_list2 = database.getCoursesBySchoolAndDept(school2_short_name, self.dept2_name)
            else:
                self.progress.emit("-> " + self.school2_name + " / " +  self.dept2_name + " ders içerikleri mevcut.  \u2713")
        except ConnectionAbortedError as e:
            self.progress_label.setText("İnternet bağlantısı yok.")

        if course_list1 and course_list2:
            logging.info(school1_short_name + " " + self.dept1_name + " ve " + school2_short_name + " " + self.dept2_name + " karşılaştırması yapılıyor")
            self.progress.emit("-> İndirme işlemi tamamlandı.  \u2713")
            equivalent_courses = matcher.find_equivalent_course(course_list1, course_list2)
            Equi_Courses.equivalent_courses = equivalent_courses
        else:
            self.progress_label.setText("Ders içeriği eksik, lütfen başka okul/bölüm ile deneyin.")


def checkNetworkConnection():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
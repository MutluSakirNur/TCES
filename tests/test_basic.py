import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import core
from src import helpers

# This test runs slow, no need to run it everytime
# def test_ege_get_department_path():
#     department_path = helpers.getEgeDepartmentPath("Felsefe")
#     assert "organizasyon.aspx?kultur=tr-tr&Mod=1&ustbirim=7&birim=6",\
#             "&altbirim=-1&program=2700&organizasyonId=105&mufredatTurId=932001"\
#             == department_path

def test_deu_get_department_path():
    department_path = helpers.getDeuDepartmentPath("İstatistik")
    assert "bolum_1135_tr.html" == department_path

def test_izmir_ekonomi_get_department_path():
    department_path = helpers.getIzmirEkonomiDepartmentPath("Mimarlık")
    assert "http://mmr.fadf.ieu.edu.tr/tr" == department_path

def test_gazi_get_department_path():
    department_path = helpers.getGaziDepartmentPath("GASTRONOMİ VE MUTFAK SANATLARI  *")
    assert "http://gbp.gazi.edu.tr//htmlProgramHakkinda.php?dr=0&lang=0"+\
            "&baslik=1&FK=19&BK=02&ders_kodu=&sirali=0&fakulte=TUR%DDZM+FAK%DCLTES"+\
            "%DD&fakulte_en=FACULTY+OF+TOURISM&bolum=GASTRONOM%DD+VE+MUTFAK+SANATLARI"+\
            "&bolum_en=GASTRONOMY+AND+CULINARY+ART&ac=11" == department_path

def test_odtu_get_department_path():
    department_path = helpers.getOdtuDepartmentPath("Architecture",
                                                    "Faculty of Architecture")
    assert "https://catalog.metu.edu.tr/program.php?fac_prog=120" == department_path

def test_uludag_get_department_path():
    department_path = helpers.getUludagDepartmentPath("Bitki Koruma")
    assert "/Programlar/Detay/1041?AyID=24" == department_path

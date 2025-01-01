from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from urllib.parse import urljoin

headers = {}

BASE_URL = "https://www.esylabus.ue.poznan.pl/pl"
MAIN_URLS = ["https://www.esylabus.ue.poznan.pl/pl/12/1/1/105", "https://www.esylabus.ue.poznan.pl/pl/12/2/1/105"]

#Wszystkie linki trybów studiów
hrefs_list = []
for MAIN_URL in MAIN_URLS:
    response = requests.get(MAIN_URL)
    main_website = BeautifulSoup(response.text, "html.parser")

    relevant_elements = main_website.find_all("a", href = re.compile(r"^/pl/12/\d/\d/105$"))
    hrefs = [link["href"] for link in relevant_elements]
    hrefs_list.extend(hrefs)

hrefs_list = pd.unique(hrefs_list)

links_list = [urljoin(BASE_URL, href) for href in hrefs_list]
links_list

#Wszystkie linki do sylabusów
all_sylabus_links = []

for link in links_list:
    response = requests.get(link)
    main_website = BeautifulSoup(response.text, "html.parser")
    
    relevant_elements = main_website.find_all("a", href = re.compile(r"/pl/12/\d/\d/105/\d{1,3}"))
    hrefs = [link["href"] for link in relevant_elements]
    all_sylabus_links.extend(hrefs)

all_sylabus_links = [urljoin(BASE_URL, href) for href in all_sylabus_links]

df_sylabus_list = []
for link in all_sylabus_links:

    response = requests.get(link)
    main_website = BeautifulSoup(response.text, "html.parser")

    course_title_element = main_website.find("h1", class_="section-title")
    course_title = course_title_element.get_text().replace("\n", "").replace("Kierunek", "").strip()

    nav_tabs = main_website.find_all("li", class_="nav-item")
    semestr_tabs = [tab for tab in nav_tabs if "Semestr" in tab.get_text()]

    for semestr_tab in semestr_tabs:
        tab_id = semestr_tab.find("button")["id"]
        semestr_text = semestr_tab.get_text().replace("\n", "").strip()
        tab_link = urljoin(link, f"#{tab_id}")
        response = requests.get(tab_link)
        website = BeautifulSoup(response.text, "html.parser")
        table = website.find("div", class_= "tab-content mt-3")
        df = pd.read_html(str(table))[0]
        df["Semestr"] = semestr_text
        df["Nazwa kierunku"] = course_title
        df_sylabus_list.append(df)

table = pd.concat(df_sylabus_list)

table.to_excel("raw_data/sylabus_programs.xlsx")

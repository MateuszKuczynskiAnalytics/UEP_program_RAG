from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils import random_sleep
from urllib.parse import urljoin
import re

BASE_URL = "https://www.esylabus.ue.poznan.pl/pl"
MAIN_URLS = ["https://www.esylabus.ue.poznan.pl/pl/12/1/1/105", "https://www.esylabus.ue.poznan.pl/pl/12/2/1/105"]

service = FirefoxService(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
actions = ActionChains(driver)

driver.get(MAIN_URLS[0])
print("Navigated to MAIN_URL:", driver.current_url)
random_sleep()

all_href_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

education_lvl_hrefs = [
    href_element.get_attribute("href") for href_element in all_href_elements
    if href_element.get_attribute("href") and re.match(r"^https://www\.esylabus\.ue\.poznan\.pl/pl/12/\d+/\d+/105$", href_element.get_attribute("href"))
]
education_lvl_hrefs.append("https://www.esylabus.ue.poznan.pl/pl/12/1/1/105")

#for url in education_lvl_hrefs:
driver.get(education_lvl_hrefs[0])

print("Navigated to education level url:", driver.current_url)
random_sleep()

all_href_elements_edu_lvl = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

program_hrefs = [
    href_element.get_attribute("href") for href_element in all_href_elements_edu_lvl
    if href_element.get_attribute("href") and re.match(r"https://www\.esylabus\.ue\.poznan\.pl/pl/12/\d/\d/105/\d{1,3}", href_element.get_attribute("href"))
]

#for program_url in pogram_hrefs:

driver.get(program_hrefs[0])

print("Navigated to program url:", driver.current_url)
random_sleep()

program_title_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='syl-major-name']")))
program_title = program_title_element.text.replace("\n", " ").replace("Kierunek ", "").strip()

program_subtitle_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='main-content']/div[1]")))
separated_text = program_subtitle_element.text.split(", ")
if separated_text:
    program_start_year = separated_text[0] if len(separated_text) > 0 else None
    program_education_level = separated_text[1] if len(separated_text) > 1 else None
    program_study_mode = separated_text[2] if len(separated_text) > 2 else None

program_description_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='nav-tab-info-panel']")))
program_description = program_description_element.text.replace("\n", " ").replace("  ", " ").replace("Zobacz pełny opis kierunku","").strip()

program_download_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Zobacz pełny opis kierunku')]")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", program_download_element)
program_download_element.click()

download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='downloadButton']")))

//*[@id="downloadButton"]

all_href_elements_edu_lvl = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))


program_hrefs = [
    href_element.get_attribute("href") for href_element in all_href_elements_edu_lvl
    if href_element.get_attribute("href") and re.match(r"https://www\.esylabus\.ue\.poznan\.pl/pl/12/\d/\d/105/\d{1,3}", href_element.get_attribute("href"))
]



hrefs_list = []
for MAIN_URL in MAIN_URLS:
    response = requests.get(MAIN_URL)
    main_website = BeautifulSoup(response.text, "html.parser")

    relevant_elements = main_website.find_all("a", href = re.compile(r"^/pl/12/\d/\d/105$"))
    hrefs = [link["href"] for link in relevant_elements]
    hrefs_list.extend(hrefs)




#driver.quit()


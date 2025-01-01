import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import pandas as pd
from scrapers.utils import random_sleep, logger, setup_logging, fetch_url
import os
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",  # Do Not Track request
    "Upgrade-Insecure-Requests": "1",
    "Accept": "application/pdf, text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}

setup_logging("logs/program_scraping_logs.log")
from scrapers.utils import logger

BASE_URL = "https://www.esylabus.ue.poznan.pl/pl"
MAIN_URLS = ["https://www.esylabus.ue.poznan.pl/pl/12/1/1/105", "https://www.esylabus.ue.poznan.pl/pl/12/2/1/105"]

#Wszystkie linki trybów studiów
edu_lvl_hrefs_list = []
for MAIN_URL in MAIN_URLS:
    response = fetch_url(MAIN_URL, headers, 2, 4, "MAIN_URL")
    study_mode_website = BeautifulSoup(response.text, "html.parser")
    logger.info(f"Scraped MAIN_URL: {MAIN_URL}")

    education_level_hrefs = study_mode_website.find_all("a", href = re.compile(r"^/pl/12/\d/\d/105$"))
    hrefs = [link["href"] for link in education_level_hrefs]
    edu_lvl_hrefs_list.extend(hrefs)

edu_lvl_hrefs_list = pd.unique(edu_lvl_hrefs_list)

edu_lvl_urls_list = [urljoin(BASE_URL, href) for href in edu_lvl_hrefs_list]

program_urls = []

for edu_lvl_url in edu_lvl_urls_list:
    response = fetch_url(edu_lvl_url, headers, 2, 4, "education_level")
    if not response:
        logger.warning(f"Skipping education level due to failed response: {edu_lvl_url}")
        continue
    
    edu_lvl_website = BeautifulSoup(response.text, "html.parser")
    program_href_elements = edu_lvl_website.find_all("a", href = re.compile(r"/pl/12/\d/\d/105/\d{1,3}"))
    program_hrefs = [link["href"] for link in program_href_elements]
    program_urls.extend(program_hrefs)

    program_urls = [urljoin(BASE_URL, href) for href in program_urls]
    #Exclude doctoral studies and Erasmus due to the lack of PDF program
    program_urls = [url for url in program_urls if url not in ["https://www.esylabus.ue.poznan.pl/pl/12/1/7/105/152", "https://www.esylabus.ue.poznan.pl/pl/12/1/6/105/23"]]

    for program_url in program_urls:

        response = fetch_url(program_url, headers, 2, 4, "program")
        if not response:
            logger.warning(f"Skipping program due to failed response: {program_url}")
            continue

        program_website = BeautifulSoup(response.text, "html.parser")

        program_title_element = program_website.find("h1", class_="section-title")
        if program_title_element:
            program_title = program_title_element.get_text().replace("\n", "").replace("Kierunek", "").strip()
        else:
            program_title = None

        if not program_title:
            logger.warning(f"Skipping program due to missing title: {program_url}")
            continue

        program_subtitle_element = program_website.select_one("#main-content > div:nth-of-type(1)")
        if program_subtitle_element:
            separated_text = program_subtitle_element.get_text().split(", ")
            separated_text = [text.replace("\n", "").strip() for text in separated_text]
            program_start_year = separated_text[0] if len(separated_text) > 0 else None
            program_education_level = separated_text[1] if len(separated_text) > 1 else None
            program_study_mode = separated_text[2] if len(separated_text) > 2 else None
        else:
            program_start_year = program_education_level = program_study_mode = None

        # Extract program description
        program_description_element = program_website.select_one("#nav-tab-info-panel")
        program_description = program_description_element.get_text().replace("\n", " ").replace("  ", " ").replace("Zobacz pełny opis kierunku", "").strip() if program_description_element else None

        # Extract program download link
        program_download_element = program_website.find("a", string="Zobacz pełny opis kierunku")
        program_download_url = urljoin(BASE_URL, program_download_element["href"] if program_download_element else None)

        api_headers = headers.copy()
        api_headers["Referer"] = program_urls[0]

        program_pdf_response = fetch_url(program_download_url, api_headers, 2, 4, "PDF program")
        
        raw_data_dir = "raw_data"

        # Program-specific directory
        program_dir = os.path.join(
            raw_data_dir,
            program_study_mode.replace(" ", "_"),
            program_education_level.replace(" ", "_"),
            program_title.replace(" ", "_")
        )
        os.makedirs(program_dir, exist_ok=True)

        # Save PDF
        pdf_path = os.path.join(
            program_dir,
            f"{program_study_mode.replace(' ', '_')}_{program_education_level.replace(' ', '_')}_{program_title.replace(' ', '_')}.pdf"
        )

        if program_pdf_response:
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(program_pdf_response.content)
        else:
            logger.warning(f"PDF not downloaded for: {program_title}")

        # Save Metadata
        metadata = {
            "title": program_title,
            "start_year": program_start_year,
            "education_level": program_education_level,
            "study_mode": program_study_mode,
            "description": program_description,
            "program_url": program_url
        }

        metadata_path = os.path.join(program_dir, f"{program_study_mode.replace(' ', '_')}_{program_education_level.replace(' ', '_')}_{program_title.replace(' ', '_')}.json")
        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, ensure_ascii=False, indent=4)

        logger.info(f"Saved PDF and metadata for: {program_title}, {program_education_level}, {program_study_mode}")

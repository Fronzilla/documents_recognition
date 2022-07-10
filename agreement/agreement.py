import os
import pathlib
import re
from pathlib import Path

import PyPDF2
import pandas as pd
from tqdm.auto import tqdm

AGREEMENT_PATH = '/Users/a1234/Desktop/archives/agreement'


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def collect_agreement_data(path_to_file: str):
    """

    :param path_to_file:
    :return:
    """

    pdf_file_obj = open(path_to_file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj, strict=False)

    num_pages = range(pdf_reader.numPages)

    first_page_data = pdf_reader.getPage(0).extractText()

    last_page = pdf_reader.getPage(num_pages[-1])
    last_page_data = last_page.extractText()

    # extract_data from first page

    name = extract_name(first_page_data)
    name = [n for n in name.split(" ") if n]
    last, first, middle = (name[0], name[1], " ".join(name[2:])) if name else (None, None, None)

    series, number = extract_passport(first_page_data)
    date = extract_date(last_page_data)

    return {
        "file": Path(path_to_file).name,
        "LastName": last,
        "FirstName": first,
        "MiddleName": middle,
        "PassportSeries": series,
        "PassportNumber": number,
        "SigningDate": date
    }


def extract_passport(s):
    """
    Extract passport by mask
    :param s:
    :return:
    """
    match = re.search(r"паспорт (\d{4})\s*-?\s*(\d{6})", s)
    if match:
        res = match.groups()
        return res[0].strip(), res[1].strip()

    return None, None


def extract_date(s):
    match = re.search(
        r"Дата подписания: \s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$", s
    )

    if match:
        return ".".join(match.groups())


def extract_name(s):
    patterns = [
        r"(?<=Я)(.*)(?= \(паспорт)",
        r'(?<=Я,)(.*)(?= даю свое согласие)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().replace(',', '').strip()

    return ""


collected_documents = collect_documents(AGREEMENT_PATH)

result = []

for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
    data = collect_agreement_data(doc)
    result.append(data)

df = pd.DataFrame(result)
df.to_csv('agreement.csv', index=False)

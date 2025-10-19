#!/usr/bin/env python3
import requests as r
from bs4 import BeautifulSoup as bs
from random import randint
from time import sleep
import csv
import sys


def saveCSV(data, output_file):
    data_list = [item for sublist in data for item in sublist]

    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["number", "name", "country", "comment", "date"])
        writer.writeheader()
        writer.writerows(data_list)

def get(url):
    sleep(randint(10,500)/1000)
    page = r.get(url)
    return page

def soup(page):
    return bs(page.content, 'html.parser')

def show_help():
    print("""
Usage:
    main.py [OPTIONS] [ARGS]

Options:
    main.py URL


Optional:
    --o [specifies the output file]
""")

def parseRow(row):
    cells = row.find_all("td")

    if len(cells) < 2:
        return None

    if not row.has_attr('id'):
        number = cells[0].get_text(strip=True)
        name = cells[1].get_text(strip=True)

        return {
            "number": number,
            "name": name,
            "country": "NaN",
            "comment": "NaN",
            "date": "NaN"
        }

    number = cells[0].get_text(strip=True)
    name = cells[1].get_text(strip=True)

    country_img = cells[2].find("img")
    country = country_img['title'] if country_img and country_img.has_attr('title') else "NaN"

    comment = cells[3].get_text(strip=True) if len(cells) > 3 else "NaN"
    date = cells[4].get_text(strip=True) if len(cells) > 4 else "NaN"

    return {
        "number": number,
        "name": name,
        "country": country,
        "comment": comment,
        "date": date
    }

def parseTable(table):
    data = []
    rows = table.find_all("tr")
    for row in rows:
        parsed = parseRow(row)
        if parsed: 
            data.append(parsed)
    return data

def getData(link):
    data = []
    link = link.split("&")[0]
    lastPage, firstPage = getLastPage(link)
    table = firstPage.find("table", id="signatures")
    data.append(parseTable(table))

    for i in range(2, int(lastPage) + 1):
        url = f"{link}&page_number={i}&num_rows=500"
        print(url)
        page = soup(get(url))
        pageTable = page.find("table", id="signatures")
        data.append(parseTable(pageTable))

    return data


def getLastPage(link):
    link = f"{link}&page_number=0&num_rows=500"
    firstPage = soup(get(link))
    pageItems = [
    li for li in firstPage.select('ul.pagination li')
    if li.a and li.a.get_text(strip=True).isdigit()]
    
    sortedItems = sorted(pageItems, key=lambda li: int(li.a.get_text(strip=True)))
    lastPage = sortedItems[-1].text

    return lastPage, firstPage

def main():
    
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    if "--o" in sys.argv:
        o_index = sys.argv.index("--o")

        if o_index >= 2:
            link = sys.argv[1]
        else:
            print("Error: Missing link after --o")
            sys.exit(1)

        if o_index + 1 < len(sys.argv):
            output_file = sys.argv[o_index + 1]
    else:
        output_file = "output.csv"
        link = sys.argv[1]

    if not link.startswith("https://www.petice.com/signatures.php"):
        print("Wrong host domain")
        sys.exit(1)

    data = getData(link)
    saveCSV(data, output_file)     

if __name__ == "__main__":
    main()
    

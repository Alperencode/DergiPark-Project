from bs4 import BeautifulSoup
import time
import requests
import os
import json

data_list = []
konu_list = []
counter = 0
checkCounter = 0
errorCounter = 0

# --------- Gathering Links ---------
linkList = []
magazine_links = []

# Parsing first page to get last page number
url = "https://dergipark.org.tr/tr/search?q=&section=journal"
url = requests.get(url)
soup = BeautifulSoup(url.content,"lxml")

# Gathering last page number 
page_slider = soup.find("ul",class_="kt-pagination__links mx-auto")
last_page = int(page_slider.find_all("li")[-2].text)
del url

# Generating links for all pages
def get_pages(pageNumber):
    url = f"https://dergipark.org.tr/tr/search/{pageNumber}?q=&section=journal"
    linkList.append(url)

# Gathering each magazine link
def get_magazine_links(url):
    url = requests.get(url)
    soup = BeautifulSoup(url.content,"lxml")
    # finding all magazines
    magazines = soup.find_all("h5",class_="card-title")
    for link in magazines:
        magazine_links.append(link.a.get('href'))

# range loop for use get_pages function
for pageNumber in range(1,last_page+1):
    get_pages(pageNumber)

# using get_magazine_links function
for url in linkList:
    get_magazine_links(url)
# --------- Gathering Links End ---------

# --------- Parsing the Data --------- 
# Creating data dictionary for each checked article
# Note: For this project, I didn't add any controls so all links will be used
def createDataDict(checkledLink):
    global checkCounter
    global counter
    url = requests.get(checkledLink)
    if url.status_code == 429:
        time.sleep(int(url.headers["Retry-After"]) + 10)
        print(f"slept {int(url.headers['Retry-After']) + 10} seconds")   
    soup = BeautifulSoup(url.content,"lxml")
    dataDict = {}
    counter += 1

    # Makale Başlığı
    article_title = soup.find("h3",class_="article-title").text.strip()
    dataDict['Makale Başlığı'] = article_title
    
    # Özet 
    ozet_section = soup.find("div",class_="article-abstract data-section")
    dataDict['Özet'] = ozet_section.text.replace("\n","")
    
    # Konu
    # split the values due ',' and take the first one
    # Note: This made for getting only the first 'Konu' of the article
    # You can use 'dataDict['Konular'] = tr_tag.td.text.strip()' to get all 'Konu' values:   
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    try:
        for tr_tag in tr_tags:
            if tr_tag.th.text.strip() == "Konular":
                first_konu = tr_tag.td.text.strip().split(",")[0]
                dataDict['Konular'] = first_konu
                if first_konu not in konu_list:
                    konu_list.append(first_konu)
    except:
        dataDict['Konular'] = ''

    # Yazar İsimleri
    article_authors = soup.find("p",class_="article-authors")
    try:
        names = []
        author_names = article_authors.find_all("a",class_="is-user")
        for name in author_names:
            names.append(name.text.strip())
        dataDict['Yazar İsimleri'] = names
    except:
        author_name = article_authors.find("a").text.strip()
        dataDict['Yazar İsimleri'] = author_name

    # Yayın Yılı
    # Note: Because of the 'Yayın yılı' is not specified in any class, I gathered the table which has the 'Yayın yılı' data
    # Then I made a control to find the 'Yayın yılı'
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    for tr_tag in tr_tags:
        if tr_tag.th.text.strip() == "Yayımlanma Tarihi":
            dataDict['Yayın Yılı'] = tr_tag.td.text.strip()

    # Dergi İsmi
    magazine_name = soup.find("h1",attrs={"id":"journal-title"}).text.strip()
    dataDict['Dergi İsmi'] = magazine_name

    # Yayın Sayfa URL
    page_url = checkledLink
    dataDict['Yayın Sayfa URL'] = page_url

    # Yayın PDF'i
    tool_bar = soup.find("div", attrs={"id":"article-toolbar"})
    a_tags = tool_bar.find_all("a")
    shortLink = a_tags[0].get("href")
    pdf_link = f"https://dergipark.org.tr{shortLink}"
    dataDict['Yayın PDF'] = pdf_link
    
    # Parsing the data has been done
    # I'm adding the data to the data_list
    data_list.append(dataDict)

    print(f"{counter}. Article created [{checkCounter}. Article]")

    # Writing the information into txt file (Used in articles directory)
    # But its not necessary for the main project

    # with open("article{counter}.txt",'w',encoding='utf-8') as f:
    #     f.write(f"Makale Başlığı: {dataDict['Makale Başlığı']}\n")
    #     f.write(f"Özet: {dataDict['Özet']}\n")
    #     f.write(f"Yazar isimleri: {dataDict['Yazar İsimleri']}\n")
    #     f.write(f"Yayın Yılı: {dataDict['Yayın Yılı']}\n")
    #     f.write(f"Dergi ismi: {dataDict['Dergi İsmi']}\n")
    #     f.write(f"Yayın sayfa url: {dataDict['Yayın Sayfa URL']}\n")
    #     f.write(f"Yayın pdf linki: {dataDict['Yayın PDF']}\n")
 

# Checking articles
# This made for adding controls to the data extraction
# For example:
# If you want to extract only articles with 'fizik' in their label, you can customize this function for it
# Just need to add 'if' statement to the 'for label in labels:' loop (E.g: if 'fizik in label':) 

# Because the purpose of this project is to extract all articles, I didn't add any controls
def checkFunc(magazineLink):
    global checkCounter
    global errorCounter
    url = requests.get(magazineLink)
    if url.status_code == 429:
        time.sleep(int(url.headers["Retry-After"]) + 10)
        print(f"slept {int(url.headers['Retry-After']) + 10} seconds")   
    soup = BeautifulSoup(url.content,"lxml")
    labels = soup.find_all("a",class_="card-title article-title")
    for label in labels:
        # removing row number and creating string variable for labels to check "roman"
        labelText = label.text.split(".")
        labelText.pop(0)
        labelText = ' '.join(labelText)
        labelText = labelText.replace("\n","").lower()
        # Control
        url = f"https:{label.get('href')}"
        try:
            createDataDict(f"https:{label.get('href')}")
        except:
            try:
                createDataDict(f"{label.get('href')}")
            except:
                errorCounter += 1
                print(f"Error appered [{errorCounter}. Error] , url: https:{label.get('href')}")

        checkCounter += 1

for magazinLink in magazine_links:
   checkFunc(magazinLink)
# --------- Parsing the Data End ---------

# --------- Output of the Data ---------
with open(f'article.jsonl', 'w',encoding='utf-8') as outfile:
    for entry in data_list:
        json.dump(entry, outfile,ensure_ascii=False)
        outfile.write('\n')
# --------- Output of the Data End ---------

print(f"\nFinished checking articles on {checkCounter} with {errorCounter} errors.")
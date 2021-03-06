from bs4 import BeautifulSoup
import time
import requests
import os
import json

data_list = []
parsingCounter = 0
errorCounter = 0

# --------- Loading Animation/Message ---------
loadingCounter = 0
animation = "|/-\\"
def loadingAnimation(text):
    global loadingCounter
    global animation
    loadingCounter += 1
    print(f"{text} {animation[loadingCounter % len(animation)]}", end="\r")
# --------- Loading Animation/Message End ---------

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
    loadingAnimation("Gathering magazine links from each page")
    get_magazine_links(url)
print("All magazines links gathered")
# --------- Gathering Links End ---------

# --------- Parsing the Data --------- 
# Parsing the data from each article link
print("\nStarting parsing the data")
def ParseArticle(articleLink):
    global parsingCounter
    parsingCounter += 1
    
    # 429 means that the server is overloaded
    url = requests.get(articleLink)
    if url.status_code == 429:
        time.sleep(int(url.headers["Retry-After"]) + 10)
        print(f"waited {int(url.headers['Retry-After']) + 10} seconds")   
    
    soup = BeautifulSoup(url.content,"lxml")
    
    # creating new dictionary for each article
    dataDict = {}

    # Makale Ba??l??????
    article_title = soup.find("h3",class_="article-title").text.strip()
    if len(article_title) < 1:
        article_title = soup.findAll("h3",class_="article-title")[1].text.strip()
    
    # ??zet 
    ozet_section = soup.find("div",class_="article-abstract data-section")
    dataDict['??zet'] = ozet_section.text.replace("\n","")
    
    # Konu
    # split the values due ','
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    try:
        for tr_tag in tr_tags:
            if tr_tag.th.text.strip() == "Konular":
                konu_list = []
                for konu in tr_tag.td.text.strip().split(","):
                    konu_list.append(konu.strip())
                dataDict['Konular'] = konu_list
    except:
        dataDict['Konular'] = ''

    # Yazar ??simleri
    article_authors = soup.find("p",class_="article-authors")
    try:
        names = []
        author_names = article_authors.find_all("a",class_="is-user")
        for name in author_names:
            names.append(name.text.strip())
        dataDict['Yazar ??simleri'] = names
    except:
        author_name = article_authors.find("a").text.strip()
        dataDict['Yazar ??simleri'] = author_name

    # Yay??n Y??l??
    # Note: Because of the 'Yay??n y??l??' is not specified in any class, I gathered the table which has the 'Yay??n y??l??' data
    # Then I made a control to find the 'Yay??n y??l??'
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    for tr_tag in tr_tags:
        if tr_tag.th.text.strip() == "Yay??mlanma Tarihi":
            dataDict['Yay??n Y??l??'] = tr_tag.td.text.strip()

    # Dergi ??smi
    magazine_name = soup.find("h1",attrs={"id":"journal-title"}).text.strip()
    dataDict['Dergi ??smi'] = magazine_name

    # Yay??n Sayfa URL
    dataDict['Yay??n Sayfa URL'] = articleLink

    # Yay??n PDF'i
    tool_bar = soup.find("div", attrs={"id":"article-toolbar"})
    a_tags = tool_bar.find_all("a")
    shortLink = a_tags[0].get("href")
    pdf_link = f"https://dergipark.org.tr{shortLink}"
    dataDict['Yay??n PDF'] = pdf_link
    
    # I'm adding Parsed data to the data_list
    data_list.append(dataDict)

    print(f"{parsingCounter}. Article created")

    # OUTPUT TO TXT FILE
    # Writing the information into txt file (Used in articles directory)
    # But its not necessary for the main project
    # ??? Uncomment the code below to use
    # OutputToTXTFile(dataDict)

# You can add specific Controls for articles
def AddControl(label):
    labelText = label.text.split(".")
    labelText.pop(0)
    labelText = ' '.join(labelText)
    labelText = labelText.replace("\n","").lower()
    # Example return for labelText: "COVID-19, Wine Routes, Crisis Management and Resilience Amongst Rural Wine Tourism Businesses"

    # Example of usage:
    # if "COVID-19" in labelText:
    #     return True
    # else:
    #     return False

# Parsing the magazine to get each article
def ParseMagazine(magazineLink):
    global errorCounter
    url = requests.get(magazineLink)
    if url.status_code == 429:
        time.sleep(int(url.headers["Retry-After"]) + 10)
        print(f"slept {int(url.headers['Retry-After']) + 10} seconds")   
    soup = BeautifulSoup(url.content,"lxml")
    labels = soup.find_all("a",class_="card-title article-title")
    for label in labels:
        # AddControl(label)
        try:
            ParseArticle(f"https:{label.get('href')}")
        except:
            try:
                ParseArticle(f"{label.get('href')}")
            except:
                errorCounter += 1
                print(f"An error occurred [{errorCounter}. Error] , url: {label.get('href')}")

for magazineLink in magazine_links:
    ParseMagazine(magazineLink)
# --------- Parsing the Data End ---------

# --------- Output of the Data ---------
def OutputToJSONLFile():
    with open('article.jsonl', 'w',encoding='utf-8') as outfile:
        for entry in data_list:
            json.dump(entry, outfile,ensure_ascii=False)
            outfile.write('\n')
OutputToJSONLFile()

def OutputToTXTFile(data):
    global parsingCounter
    with open(f"article{parsingCounter}.txt",'w',encoding='utf-8') as txt:
        txt.write(f"Makale Ba??l??????: {data['Makale Ba??l??????']}\n")
        txt.write(f"??zet: {data['??zet']}\n")
        txt.write(f"Yazar isimleri: {data['Yazar ??simleri']}\n")
        txt.write(f"Yay??n Y??l??: {data['Yay??n Y??l??']}\n")
        txt.write(f"Dergi ismi: {data['Dergi ??smi']}\n")
        txt.write(f"Yay??n sayfa url: {data['Yay??n Sayfa URL']}\n")
        txt.write(f"Yay??n pdf linki: {data['Yay??n PDF']}\n")
# --------- Output of the Data End ---------

print(f"\nFinished with {errorCounter} errors.")
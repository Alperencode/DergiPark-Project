from bs4 import BeautifulSoup
import requests,os,json

data_list, link_list, journal_links = [], [], []
parsed_counter, error_counter, loading_counter, request_counter, txt_counter, session_counter = 0, 0, 0, 0, 0, 1
MAX_REQUEST = 100

session = requests.Session()

def SendRequest(url):
    """
    Sends a request to the given url
    """
    global request_counter, error_counter

    if request_counter > MAX_REQUEST:
        ChangeSession()
        request_counter = 0

    try:
        url = session.get(url)
        request_counter += 1
    except Exception as e:
        error_counter += 1
        return

    return url

def ChangeSession():
    """
    Changes the session to avoid connection errors
    [Eg: 429 - Too Many Requests]
    """
    global session, session_counter
    session_counter += 1
    session = requests.Session()

def GetLastPage():
    """
    Gets the last page number
    """
    url = SendRequest("https://dergipark.org.tr/tr/search?q=&section=journal")
    soup = BeautifulSoup(url.content,"lxml")

    # Gathering last page number 
    page_slider = soup.find("ul",class_="kt-pagination__links mx-auto")
    last_page = int(page_slider.find_all("li")[-2].text)

    return last_page

last_page = GetLastPage()

def LoadingAnimation(text):
    """
    Creates Loading Animation with argument string
    """
    global loading_counter
    animation = "|/-\\"
    loading_counter += 1
    print(f"{text} {animation[loading_counter % len(animation)]}", end="\r")

def GetPages(page_number):
    """
    Generates links for all pages
    """
    url = f"https://dergipark.org.tr/tr/search/{page_number}?q=&section=journal"
    link_list.append(url)

def GetJournalLinks(url_str):
    """
    Gathering each journal link from each page
    """
    LoadingAnimation(f"Gathering journals [Approximately {last_page*24}]")
    url = SendRequest(url_str)

    soup = BeautifulSoup(url.content,"lxml")

    journals = soup.find_all("h5",class_="card-title")
    for link in journals:
        journal_links.append(link.a.get('href'))


def ParseArticle(articleLink):
    """
    Parsing each article data in 8 main headings
    """
    global parsed_counter, error_counter
    
    url = SendRequest(articleLink)
    if url == None:
        return
    soup = BeautifulSoup(url.content,"lxml")

    # Creating a dictionary to store the data
    data_dict = {}

    # 1) Makale Başlığı (Article Title)
    article_title = soup.find("h3",class_="article-title").text.strip()
    if len(article_title) < 1:
        article_title = soup.findAll("h3",class_="article-title")[1].text.strip()
    data_dict['Makale Başlığı'] = article_title.replace("\n","").replace("  ","").replace("\t","")
    
    # 2) Özet 
    ozet_section = soup.find("div",class_="article-abstract data-section")
    data_dict['Özet'] = ozet_section.text.replace("\n","")[2:] if ozet_section.text[0:2] != "Öz" else ozet_section.text.replace("\n","")[2:]
    
    # 3) Konular (Topics)
    # split the values due ','
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    try:
        for tr_tag in tr_tags:
            if tr_tag.th.text.strip() == "Konular":
                konu_list = []
                for konu in tr_tag.td.text.strip().split(","):
                    konu_list.append(konu.strip())
                data_dict['Konular'] = konu_list
    except:
        data_dict['Konular'] = ''

    # 4) Yazar İsimleri (Author Names)
    article_authors = soup.find("p",class_="article-authors")
    try:
        names = []
        author_names = article_authors.find_all("a",class_="is-user")
        for name in author_names:
            names.append(name.text.strip())
        data_dict['Yazar İsimleri'] = names
    except:
        author_name = article_authors.find("a").text.strip()
        data_dict['Yazar İsimleri'] = author_name

    # 5) Yayın Yılı (Publication Year)
    # Scraping the publication year from the table
    info_table = soup.find("table",class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    for tr_tag in tr_tags:
        if tr_tag.th.text.strip() == "Yayımlanma Tarihi":
            data_dict['Yayın Yılı'] = tr_tag.td.text.strip()

    # 6) Dergi İsmi (Journal Name)
    journal_name = soup.find("h1",attrs={"id":"journal-title"}).text.strip()
    data_dict['Dergi İsmi'] = journal_name

    # 7) Yayın Sayfa URL (Article Page URL)
    data_dict['Yayın Sayfa URL'] = articleLink

    # 8) Yayın PDF (Article PDF)
    tool_bar = soup.find("div", attrs={"id":"article-toolbar"})
    a_tags = tool_bar.find_all("a")
    short_link = a_tags[0].get("href")
    pdf_link = f"https://dergipark.org.tr{short_link}"
    data_dict['Yayın PDF'] = pdf_link
    
    # Appending the data to the data_list
    data_list.append(data_dict)

    parsed_counter += 1
    LoadingAnimation(f"Parsed Articles: {parsed_counter}, Errors: {error_counter} [Session count: {session_counter}]")


def ParseJournal(journal_link):
    """
    Parsing the journal link to get each article
    """
    global error_counter
    url = SendRequest(journal_link)

    if url == None:
        return

    soup = BeautifulSoup(url.content,"lxml")
    labels = soup.find_all("a",class_="card-title article-title")

    for label in labels:
        # if AddControl('Covid'):
        try:
            ParseArticle(f"https:{label.get('href')}")
        except:
            try:
                ParseArticle(label.get('href'))
            except:
                error_counter += 1

def AddControl(label):
    """
    Adding control to the article label (Eg: 'Covid')
    Can be used to filter the articles
    Returns boolean
    """
    label_text = label.split(".")
    label_text.pop(0)
    label_text = ' '.join(label_text)
    label_text = label_text.replace("\n","").lower()

    if label.lower() in label_text:
        return True
    return False

    # Example usage:
    # if AddControl('Covid'):
    #     ParseArticle(f"https:{label.get('href')}")


def MakeDir(dir_name):
    """
    Creating a directory
    If the directory exists, it will be deleted
    """
    import os, shutil
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def OutputToJSONLFile():
    """
    Outputting the data to a JSONL file
    """
    if not data_list:
        return
    with open('OutputJSONL/articles.jsonl', 'w',encoding='utf-8') as outfile:
        for entry in data_list:
            json.dump(entry, outfile,ensure_ascii=False)
            outfile.write('\n')

def OutputToTXTFile():
    """
    Outputting the data to a TXT file
    """
    if not data_list:
        return
    for counter in range(0, parsed_counter):
        with open(f"OutputTXT/articles_{counter+1}.txt", "w",encoding='utf-8') as file:
            for key, value in data_list[counter].items():
                if type(value) == list:
                    file.write(f"{key}: ")
                    for item in value:
                        file.write(f"{item}, ") if item != value[-1] else file.write(f"{item}")
                file.write(f"{key}: {value}\n")
    
def Stats(time):
    """
    Printing the stats of the program
    """
    print(f"\n\nTotal time: {time}")
    if parsed_counter == 0:
        print("No articles parsed")
        return
    print(f"Total articles: {parsed_counter} [Succes rate: %.2f%%]" % (parsed_counter/(parsed_counter+error_counter)*100))
    print(f"Total errors: {error_counter} [Error rate: %.2f%%]" % (error_counter/(parsed_counter+error_counter)*100))
    print(f"Session count: {session_counter}")
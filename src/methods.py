from bs4 import BeautifulSoup
import requests
import json

parsed_count, error_count, loading_count = 0, 0, 0
request_count, txt_count, session_count = 0, 0, 1
data_list, journal_links = [], []

MAX_REQUEST = 100
SESSION = requests.Session()


def SendRequest(url):
    """
    Sends a request to the given url
    """
    global request_count, error_count

    if request_count > MAX_REQUEST:
        ChangeSession()
        request_count = 0

    try:
        url = SESSION.get(url)
        request_count += 1
    except Exception:
        error_count += 1
        return

    return url


def ChangeSession():
    """
    Changes the session to avoid connection errors
    [Eg: 429 - Too Many Requests]
    """
    global SESSION, session_count
    session_count += 1
    SESSION = requests.Session()


def GetLastPage():
    """
    Gets the max page number from the first page of DergiPark
    """
    url = SendRequest("https://dergipark.org.tr/tr/search?q=&section=journal")
    soup = BeautifulSoup(url.content, "lxml")

    # Gathering last page number
    page_slider = soup.find("ul", class_="kt-pagination__links mx-auto")
    last_page = int(page_slider.find_all("li")[-2].text)

    return last_page


def LoadingAnimation(text):
    """
    Creates Loading Animation with argument string
    """
    global loading_count
    animation = "|/-\\"
    loading_count += 1
    print(f"{text} {animation[loading_count % len(animation)]}", end="\r")


def GetJournalLinks(url_str):
    """
    Gathering each journal link from each page
    """
    LoadingAnimation("Gathering journals")
    url = SendRequest(url_str)

    soup = BeautifulSoup(url.content, "lxml")

    journals = soup.find_all("h5", class_="card-title")
    for link in journals:
        journal_links.append(link.a.get('href'))


def ParseArticle(articleLink):
    """
    Parsing each article data in 8 main headings
    """
    global parsed_count, error_count

    url = SendRequest(articleLink)
    if not url:
        return
    soup = BeautifulSoup(url.content, "lxml")

    # Creating a dictionary to store the data
    data_dict = {}

    # 1) Makale Başlığı (Article Title)
    article_title = soup.find("h3", class_="article-title").text.strip()
    if len(article_title) < 1:
        article_title = soup.findAll("h3", class_="article-title")[1]
        article_title = article_title.text.strip()
    data_dict['Makale Başlığı'] = article_title.replace(
        "\n", "").replace("  ", "").replace("\t", "")

    # 2) Özet
    ozet_section = soup.find("div", class_="article-abstract data-section")
    if ozet_section.text[0:2] != "Öz":
        data_dict['Özet'] = ozet_section.text.replace("\n", "")[2:]
    else:
        ozet_section.text.replace("\n", "")[2:]

    # 3) Konular (Topics)
    # split the values due ','
    info_table = soup.find("table", class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    try:
        for tr_tag in tr_tags:
            if tr_tag.th.text.strip() == "Konular":
                konu_list = []
                for konu in tr_tag.td.text.strip().split(","):
                    konu_list.append(konu.strip())
                data_dict['Konular'] = konu_list
    except Exception:
        data_dict['Konular'] = ''

    # 4) Yazar İsimleri (Author Names)
    article_authors = soup.find("p", class_="article-authors")
    try:
        names = []
        author_names = article_authors.find_all("a", class_="is-user")
        for name in author_names:
            names.append(name.text.strip())
        data_dict['Yazar İsimleri'] = ', '.join(name for name in names)
    except Exception:
        author_name = article_authors.find("a").text.strip()
        data_dict['Yazar İsimleri'] = author_name

    # 5) Yayın Yılı (Publication Year)
    # Scraping the publication year from the table
    info_table = soup.find("table", class_="record_properties table")
    tr_tags = info_table.find_all("tr")
    for tr_tag in tr_tags:
        if tr_tag.th.text.strip() == "Yayımlanma Tarihi":
            data_dict['Yayın Yılı'] = tr_tag.td.text.strip()

    # 6) Dergi İsmi (Journal Name)
    journal_name = soup.find("h1", attrs={"id": "journal-title"}).text.strip()
    data_dict['Dergi İsmi'] = journal_name

    # 7) Yayın Sayfa URL (Article Page URL)
    data_dict['Yayın Sayfa URL'] = articleLink

    # 8) Yayın PDF (Article PDF)
    tool_bar = soup.find("div", attrs={"id": "article-toolbar"})
    a_tags = tool_bar.find_all("a")
    short_link = a_tags[0].get("href")
    pdf_link = f"https://dergipark.org.tr{short_link}"
    data_dict['Yayın PDF'] = pdf_link

    # Appending the data to the data_list
    data_list.append(data_dict)

    parsed_count += 1
    LoadingAnimation(f"Parsed Articles: {parsed_count}, Errors: {error_count} [Session count: {session_count}]")


def ParseJournal(journal_link):
    """
    Parsing the journal link to get each article
    """
    global error_count
    url = SendRequest(journal_link)

    if not url:
        return

    soup = BeautifulSoup(url.content, "lxml")
    labels = soup.find_all("a", class_="card-title article-title")

    for label in labels:
        # if AddControl('Covid'):
        try:
            ParseArticle(f"https:{label.get('href')}")
        except Exception:
            try:
                ParseArticle(label.get('href'))
            except Exception:
                error_count += 1


def AddControl(label):
    """
    Adding control to the article label (Eg: 'Covid')
    Can be used to filter the articles
    Returns boolean
    """
    label_text = label.split(".")
    label_text.pop(0)
    label_text = ' '.join(label_text)
    label_text = label_text.replace("\n", "").lower()

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
    import os
    import shutil
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)


def OutputToJSONLFile():
    """
    Outputting the data to a JSONL file
    """
    if not data_list:
        return
    with open('OutputJSONL/articles.jsonl', 'w', encoding='utf-8') as outfile:
        for entry in data_list:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')


def OutputToTXTFile():
    """
    Outputting the data to a TXT file
    """
    if not data_list:
        return
    for counter in range(0, parsed_count):
        with open(f"OutputTXT/articles_{counter+1}.txt", "w", encoding='utf-8') as file:
            for key, value in data_list[counter].items():
                if type(value) is list:
                    file.write(f"{key}: ")
                    for item in value:
                        file.write(
                            f"{item}, ") if item != value[-1] else file.write(f"{item}")
                file.write(f"{key}: {value}\n")


def Stats(time):
    """
    Printing the stats of the program
    """
    print(f"\n\nTotal time: {time}")
    if parsed_count == 0:
        print("No articles parsed")
        return

    print(f"Total articles: {parsed_count} [Succes rate: %.2f%%]" %
          (parsed_count/(parsed_count+error_count)*100))

    print(f"Total errors: {error_count} [Error rate: %.2f%%]" %
          (error_count/(parsed_count+error_count)*100))

    print(f"Session count: {session_count}")

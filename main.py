"""
- DergiPark's information
    - DergiPark has 100+ pages
    - Each page has 24 Journal
    - Each Journal has average 10 Articles
    - Total Articles: 24000+

- Roadmap of the project
    - Get the current last page number
    - Create a link for each page
    - Get the journal links from each page
    - Get the article links from each journal
    - Parse the data from each article

@Author: Alperen Ağa
@Date: 02.04.2022 (dd.mm.yyyy)
@Last Update: 20.05.2024 (dd.mm.yyyy)
"""

from src import methods
from datetime import datetime

# Starting timer
start_time = datetime.now()

# Creating output directories
methods.MakeDir("OutputTXT")
methods.MakeDir("OutputJSONL")

# Getting the last page number
last_page = methods.GetLastPage()

# Gathering journal links from each page
for page_number in range(1, last_page+1):
    methods.GetJournalLinks(
        f"https://dergipark.org.tr/tr/search/{page_number}?q=&section=journal")

print("\nAll journal links gathered")
print("\nParsing journals")

# Parsing each journal and each article in these journals
for journal_link in methods.journal_links:
    methods.ParseJournal(journal_link)

# Outputting the data
methods.OutputToJSONLFile()
methods.OutputToTXTFile()

# Printing stats
finish_time = datetime.now() - start_time
methods.Stats(finish_time)

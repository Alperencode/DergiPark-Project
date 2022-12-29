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
@Last Update: 19.12.2022 (dd.mm.yyyy)
"""

from src import *

# Starting timer
start_time = datetime.datetime.now()

# Creating output directories
MakeDir("OutputTXT")
MakeDir("OutputJSONL")

# Parsing pages and creating page links
for page_number in range(1, last_page+1):
    GetPages(page_number)

# Gathering journal links from each page
for url in link_list:
    GetJournalLinks(url)

print("\nAll journal links gathered")
print("\nParsing journals")

# Parsing each journal and each article in these journals
for journal_link in journal_links:
    ParseJournal(journal_link)

# Outputting the data
OutputToJSONLFile()
OutputToTXTFile()

# Printing stats
finish_time = datetime.datetime.now() - start_time
Stats(finish_time)    

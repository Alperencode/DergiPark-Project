"""
- DergiPark's information
    - DergiPark has 100+ pages
    - Each page has 24 Magazine
    - Each Magazine has average 10 Articles
    - Total Articles: 24000+

- Roadmap of the project
    - Get the current last page number
    - Create a link for each page
    - Get the magazine links from each page
    - Get the article links from each magazine
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

# Gathering magazine links from each page
for url in link_list:
    GetMagazineLinks(url)

print("\nAll magazines links gathered")
print("\nStarting parsing the data")

# Parsing each magazine and each article in these magazines
for magazine_link in magazine_links:
    ParseMagazine(magazine_link)

OutputToJSONLFile()
OutputToTXTFile()

finish_time = datetime.datetime.now() - start_time
Stats(finish_time)    
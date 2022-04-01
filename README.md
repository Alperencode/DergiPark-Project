# DergiPark Project

## Description

[DergiPark](https://dergipark.org.tr/tr/) is one of the biggest websites that provides electronic hosting for academic peer-reviewed articles in Turkey.
In this project, I extracted all articles from DergiPark and parsed the data in 8 main headings.
Afterwards, I outputted that data into different formats of files like .jsonl (JSON lines) and .txt (Text).
The number of formats can be increased by customizing the source code.

&emsp; DergiPark currently has over 25.000 academic articles.
I extracted them all with [Web Scraping](https://www.edureka.co/blog/web-scraping-with-python/#:~:text=Web%20scraping%20is%20an%20automated,or%20writing%20your%20own%20code.) in Python.
Web Scraping is basically extracting the big amount of data from a specific website.

&emsp; This data can be used in Ai models to give meaning to this data or train any model with them. 
Because the data is academic peer-reviewed articles this data can be used in any formal project

<br>

## Used Techs

I used Python as a main programming language.

&emsp; For Web scraping, I used 'BeautifulSoup' and 'request' modules.
Except for these I used 'json', 'os' and 'time' for outputting the data and waiting sections.

<br>


## Installation

Installing the required modules

```bash
pip install -r requirements.txt
```

<br>

## Usage/Examples

Run main.py which is in root directory 

```bash
python main.py
```

Example of proper working

<img src="img/Project-Video.gif">

<br>


## Screenshots

Screenshot from JSON line data

<img src="img/jsonl-example.png" width=700>

<br>

Screenshot from txt data

<img src="img/txt-example.png" width=700>

<br>

## Authors

- [Alperen Aga](https://www.github.com/Alperencode)

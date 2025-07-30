import requests
import pandas as pd
from bs4 import BeautifulSoup

url='https://echa.europa.eu/substances-restricted-under-reach'
r=requests.get(url)
print(r)
from bs4 import BeautifulSoup
import logging

html = ''

with open('cum.html', 'r') as htmlREALLY:
        html = htmlREALLY.read()

soup = BeautifulSoup(html, 'lxml')

# soup.find_all(class="explanation fade in")
fuck = soup.find_all('span', class_="explanationMessage")
print(fuck)
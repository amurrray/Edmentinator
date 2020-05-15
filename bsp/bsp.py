import mechanicalsoup
from secrets import MY_USERNAME, MY_PASSWORDword

browser = mechanicalsoup.StatefulBrowser()
browser.open("https://www.coolmathgames.com/login")

firstLink = browser.get_url() 
print (firstLink)

browser.select_form('form[action="/login"]')
browser["name"] = MY_USERNAME 
browser["pass"] = MY_PASSWORD

print('Logging In...' + '\n')

browser.submit_selected()

secondLink = browser.get_url()
#print(secondLink)

if str(secondLink) != (firstLink):
    print('"im in"' + '\n' + browser.get_url())
else:
    print('"i am not in"' + '\n' + browser.get_url())

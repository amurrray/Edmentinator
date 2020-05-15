import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

query = input('whatcha looking for doofus?\n')
chrome_options = Options()

# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
def ask_google(query):

    # Search for query
    query = query.replace(' ', '+')

    driver.get('http://www.google.com/search?q=' + query)

    # Get text from Google answer box

    # answer = driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", 350, 230).text
    answer = driver.find_element(By.CLASS_NAME, 'Z0LcW').text
    return answer

print(ask_google(query))
# print(ask_google("when was the decleration of independence written"))
driver.quit()

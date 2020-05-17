import os
from pathlib import Path
import json
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# newAmount = 3

# print(newAmount)

# theEA = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

# print(theEA)

# theAA = []

# print(theAA)

# i = 0
# for x in theEA:
#     theAA.append(theEA[i])
#     print(theAA)
#     print(len(theAA))
#     i += 1
#     if len(theAA) == newAmount:
#         print("theAA done")
#         break

# import logging
# import os
# from json import loads
# from pathlib import Path
# from secrets import MY_PASSWORD, MY_USERNAME
# from time import sleep

# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.support.ui import WebDriverWait
# from slimit import ast
# from slimit.parser import Parser as JavascriptParser
# from slimit.visitors import nodevisitor

# # setup logging
# logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
# logger = logging.getLogger('main')
# logger.setLevel(logging.DEBUG)

# # constants
# if os.name == 'nt':
#     CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
# else:
#     CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver'
# EXTENSION_PATH = str(Path(__file__).resolve().parents[0]) + '/classlink.crx'
# CHROME_OPTIONS = webdriver.ChromeOptions()
# CHROME_OPTIONS.add_extension(EXTENSION_PATH)
# BASE_URL = "https://f2.app.edmentum.com/"
# DEBUG = True
# logger.debug('soup was here')

# driver = webdriver.Chrome(CHROME_PATH, options=CHROME_OPTIONS)
# actions = ActionChains(driver)
# assignments = None # placeholder because i bad code flow


# driver.get("https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView")

# example = "//h2[@id='Example']"
# exampleElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(example))

# # ActionChains(driver).move_to_element(exampleElm).perform()

# sleep(1)

# driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", exampleElm)

# class z():
#     def __init__(self, name):
#         self.name = name

# test = z('fred')

# z.name

#HERE DADDY

# if os.name == 'nt':
#     CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
# else:
#     CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver'

# driver = webdriver.Chrome(executable_path=CHROME_PATH)
# driver.implicitly_wait(30)

# driver.get("https://chercher.tech/practice/table")


if os.name == 'nt':
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
else:
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver'
driver = webdriver.Chrome(executable_path=CHROME_PATH)
driver.implicitly_wait(30)

driver.get("https://chercher.tech/practice/table")

tableElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//table[@id='webtable']"))

class whatTheFuck:
    
    def __init__(self, webtable):
       self.table = webtable

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def get_row_count(self):
      return len(self.table.find_elements_by_tag_name("tr")) - 1

    def get_column_count(self):
        return len(self.table.find_elements_by_xpath("//tr[2]/td"))

    def get_table_size(self):
        return {"rows": self.get_row_count(),
                "columns": self.get_column_count()}

    def row_data(self, row_number):
        if(row_number == 0):
            raise Exception("Row number starts from 1")

        row_number = row_number + 1
        row = self.table.find_elements_by_xpath("//tr["+str(row_number)+"]/td")
        rData = []
        for webElement in row :
            rData.append(webElement.text)

        return rData

    def column_data(self, column_number):
        col = self.table.find_elements_by_xpath("//tr/td["+str(column_number)+"]")
        rData = []
        for webElement in col :
            rData.append(webElement.text)
        return rData

    def get_all_data(self):
        # get number of rows
        noOfRows = len(self.table.find_elements_by_xpath("//tr")) -1
        # get number of columns
        noOfColumns = len(self.table.find_elements_by_xpath("//tr[" + str(noOfRows) + "]/td"))
        allData = []
        # iterate over the rows, to ignore the headers we have started the i with '1'
        for i in range(2, noOfRows+2):
            # reset the row data every time
            ro = []
            # iterate over columns
            for j in range(1, noOfColumns+1) :
                # get text from the i th row and j th column
                ro.append(self.table.find_element_by_xpath("//tr["+str(i)+"]/td["+str(j)+"]").text)

            # add the row data to allData of the self.table
            allData.append(ro)

        return allData

    def presence_of_data(self, data):
        # verify the data by getting the size of the element matches based on the text/data passed
        dataSize = len(self.table.find_elements_by_xpath("//td[normalize-space(text())='"+data+"']"))
        presence = False
        if(dataSize > 0):
            presence = True
        return presence

    def get_cell_data(self, row_number, column_number):
        if(row_number == 0):
            raise Exception("Row number starts from 1")

        row_number = row_number+1
        cellData = table.find_element_by_xpath("//tr["+str(row_number)+"]/td["+str(column_number)+"]").text
        return cellData

columnNUM = whatTheFuck(tableElm).get_column_count()
everything = whatTheFuck(tableElm).get_all_data()
print(everything)
print(columnNUM)
# doof = []
# print("doof: " + str(doof) )

#   
#     doof.append(" ")

# print("new doof: " + str(doof))

array = ['google.com','Google', 'Search Engine']
# everything.index(array)
print(everything.index(array))
# print(everything.index[0])

# ohFuckRowCount = whatTheFuck(tableElm).get_row_count()
# ohShitBoys = driver.execute_script("arguments[0].get_row_count();", whatTheFuck(tableElm))

# print(ohFuckRowCount)

# class Object:
#     def toJSON(self):
#         return json.dumps(self, default=lambda o: o.__dict__, 
#             sort_keys=True, indent=4)

# me = Object()
# me.name = "Onur"
# me.age = 35
# me.dog = Object()
# me.dog.name = "Apollo"

# print(me.toJSON())






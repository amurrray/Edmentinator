import logging
import os
from json import loads
from pathlib import Path
from secrets import MY_PASSWORD, MY_USERNAME
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

# constants
if os.name == 'nt':
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
else:
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver'
EXTENSION_PATH = str(Path(__file__).resolve().parents[0]) + '/classlink.crx'
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_extension(EXTENSION_PATH)
BASE_URL = "https://f2.app.edmentum.com/"
DEBUG = True
logger.debug('soup was here')

driver = webdriver.Chrome(CHROME_PATH, options=CHROME_OPTIONS)
actions = ActionChains(driver)
assignments = None # placeholder because i bad code flow

class TableThings:
    def __init__(self, webtable):
        self.table = webtable

    def get_row_count(self):
        return len(self.table.find_elements_by_tag_name("tr")) - 1

    def get_column_count(self):
        return len(self.table.find_elements_by_xpath("//tr[2]/th"))

    def get_table_size(self):
        return {"rows": self.get_row_count(),
                "columns": self.get_column_count()}

    def row_data(self, row_number):
        if(row_number == 0):
            raise Exception("Row number starts from 1")
        row_number = row_number + 1
        row = self.table.find_elements_by_xpath("//tr["+str(row_number)+"]/th")
        rData = []
        for webElement in row :
            rData.append(webElement.text)
        return rData

    def column_data(self, column_number):
        col = self.table.find_elements_by_xpath("//tr/th["+str(column_number)+"]")
        rData = []
        for webElement in col :
            rData.append(webElement.text)
        return rData

    def get_all_data(self):
        # get number of rows
        noOfRows = len(self.table.find_elements_by_xpath("//tr")) -1
        # print("noOfRows: " + str(noOfRows))
        # get number of columns
        noOfColumns = len(self.table.find_elements_by_xpath("//tr[2]/th"))
        # print("noOfColumns: " + str(noOfColumns))
        allData = []
        # iterate over the rows, to ignore the headers we have started the i with '1'
        for i in range(2, noOfRows+2):
            # reset the row data every time
            ro = []
            # iterate over columns
            for j in range(1, noOfColumns+1) :
                # get text from the i th row and j th column
                try:
                    thPath = "//tr["+str(i)+"]/th["+str(j)+"]"
                    tdPath = "//tr["+str(i)+"]/td["+str(j)+"]"
                    ro.append(self.table.find_element_by_xpath(thPath).text)
                    # print(str(thPath)+" found")
                except NoSuchElementException:
                    # print("//th not found, looking for //td")
                    ro.append(self.table.find_element_by_xpath(tdPath).text)
                    print(str(tdPath)+"found")
            # add the row data to allData of the self.table
            # print("i =" + str(i))
            allData.append(ro)

        return allData

    def presence_of_data(self, data):
        # verify the data by getting the size of the element matches based on the text/data passed
        dataSize = len(self.table.find_elements_by_xpath("//th[normalize-space(text())='"+data+"']"))
        presence = False
        if(dataSize > 0):
            presence = True
        return presence

    def get_cell_data(self, row_number, column_number):
        if(row_number == 0):
            raise Exception("Row number starts from 1")
        row_number = row_number+1
        cellData = table.find_element_by_xpath("//tr["+str(row_number)+"]/th["+str(column_number)+"]").text
        return cellData

def getAssignments():
    page_source = driver.page_source
    
    soup = BeautifulSoup(page_source, 'lxml')
    assignments = []
    assignment_selector = soup.find_all('div', class_='assignment isotope-item')
    for assignment_selector in assignment_selector:
        name = assignment_selector.find('div', class_='assignmentName').get_text()
        name = " ".join(name.splitlines()) # remove weird newlines
        try:
             name = name.split("- ", 1)[1]
             name = name.split(" - Period", 1)[0]
        except:
            pass
        url = assignment_selector.find('a').get('href')
        assignment = {"name": name, "url": url}
        assignments.append(assignment)
    return assignments

def assignmentSelect(assignments):
    WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('activeAssignments')) #Just to make sure page is loaded before looking for classes
    sleep(.3)

    theEntireAlphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    theAvailableAlphabet = []

    for letter in theEntireAlphabet:
        theAvailableAlphabet.append(letter)
        if len(theAvailableAlphabet) == len(assignments):
            break
    
    i = 0
    for assignment in assignments:
        print('[' + theAvailableAlphabet[i] + '] ' + assignment['name'])
        i += 1

    while True:
        selectLet = input('Choose an assignment: ').upper()
        if selectLet in theAvailableAlphabet:
            break
        else:
            print('\n'+"Error: Invalid Character")
    selection = theAvailableAlphabet.index(selectLet) 

    print('Chose ' + assignments[selection]['name'])
    driver.get(BASE_URL + assignments[selection]['url'])

def openCourse():
    try:
        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[text()='0 of 2']"))).click()

    except NoSuchElementException:
        logger.error("no classes found")
        while True:
            goBack = input ("Go Back and Pick New Class?" + '\n' + "[y/n]? ")
            if goBack in ['y', 'n']:
                break
        if goBack == 'y':
            WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[text()='Back to Home']"))).click()
            assignmentSelect(assignments)

        elif goBack == 'n':
            print("goodbye!" + "\n" + "you're on your own now.")
    else:
        print("assignment found")

def openTut():
    try:
        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Tutorial')]"))).click() 

    except NoSuchElementException:
        print("Tutorial Not Found")
    
    else:
        print("Tutorial Opened")

def completeTut():
    try:
        print('is it disabled?')
        driver.find_element_by_xpath("//button[@class='tutorial-nav-next disabled']")

    except NoSuchElementException:
        print("nada")
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")).click()
        print("*Next*")
        sleep(.5)
        completeTut()
    else:
        print("yes")
        print("work to be done...")
        
        sleep(.5)

        isFRQ()

        isMPC()

        isDrag()

        isFinished()
      

def isFRQ():
    
    try:
        logger.debug('is it FRQ?')
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        print("switched to frame")
        driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')

    except NoSuchElementException:
        logger.debug("nope")
    else:
        logger.debug("yes")
        frqFrames = driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')
        logger.debug(str(len(frqFrames)) + " FRQs Found")
        if len(frqFrames) == 0:
            driver.switch_to.parent_frame()
            return
        
        count_arr = [str("mce_") + str(i) + str("_ifr") for i, frqFrame in enumerate(frqFrames, start=0)]
        print("found iframes: " + str(count_arr))
        for frqFrame in count_arr:
            try:  #grabs chart answer 
                print("looking for table ans")
                tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-5 k-table']") #gets answer table
                AnswerTable = TableThings(tableAnswerElm).get_all_data()    
            except NoSuchElementException:
                print("no table answer saved")
            

            driver.switch_to.frame(frqFrame)
            print("in " + frqFrame)
            # box1Elm = driver.find_element_by_id("tinymce").get_attribute("class")
            # print(box1Elm)

            # try statement to figure out if it chart or not
            try:
                print("table?")
                driver.find_element_by_xpath('//table[@class="ed border-on padding-5 k-table mce-item-table"]')
                
            except NoSuchElementException:
                try:
                    tableComplete = 0
                    print("\n" + "Not Table")
                    driver.find_element_by_xpath("//p")
                except NoSuchElementException:
                    logger.error("Cant find frq textbox or chart")
                else:
                    print("normal frq")
                    answer = driver.find_element_by_xpath("//p")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", answer)
                    answer.send_keys('.') #REPLACE WITH VAR TO ANSWER
                    print("switching frame")
                    driver.switch_to.parent_frame()
                    try:
                        print("looking for btn")
                        driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']")
                    except NoSuchElementException:
                        print("all buttons pressed, hopefully")
                    else:
                        print("found btn")
                        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
                        print("scroll to btn")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
                        submitBtnElm.click()
                        sleep(.5)
            else:
                print("yeppa")           
                tableElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//table[@class='ed border-on padding-5 k-table mce-item-table']"))
                # print(tableElm)
                tableElmClass = tableElm.get_attribute("class")
                print(tableElmClass)
                #What the Fuck!
                TableData = TableThings(tableElm).get_all_data()

                print("Question Table: " + str(TableData))
                try:
                    print("AnserTable: " + str(AnswerTable))
                except UnboundLocalError:
                    print("no Answer Table")
                # print(AnswerTable)

                columnNUM = TableThings(tableElm).get_column_count()
                print("# of Columns: "+str(columnNUM))
                doof = []
                print("doof: " + str(doof) )

                for _ in range(int(columnNUM)): 
                    doof.append(" ")

                print("new doof: " + str(doof))
                print(TableData[1])

                # print("is" + str(doof) + "==" + str(TableData[1]))
                # if str(doof) == str(TableData[1]):
                #     continue
                # else:
                #     print("its not equal")
                #     driver.switch_to.parent_frame()
                #     break

                rowNUM = TableData.index(doof)
                print("Row #: "+str(rowNUM + 1)) # +1 because arrays start @ 0
                

                i = 1
                for _ in range(columnNUM):
                    print("in loop")
                    tableboxPATH =  "//tr["+str(rowNUM + 2)+"]/td["+str(i)+"]" # +2 to include table header row and arrays start at 0
                    print(tableboxPATH)
                    tableboxELM = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(tableboxPATH))
                    tableboxELM.send_keys(".") #REPLACE WITH VAR TO ANSWER
                    i+=1
                driver.switch_to.parent_frame()
                print("chart complete")
            

            submittedArray = driver.find_elements_by_xpath("//button[@class='btn buttonDone' and @style='display: none;']")
            print(len(frqFrame)) 
            print(len(submittedArray))
            if len(frqFrame) == len(submittedArray): # check if we are on the last one
                break
        driver.switch_to.parent_frame()
        print("FRQ(s) Answered")

def isMPC():
    try:
        print('is it MPC?')
        # print("looking for iframe")
        driver.find_element_by_id("content-iframe")
        print("switched to i frame")
        driver.switch_to.frame("content-iframe")
        # print("looking for mpqChoices")
        driver.find_element_by_id("mcqChoices")
        # print("finished all that jont")
    except NoSuchElementException:
        print("nope")
        driver.switch_to.parent_frame()
    else:
        print("yes")
        script = driver.find_element_by_xpath("//script[contains(.,'IsCorrect')]").get_attribute("innerHTML")
        # print(script + '\n')
        scriptElmCut = script[20:-2]
        # print(scriptElmCut + '\n')
        parsedScript = loads(scriptElmCut) 
        theEntireNumabet = ['0', '1', '2', '3']
        i = 0
        for choice in parsedScript['Choices']: # this goes thru all the choices
            if choice['IsCorrect']: # if the isCorrect bool is True, then the answer is correct
                print('the answer is ' + theEntireNumabet[i])
                ans = theEntireNumabet[i]
            i += 1
            
        mpcAnsr = 'choice' + ans
        print(mpcAnsr)
        mpcBtn = "//input[@id=\'" + mpcAnsr + "\']"
        # userURL = "//input[@id='username']"
        print(mpcBtn)
        # mpcBtnElm = driver.find_element_by_xpath(mpcBtn)
        mpcBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(mpcBtn))
        mpcBtnElm.click()
        driver.switch_to.parent_frame()
        print("MPC answered")

def isDrag():
    try:
        print("is it drag?")
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        print("switched to frame")
        driver.find_elements_by_xpath('//div[@class="drop-panel"]')
        
    except NoSuchElementException:
        print("nada")
    else:
        print("yada")

def isFinished():
    try:
        print("are we done?")
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        congrats = "//h1[contains(text(),'Congratulations!')]"
        driver.find_element_by_xpath(congrats)
        driver.switch_to.parent_frame()
        
    except NoSuchElementException:
        print("nope")
        
    else:
        print("Tutorial Complete")
        driver.find_element_by_xpath("//button[@class='tutorial-nav-exit']").click() #closes tutorial

def main(): # this the real one bois
    driver.get("https://launchpad.classlink.com/loudoun")

    userURL = "//input[@id='username']"
    passURL = "//input[@id='password']"
    buttonURL = "//button[@id='signin']"
    edButtonURL = "//div[@class='container-fluid result-container no-selection']//div[7]//div[1]"
    dragBar = "//div[@id='mCSB_2_dragger_vertical']//div[@class='mCSB_dragger_bar']"
    dragTo = "//span[contains(text(),'©2020 Edmentum, Inc.')]"
    backButton = "//a[contains(text(),'Back to Home')]"

    userElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(userURL))
    userElement.send_keys(MY_USERNAME)

    passElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(passURL))
    passElement.send_keys(MY_PASSWORD)

    logger.debug("user/pass entered")
    # sleep(1)
    logger.debug("signing in...")

    buttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(buttonURL))
    buttonElement.click()

    edbuttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(edButtonURL))
    edbuttonElement.click()

    driver.switch_to.window(driver.window_handles[-1])  # switch to edmentum tab
    WebDriverWait(driver, 15).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'activeAssignments')))
    logger.debug("edmentum page is ready!")
    logger.debug('collecting assignments')

    assignments = getAssignments()
    assignmentSelect(assignments)

    sleep(.5)

    openCourse()

    sleep(.5)

    openTut()

    sleep(2)

    i=0
    while True:
        completeTut()
        driver.switch_to.parent_frame()
        if i == 69:
            break

main()
print("poggers")

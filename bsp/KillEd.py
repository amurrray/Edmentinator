import logging
import os
from json import loads
from pathlib import Path
from secrets import MY_PASSWORD, MY_USERNAME
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException, NoSuchFrameException
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
        # logger.debug("noOfRows: " + str(noOfRows))
        # get number of columns
        noOfColumns = len(self.table.find_elements_by_xpath("//tr[2]/th"))
        # logger.debug("noOfColumns: " + str(noOfColumns))
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
                    # logger.debug(str(thPath)+" found")
                except NoSuchElementException:
                    # logger.debug("//th not found, looking for //td")
                    ro.append(self.table.find_element_by_xpath(tdPath).text)
                    logger.debug(str(tdPath)+"found")
            # add the row data to allData of the self.table
            # logger.debug("i =" + str(i))
            allData.append(ro)

        return allData

    def presence_of_data(self, data):
        # verify the data by getting the size of the element matches based on the text/data passed
        dataSize = len(self.table.find_elements_by_xpath("//th[normalize-space(text())='"+data+"']"))
        presence = False
        if(dataSize > 0):
            presence = True
        return presence

    def get_cell_data(self, table, row_number, column_number):
        if(row_number == 0):
            raise Exception("Row number starts from 1")
        row_number = row_number+1
        cellData = table.find_element_by_xpath("//tr["+str(row_number)+"]/th["+str(column_number)+"]").text
        return cellData

def getAssignments():
    # WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//*[@id = "mCSB_2_container"]/div')) #Just to make sure page is loaded before looking for classes
    WebDriverWait(driver, 10).until(lambda driver: expected_conditions.presence_of_element_located((By.CLASS_NAME, 'assignmentName')))
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
    theEntireAlphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    theAvailableAlphabet = []

    for letter in theEntireAlphabet:
        theAvailableAlphabet.append(letter)
        if len(theAvailableAlphabet) == len(assignments):
            break
    
    i = 0
    for assignment in assignments:
        logger.debug('[' + theAvailableAlphabet[i] + '] ' + assignment['name'])
        i += 1

    while True:
        selectLet = input('Choose an assignment: ').upper()
        if selectLet in theAvailableAlphabet:
            break
        else:
            logger.debug('\n'+"Error: Invalid Character")
    selection = theAvailableAlphabet.index(selectLet) 

    logger.debug('Chose ' + assignments[selection]['name'])
    driver.get(BASE_URL + assignments[selection]['url'])

def openTut():
    # topics = driver.find_elements_by_class_name("learningPathCard") # get all assignments
    tutorialsToExpand = driver.find_elements_by_xpath("//span[contains(text(), 'of 2')]") # get just tuts

    for tutorial in tutorialsToExpand:
        tutorial.click()

    try:
        # WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text() 'of 2']"))).click()
        tutorialBtn = driver.find_element_by_xpath("//span[contains(text(), 'Tutorial')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", tutorialBtn)
        openTutBtn = WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Tutorial')]")))

    except NoSuchElementException:
        logger.debug("Tutorial Not Found")
    
    else:
        logger.debug("is tut complete?")
        try:
            driver.find_element_by_xpath("//li[@class='activity completed collapsed']")
        except NoSuchElementException:
            openTutBtn.click()
            logger.debug("Tutorial Opened")
        else:
            logger.debug("Tutorial Already Complete")
            raise SyntaxError('TutAlreadyComplete')

def completeTut():
    try:
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//header[@class='tutorial-viewport-header']"))
        logger.debug('is it disabled?')
        driver.find_element_by_xpath("//button[@class='tutorial-nav-next disabled']")

    except NoSuchElementException:
        logger.debug("nada")
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")).click()
        logger.debug("*Next*")
        sleep(.5)
        completeTut()
    else:
        logger.debug("yes")
        logger.debug("work to be done...")
        
        sleep(.5)

        isFRQ()

        isMPC()

        # isDrag()

        # ischeckboxMPC()

        isAnswerBtn()

        isFinished()

def openMasteryTest():
        try:

            masterytestBtn = driver.find_element_by_xpath("//span[contains(text(), 'Mastery Test')]")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", masterytestBtn)
            WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Mastery Test')]"))).click() 
        except NoSuchElementException:
            logger.debug("Mastery Test Not Found")
        
        else:
            logger.debug("Mastery Test Opened")

def completeMasteryTest():
    logger.debug("in completeMasterTest()")
    # startTestBtn = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='mastery-test-start']"))
    logger.debug("starting test")
    startTestBtn.click()
    logger.debug("clicked sTB")
    # reviewAnsBtnPATH = "//button[@class='mastery-test-learner-review']"
    # logger.debug("def reviewAnsBtn")
    # reviewAnsBtn = driver.find_element_by_xpath(reviewAnsBtnPATH)
    # logger.debug("clicking rab")
    # driver.execute_script("arguments[0].click();", reviewAnsBtn)
    
    # //*[contains(text(),'Nicaragua') and @style='display: none;']


def isFRQ():
    
    try:
        logger.debug('is it FRQ?')
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
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
        logger.debug("found iframes: " + str(count_arr))
        for frqFrame in count_arr:
            try:  #grabs chart answer 
                logger.debug("looking for table ans")
                try:
                    tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-5 k-table']") #gets answer table if padding is 5
                except NoSuchElementException:
                    tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-7 k-table']") #gets answer table if padding is 7

                AnswerTable = TableThings(tableAnswerElm).get_all_data()    
                logger.debug(AnswerTable)

            except NoSuchElementException:
                logger.debug("no table answer saved")
            
            try:
                driver.switch_to.frame(frqFrame)
                logger.debug("in " + frqFrame)
            except NoSuchFrameException:
                driver.switch_to.frame("responseText_ifr")
                logger.debug("Response Text iFrame")
            # try statement to figure out if it chart or not
            try:
                logger.debug("table?")
                try:
                    tableXPATH='//table[@class="ed border-on padding-5 k-table mce-item-table"]'
                    driver.find_element_by_xpath(tableXPATH)
                except NoSuchElementException:
                    tableXPATH='//table[@class="ed border-on padding-7 k-table mce-item-table"]'
                    driver.find_element_by_xpath(tableXPATH)
                logger.debug(tableXPATH)
            except NoSuchElementException:
                try:
                    logger.debug("\n" + "Not Table")
                    driver.find_element_by_xpath("//p")
                except NoSuchElementException:
                    logger.error("Cant find frq textbox or chart")
                else:
                    logger.debug("normal frq")
                    answer = driver.find_element_by_xpath("//p")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", answer)
                    answer.send_keys('.') #REPLACE WITH VAR TO ANSWER
                    logger.debug("switching frame")
                    driver.switch_to.parent_frame()
                    try:
                        logger.debug("looking for btn")
                        driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']")
                    except NoSuchElementException:
                        logger.debug("all buttons pressed, hopefully")
                    else:
                        logger.debug("found btn")
                        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
                        logger.debug("scroll to btn")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
                        submitBtnElm.click()
                        sleep(.5)
            else:
                logger.debug("yeppa")           
                tableElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(tableXPATH))
                
                # logger.debug(tableElm)
                tableElmClass = tableElm.get_attribute("class")
                logger.debug(tableElmClass)
                #What the Fuck!
                TableData = TableThings(tableElm).get_all_data()

                logger.debug("Question Table: " + str(TableData))
                try:
                    logger.debug("AnserTable: " + str(AnswerTable))
                except UnboundLocalError:
                    logger.debug("no Answer Table")
                # logger.debug(AnswerTable)

                columnNUM = TableThings(tableElm).get_column_count()
                logger.debug("# of Columns: "+str(columnNUM))
                doof = []
                logger.debug("doof: " + str(doof) )

                for _ in range(int(columnNUM)): 
                    doof.append(" ")

                logger.debug("new doof: " + str(doof))
                logger.debug(TableData[1])

                # logger.debug("is" + str(doof) + "==" + str(TableData[1]))
                # if str(doof) == str(TableData[1]):
                #     continue
                # else:
                #     logger.debug("its not equal")
                #     driver.switch_to.parent_frame()
                #     break

                rowNUM = TableData.index(doof)
                logger.debug("Row #: "+str(rowNUM + 1)) # +1 because arrays start @ 0
                

                i = 1
                for _ in range(columnNUM):
                    logger.debug("in loop")
                    tableboxPATH =  "//tr["+str(rowNUM + 2)+"]/td["+str(i)+"]" # +2 to include table header row and arrays start at 0
                    logger.debug(tableboxPATH)
                    tableboxELM = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(tableboxPATH))
                    tableboxELM.send_keys(".") #REPLACE WITH VAR TO ANSWER
                    i+=1
                driver.switch_to.parent_frame()
                logger.debug("chart complete")
            

            submittedArray = driver.find_elements_by_xpath("//button[@class='btn buttonDone' and @style='display: none;']")
            logger.debug(len(frqFrames)) 
            logger.debug(len(submittedArray))
            if len(frqFrames) == len(submittedArray): # check if we are on the last one
                break
        driver.switch_to.parent_frame()
        logger.debug("FRQ(s) Answered")

def isMPC():
    try:
        logger.debug('is it MPC?')
        # logger.debug("looking for iframe")
        driver.find_element_by_id("content-iframe")
        logger.debug("switched to i frame")
        driver.switch_to.frame("content-iframe")
        # logger.debug("looking for mpqChoices")
        driver.find_element_by_id("mcqChoices")
        # logger.debug("finished all that jont")
    except NoSuchElementException:
        logger.debug("nope")
        driver.switch_to.parent_frame()
    else:
        logger.debug("yes")
        script = driver.find_element_by_xpath("//script[contains(.,'IsCorrect')]").get_attribute("innerHTML")
        # logger.debug(script + '\n')
        scriptElmCut = script[20:-2]
        # logger.debug(scriptElmCut + '\n')
        parsedScript = loads(scriptElmCut) 
        theEntireNumabet = ['0', '1', '2', '3']
        i = 0
        for choice in parsedScript['Choices']: # this goes thru all the choices
            if choice['IsCorrect']: # if the isCorrect bool is True, then the answer is correct
                logger.debug('the answer is ' + theEntireNumabet[i])
                ans = theEntireNumabet[i]
            i += 1
            
        mpcAnsr = 'choice' + ans
        logger.debug(mpcAnsr)
        mpcBtn = "//input[@id=\'" + mpcAnsr + "\']"
        # userURL = "//input[@id='username']"
        logger.debug(mpcBtn)
        # mpcBtnElm = driver.find_element_by_xpath(mpcBtn)
        mpcBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(mpcBtn))
        mpcBtnElm.click()
        driver.switch_to.parent_frame()
        logger.debug("MPC answered")

# def isDrag():
#     try:
#         logger.debug("is it drag?")
#         driver.find_element_by_id("content-iframe")
#         driver.switch_to.frame("content-iframe")
#         logger.debug("switched to frame")
#         driver.find_elements_by_xpath('//div[@class="drop-panel"]')
#         driver.find_element_by_xpath('//div[@class="drag-panel"]')    
#     except NoSuchElementException:
#         logger.debug("nada")
#         driver.switch_to.parent_frame()
#     else:
#         logger.debug("yada")
#         submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
#         logger.debug("scroll to SubBtn")
#         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
#         logger.debug("find ans btn")
#         showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
#         showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
#         logger.debug("click ans btn")
#         driver.execute_script("arguments[0].click()", showAnsBtn)
#         logger.debug("clicked")
#         driver.execute_script("arguments[0].click()", submitBtnElm)
#         driver.switch_to.parent_frame()
#         logger.debug("drag answered")

# def ischeckboxMPC():
#     try:
#         logger.debug("is it checkbox?")
#         driver.find_element_by_id("content-iframe")
#         driver.switch_to.frame("content-iframe")
#         logger.debug("switched to frame")
#         driver.find_element_by_xpath("//input[@type='checkbox']")
#     except NoSuchElementException:
#         logger.debug("not checkbox")   
#         driver.switch_to.parent_frame() 
#     else:
#         logger.debug("it is checkbox!")
#         submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
#         logger.debug("scroll to SubBtn")
#         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
#         logger.debug("find ans btn")
#         showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
#         showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
#         logger.debug("click ans btn")
#         driver.execute_script("arguments[0].click()", showAnsBtn)
#         logger.debug("clicked")
#         driver.execute_script("arguments[0].click()", submitBtnElm)
#         driver.switch_to.parent_frame()
#         logger.debug("checkbox answered")

def isAnswerBtn():
    try:
        logger.debug("is there a answer toggle button?")
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
    except NoSuchElementException:
        logger.debug("nope")
        driver.switch_to.parent_frame()
    else:
        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        logger.debug("scroll to SubBtn")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
        logger.debug("click ans btn")
        driver.execute_script("arguments[0].click()", showAnsBtn)
        logger.debug("clicked")
        driver.execute_script("arguments[0].click()", submitBtnElm)
        driver.switch_to.parent_frame()





def isFinished():
    logger.debug("are we done?")
    # driver.switch_to.parent_frame()
    try:
        currentPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-current ng-binding']"))
        totalPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-total ng-binding']"))
    except ValueError:
        logger.debug("refreshing")
        driver.refresh()
        logger.debug("refreshed")
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//header[@class='tutorial-viewport-header']"))
        currentPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-current ng-binding']"))
        totalPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-total ng-binding']"))
    
    currentNUM = int(currentPage.text)
    totalNUM = int(totalPage.text)
    logger.debug(str(currentNUM)+" of "+str(totalNUM))
    if currentNUM == totalNUM:
        logger.debug("Tutorial Complete")
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
    logger.debug("signing in...")

    buttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(buttonURL))
    buttonElement.click()

    edbuttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(edButtonURL))
    edbuttonElement.click()

    driver.switch_to.window(driver.window_handles[-1])  # switch to edmentum tab
    WebDriverWait(driver, 15).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'activeAssignments')))
    logger.debug('collecting assignments')

    assignments = []
    while len(assignments) == 0:
        assignments = getAssignments()
        logger.debug('collecting assignments returned no assignments, retrying')
    assignmentSelect(assignments)
    # sleep(.5)

    openTut()

    # sleep(2)

    tutfinished = False

    while True:
        openTut()
        completeTut()
        driver.switch_to.parent_frame()
        if tutfinished == True:
            break

if __name__ == "__main__":
    main()

logger.debug("poggers")

import logging
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
CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/chromedriver.exe'
EXTENSION_PATH = str(Path(__file__).resolve().parents[0]) + '/8.9_0.crx'
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_extension(EXTENSION_PATH)
logger.debug('soup was here')

driver = webdriver.Chrome(CHROME_PATH, chrome_options=CHROME_OPTIONS)
driver.get("https://launchpad.classlink.com/loudoun")

userURL = "//input[@id='username']"
passURL = "//input[@id='password']"
buttonURL = "//button[@id='signin']"
edButtonURL = "//div[@class='container-fluid result-container no-selection']//div[7]//div[1]"
phyButton = "//div[@id='49021089']//a[contains(text(),'All Activities')]"
econButton = "//div[@id='49007108']//a[contains(text(),'All Activities')]"
hisButton = "//div[@id='49020693']//a[contains(text(),'All Activities')]"
engButton = "//div[@id='49021910']//a[contains(text(),'All Activities')]"
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
sleep(15) # we should really find a better way to do this but it works so eh

driver.switch_to.window(driver.window_handles[-1]) # switch to edmentum tab
logger.debug('collecting assignments')
# WebDriverWait(driver, 30).until(lambda driver: driver.find_element_by_class_name('assignment isotope-item'))
def getAssignments():
    page_source = driver.page_source
    # driver.find_element_by_class_name('assignment isotope-item')

    soup = BeautifulSoup(page_source, 'lxml')
    assignments = []
    assignment_selector = soup.find_all('div', class_='assignment isotope-item')
    for assignment_selector in assignment_selector:
        name = assignment_selector.find('div', class_='assignmentName').get_text()
        link = assignment_selector.find('a').get('href')
        assignment = {"name": name, "link": link}
        assignments.append(assignment)
    return assignments

assignments = getAssignments()

def newClassSelect(assignments):
    i = 0
    for assignment in assignments:
        logger.debug('[' + str(i) + '] ' + assignment['name'])
        i += 1
        # TODO: remove newlines in this and actually build the selector
        # essentially ill switching from your button click to a direct link open (stored in assignments) and from there your system should work with it
    logger.warn('if youre reading this aidan check my todo on line 89, also much love and muffins')

newClassSelect(assignments)

phyButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(phyButton))
econButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(econButton))
hisButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(hisButton))
engButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(engButton))
dragBarElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(dragBar))

dragToElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(dragTo))

hover = ActionChains(driver).move_to_element(dragBarElm)

def classSelect():
    while True:
        pickClass = input ("A) Physics" + '\n' + "B) Econ" + '\n' + "C) History" + '\n' + "D) English" + '\n' +"[a/b/c/d]? ")
        # check if d1a is equal to one of the strings, specified in the list
        if pickClass in ['a', 'b', 'c', 'd']:
            # if it was equal - break from the while loop
            break
    # process the input
    if pickClass == "a": 
        logger.debug("opening physics...") 
        phyButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(phyButton))
        phyButtonElm.click()
        logger.debug("opened")

    elif pickClass == "b": 
        logger.debug("opening econ...")
        econButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(econButton))
        econButtonElm.click()
        logger.debug("opened")

    elif pickClass == "c": 
        logger.debug("opening history...")
        webdriver.ActionChains(driver).drag_and_drop(dragBarElm,dragToElm).perform()
        logger.debug("scrolled")
        sleep(.5)
        hisButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(hisButton))
        hisButtonElm.click()
        logger.debug("opened")
        
    elif pickClass == "d": 
        print ("opening english...")
        webdriver.ActionChains(driver).drag_and_drop(dragBarElm,dragToElm).perform()
        print("scrolled")
        sleep(.5)
        engButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(engButton))
        engButtonElm.click()
        print("opened")
        
    logger.debug("im in")

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
            classSelect()

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
        print("nope")
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")).click()
        print("*Next*")
        sleep(.5)
        completeTut()
    else:
        print("yes")
        print("work to be done...")
        sleep(2)
  
        try:
            isFRQ()
        except NoSuchElementException:
            print("not FRQ")

        try:
            isMPC()
        except NoSuchElementException:
            print("not MPC")
        
        try:
            isFinished()
        except NoSuchElementException:
            print("not done")

        completeTut()
        
def isFRQ():
    try:
        print('is it FRQ?')
        driver.switch_to.frame("content-iframe")
        # driver.find_element_by_class_name("btn buttonDone")
        driver.find_elements_by_xpath("//button[@class='btn buttonDone']")        
    except NoSuchElementException:
        print("nope")
    else:
        print("yes")
        frameArray = driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')
        frameCount = len(frameArray)
        print(str(frameCount) + " FRQs Found")

        count_arr = [str("mce_") + str(i) + str("_ifr") for i, x in enumerate(frameArray, start=0)]

        for x in count_arr:
            driver.switch_to.frame(x)
            print("in")
            box1Elm = driver.find_element_by_id("tinymce").get_attribute("class")
            print(box1Elm)
            answer = driver.find_element_by_xpath("//p")
            answer.send_keys('.')
            driver.switch_to.parent_frame()
            print("out")
            if x == "mce_" + str(frameCount)+"_ifr":
                break

        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//button[@class='btn buttonDone']"))
        count_button = [str(i) for i, x in enumerate(submitBtnElm, start=0)]
        print(submitBtnElm)
        print(count_button)

        for x in count_button:
            print(int(x))
            int(x)
            try:
                sleep(.5)
                body = driver.find_element_by_css_selector('body')
                body.send_keys(Keys.PAGE_UP)
                actions = ActionChains(driver)
                actions.move_to_element(submitBtnElm[int(x)]).perform()
                driver.execute_script("arguments[0].scrollIntoView();", submitBtnElm[int(x)])
            except MoveTargetOutOfBoundsException:
                print("Button in view")
                sleep(1)
                submitBtnElm[int(x)].click()
                sleep(1)
            else:
                print("this shouldn't happen")
                
            if x == str(frameCount):
                break
        print("FRQ(s) Answered")

def isMPC():
    try:
        print('is it MPC?')
        driver.switch_to.frame("content-iframe")
        driver.find_element_by_id("mcqChoices")
    except NoSuchElementException:
        print("nope")
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
        mpcBtn = "\"//input[@id='" + mpcAnsr + "']\""
        print(mpcBtn)
        # mpcBtnElm = driver.find_element_by_xpath(mpcBtn)
        mpcBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//input[@id='choice2']"))
        mpcBtnElm.click()
        driver.switch_to.parent_frame()
        print("MPC answered")

def isFinished():
    try:
        print("are we done?")
        driver.switch_to.frame("content-iframe")
        congrats = "//h1[contains(text(),'Congratulations!')]"
        driver.find_element_by_xpath(congrats)
        driver.switch_to.parent_frame()
        
    except NoSuchElementException:
        print("lets hope no one ever has to see this")
    else:
        driver.find_element_by_xpath("//button[@class='tutorial-nav-exit']").click()


classSelect()

sleep(.5)

openCourse()

sleep(.5)

openTut()

sleep(2)

completeTut()

print("done")

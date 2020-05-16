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
EXTENSION_PATH = str(Path(__file__).resolve().parents[0]) + '/8.9_0.crx'
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_extension(EXTENSION_PATH)
BASE_URL = "https://f2.app.edmentum.com/"
DEBUG = True
logger.debug('soup was here')

driver = webdriver.Chrome(CHROME_PATH, options=CHROME_OPTIONS)
assignments = None # placeholder because i bad code flow

def getAssignments():
    page_source = driver.page_source
    # driver.find_element_by_class_name('assignment isotope-item')

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
    dragBar = "//div[@id='mCSB_2_dragger_vertical']//div[@class='mCSB_dragger_bar']"
    dragBarElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(dragBar)) #Just to make sure page is loaded before looking for classes
    
    theEntireAlphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    theAvailableAlphabet = []

    i = 0
    for x in theEntireAlphabet:
        theAvailableAlphabet.append(theEntireAlphabet[i])
        i += 1
        if len(theAvailableAlphabet) == len(assignments):
            break
    
    i = 0
    for assignment in assignments:
        print('[' + theAvailableAlphabet[i] + '] ' + assignment['name']) #also theres this weird bug where this sometimes doesnt go through, if you run into it too maybe a webdriverwait somehwere in the getAssignments?
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
            print("not finished")
        
def isFRQ():
    try:
        logger.debug('is it FRQ?')
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')

    except NoSuchElementException:
<<<<<<< HEAD
        logger.debug("nope")
=======
        driver.switch_to.parent_frame()
        print("nope")
>>>>>>> a71c545db5baaa7357daf3d27c06a366747e01ca
    else:
        logger.debug("yes")

        frqFrames = driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')
        logger.debug(str(len(frqFrames)) + " FRQs Found")

<<<<<<< HEAD
        count_arr = [str("mce_") + str(i) + str("_ifr") for i, frqFrame in enumerate(frqFrames, start=0)]
        for frqFrame in count_arr:
            driver.switch_to.frame(frqFrame)
            print("in")
=======
        for x in count_arr:
            driver.switch_to.frame(x)
            # print("in micro iframe")
>>>>>>> a71c545db5baaa7357daf3d27c06a366747e01ca
            box1Elm = driver.find_element_by_id("tinymce").get_attribute("class")
            # print(box1Elm)
            answer = driver.find_element_by_xpath("//p")
            answer.send_keys('.')
            driver.switch_to.parent_frame()
<<<<<<< HEAD
            print("out")
            if frqFrame == "mce_" + str(len(frqFrames)) + "_ifr": # check if we are on the last one
=======
            # print("out microiframe")
            if x == "mce_" + str(frameCount)+"_ifr":
>>>>>>> a71c545db5baaa7357daf3d27c06a366747e01ca
                break

        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//button[@class='btn buttonDone']"))
        count_button = [str(i) for i, x in enumerate(submitBtnElm, start=0)]
        # print(submitBtnElm)
        # print(count_button)

        for x in count_button:
            # print(int(x))
            int(x)
            try:
                sleep(.5)
                body = driver.find_element_by_css_selector('body')
                body.send_keys(Keys.PAGE_UP)
                actions = ActionChains(driver)
                actions.move_to_element(submitBtnElm[int(x)]).perform()
                driver.execute_script("arguments[0].scrollIntoView();", submitBtnElm[int(x)])
            except MoveTargetOutOfBoundsException:
                # print("Button in view")
                sleep(1)
                submitBtnElm[int(x)].click()
                sleep(1)
            else:
                print("this shouldn't happen")
                
            # if x == str(frameCount):
            #     break
        driver.switch_to.parent_frame()
        print("FRQ(s) Answered")

def isMPC():
    try:
        print('is it MPC?')
        print("looking for iframe")
        driver.find_element_by_id("content-iframe")
        print("switched to i frame")
        driver.switch_to.frame("content-iframe")
        print("looking for mpqChoices")
        driver.find_element_by_id("mcqChoices")
        print("finished all that jont")
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
        i = 69



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

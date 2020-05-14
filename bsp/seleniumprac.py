import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path 
from secrets import myUsername, myPassword, chromePath

chrome_options = webdriver.ChromeOptions()
extensionPath = (str(Path(__file__).resolve().parents[0]) + r'\8.9_0.crx')
chrome_options.add_extension(extensionPath)
# print(balls) # D:\CodeProjects\VisualStudio repos\BeautifulSoupPractice\bsp\seleniumprac.py\8.9_0.crx
# time.sleep(5)
print('soup was here')

driver = webdriver.Chrome(chromePath, chrome_options=chrome_options)
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
userElement.send_keys(myUsername)

passElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(passURL))
passElement.send_keys(myPassword)

buttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(buttonURL))
buttonElement.click()

edbuttonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(edButtonURL))
edbuttonElement.click()

time.sleep(15)

print('woke')

driver.switch_to.window(driver.window_handles[-1])
phyButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(phyButton))
econButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(econButton))
hisButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(hisButton))
engButtonElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(engButton))
dragBarElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(dragBar))

dragToElm = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(dragTo))

# dragToEleXOffset = dragToElm.location.get("x")
# dragToEleYOffset = dragToElm.location.get("y")


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
        print ("opening physics...") 
        phyButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(phyButton))
        phyButtonElm.click()
        print("opened")

    elif pickClass == "b": 
        print ("opening econ...")
        econButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(econButton))
        econButtonElm.click()
        print("opened")

    elif pickClass == "c": 
        print ("opening history...")
        webdriver.ActionChains(driver).drag_and_drop(dragBarElm,dragToElm).perform()
        print("scrolled")
        time.sleep(.5)
        hisButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(hisButton))
        hisButtonElm.click()
        print("opened")
        
    elif pickClass == "d": 
        print ("opening english...")
        webdriver.ActionChains(driver).drag_and_drop(dragBarElm,dragToElm).perform()
        print("scrolled")
        time.sleep(.5)
        engButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(engButton))
        engButtonElm.click()
        print("opened")
        
    print("im in")

def openCourse():
    try:
        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[text()='0 of 2']"))).click()

    except NoSuchElementException:
        print("no classes found")
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
        # //*[matches(@id, '.*Soup.*')]
        # //span[contains(text(),'The Vietnam War: Tutorial')]
    
    except NoSuchElementException:
        print("Tutorial Not Found")
    
    else:
        print("Tutorial Opened")

def completeTut():
    try:
        nextButtonElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='player-icon next']"))
        nextButtonElm.click()

    except NoSuchElementException:
        print("Work to Be Done")
    else:
        print("*Next*")
        completeTut()



classSelect()

time.sleep(.5)

openCourse()

time.sleep(.5)

openTut()
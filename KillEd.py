import logging
import os
from json import loads
from pathlib import Path
from random import randint
from secrets import MY_PASSWORD, MY_USERNAME
from time import sleep
from fuzzywuzzy import process

from lxml import etree
from bs4 import BeautifulSoup
from printy import inputy, printy
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        MoveTargetOutOfBoundsException,
                                        NoSuchElementException,
                                        NoSuchFrameException, TimeoutException)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import answers
import complimentinator
from database import checkIfSyncedUser, syncDB

# setup logging
logging.basicConfig(level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# sync db
syncDB()

# constants
if os.name == 'nt':
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/drivers/chromedriver.exe'
    logger.debug('using windows chromedriver')
else:
    CHROME_PATH = str(Path(__file__).resolve().parents[0]) + '/drivers/chromedriver'
    logger.debug('using linux chromedriver')
CLASSLINK_PATH = str(Path(__file__).resolve().parents[0]) + '/classlink.crx'
CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_extension(CLASSLINK_PATH)
BASE_URL = "https://f1.app.edmentum.com/"

try:
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=CHROME_OPTIONS)
except:
    driver = webdriver.Chrome(CHROME_PATH, options=CHROME_OPTIONS)
    logger.debug('ChromeDriverManager failed, using local binary')
actions = ActionChains(driver)
assignments = None  # placeholder because i bad code flow


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
        for webElement in row:
            rData.append(webElement.text)
        return rData

    def column_data(self, column_number):
        col = self.table.find_elements_by_xpath("//tr/th["+str(column_number)+"]")
        rData = []
        for webElement in col:
            rData.append(webElement.text)
        return rData

    def get_all_data(self):
        # get number of rows
        noOfRows = len(self.table.find_elements_by_xpath("//tr")) - 1
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
            for j in range(1, noOfColumns+1):
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
    WebDriverWait(driver, 10).until(lambda driver: expected_conditions.presence_of_element_located((By.CLASS_NAME, 'assignmentName')))
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')
    assignments = []
    assignment_selector = soup.find_all('div', class_='assignment isotope-item')
    for assignment_selector in assignment_selector:
        name = assignment_selector.find('div', class_='assignmentName').get_text()
        name = " ".join(name.splitlines())  # remove weird newlines
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
        printy(f'[n>]\[{theAvailableAlphabet[assignments.index(assignment)]}\]@ {assignment["name"]}')
        i += 1

    while True:
        selectLet = input('Choose an assignment: ').upper()
        if selectLet in theAvailableAlphabet:
            break
        else:
            printy('\nError: Invalid Character', 'r')
    selection = theAvailableAlphabet.index(selectLet)

    printy(f'Chose {assignments[selection]["name"]}', 'n')
    driver.get(BASE_URL + assignments[selection]['url'])


def openCourse():
    # find/open started unit, then if one cant be found find/open new unit
    sortInProgress = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-inprogress']"))
    sortNotMastered = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-completed-not-mastered']"))
    sortNotStarted = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-notstarted']"))
    # we are currently above the array
    sortArray = [sortInProgress, sortNotMastered, sortNotStarted]
    for sort in sortArray:
        sort.click()
        sleep(1)
        try:
            tutOpen = False
            try:
                logger.debug("looking for path 2 of x")
                coursePATH = "//span[contains(text(), '2 of ')]"
                coursesArray = WebDriverWait(driver, 1).until(lambda driver: driver.find_elements_by_xpath(coursePATH))
                for course in coursesArray:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", course)
                        course.click()
                    except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                        logger.error("wrong course")
                    else:
                        openTut()
                        tutOpen = True
                        break
                if tutOpen == False:
                    raise ElementNotInteractableException
            except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                try:
                    logger.debug("looking for path 1 of x")
                    coursePATH = "//span[contains(text(), '1 of ')]"
                    coursesArray = WebDriverWait(driver, 1).until(lambda driver: driver.find_elements_by_xpath(coursePATH))
                    for course in coursesArray:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", course)
                            course.click()
                        except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                            logger.error("wrong course")
                        else:
                            openTut()
                            tutOpen = True
                            break
                    if tutOpen == False:
                        raise ElementNotInteractableException

                except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                    try:
                        logger.debug("looking for path 0 of x")
                        coursePATH = "//span[contains(text(), '0 of ')]"
                        coursesArray = WebDriverWait(driver, 1).until(lambda driver: driver.find_elements_by_xpath(coursePATH))
                        for course in coursesArray:
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", course)
                                course.click()
                            except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                                logger.error("wrong course")
                            else:
                                openTut()
                                tutOpen = True
                                break
                        if tutOpen == False:
                            raise ElementNotInteractableException
                    except (ElementNotInteractableException, ElementClickInterceptedException, TimeoutException):
                        logger.debug("No Courses Found")

                    else:
                        logger.debug("Found Course (0 of x)")
                        break
                else:
                    logger.debug("Found Course (1 of x)")
                    break
            else:
                logger.debug("Found Course (2 of x)")
                break
        except SyntaxError:
            logger.error("if this runs imma kms")
    try:
        openCourseType2()
    except:
        pass

def openCourseType2():  
    logger.debug("in CourseType2")
    # find/open started unit, then if one cant be found find/open new unit
    sortInProgress = WebDriverWait(driver, 1).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-inprogress']"))
    sortNotMastered = WebDriverWait(driver, 1).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-completed-not-mastered']"))
    sortNotStarted = WebDriverWait(driver, 1).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-notstarted']"))
    # we are currently above the array
    sortArray = [sortInProgress, sortNotMastered,sortNotStarted]
    sleep(1)
    for sort in sortArray:
        sort.click()
        logger.debug("sorting")
        try:
            # looks for all activities
            activityArray = driver.find_elements_by_xpath("//span[@class='ico oneSheetIco']")
            for activity in activityArray:
                try: 
                    # scrolls to possible activity
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", activity)
                    activity.click()
                except (ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException):
                    # if activity can't open it tries the next one in the array
                    pass
                else:
                    logger.debug("activity opened")
                    try:
                        # sees if prgm is in Tut
                        driver.find_element_by_xpath("//h1//thspan[contains(text(), 'Tutorial')]")
                    except NoSuchElementException:
                        try:
                            # checks if prgm is in Practice
                            driver.find_element_by_xpath("//li[contains(text(), 'Practice')]")
                        except NoSuchElementException:
                            try:
                                # checks if prgm is in Test
                                driver.find_element_by_xpath("//li[contains(text(), 'Test')]")
                            except NoSuchElementException:
                                logger.error("No one should see this... Ever.")
                            else:
                                # runs complete test
                                completeMasteryTest()
                        else:
                            # runs complete prac
                            completePractice()
                    else:
                        # runs complete tut
                        completeTut()
        except:
            logger.debug("not menu type 2")
            pass

def openTut():
    try:
        tutorialBtnArray = driver.find_elements_by_xpath("//span[contains(text(), 'Tutorial')]")
        for tutorialBtn in tutorialBtnArray:
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", tutorialBtn)
                WebDriverWait(driver, 1).until(expected_conditions.element_to_be_clickable((By.ID, tutorialBtn)))
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
                logger.debug("moving on to next tut")

            else:
                print("opened tutorial")
                tutorialBtn = tutorialBtn
                break

    except NoSuchElementException:
        logger.debug("Tutorial Not Found")

    else:
        logger.debug("is tut complete?")
        try:
            try:
                logger.debug("looking for finished icon")
                WebDriverWait(driver, .5).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[@class='ico finishedBigIco']")))

            except TimeoutException:
                logger.debug("looking for expemt icon")
                WebDriverWait(driver, .5).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[@class='ico exemptBigIco]'")))
        except TimeoutException:
            tutorialBtn.click()
            logger.debug("Tutorial Opened")
        else:
            logger.debug("Tutorial Already Complete")
            try:
                # OPEN PRACTICE
                openPractice()
            except EnvironmentError:
                logger.debug('Attempting to Open Test')
                try:
                    openMasteryTest()
                except SyntaxError as err:
                    logger.error(err)

                closeCourseBtnArray = driver.find_elements_by_xpath("//span[@class='ico closeCardIco']")
                i = 0
                for closeCourseBtn in closeCourseBtnArray:
                    i += 1
                    try:
                        # is clickable?
                        closeCourseBtn.click()
                    except ElementClickInterceptedException:
                        logger.debug('closeCourseBtn not clickable')

                    else:
                        logger.debug('closeCourseBtn is clickable')
                        break

                raise ElementNotInteractableException


def completeTut():
    WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//header[@class='tutorial-viewport-header']"))
    try:
        # is navNext disabled?
        driver.switch_to.parent_frame()
        # driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")
        WebDriverWait(driver, 1).until(lambda driver: driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")).click()
        logger.debug('navNext is not disabled, moving to next')
        completeTut()

    except:
        logger.debug('navNext is disabled, work to be done..')

        isFRQ()

        isMPC()

        isMultipageSlide()

        isAnswerBtn()

        isAnswerBtn2()

        isAnswerBtn3()

        isAnswerBtn4()

        isAnswerBtn5()

        isOrderedProblemChoice()

        isFinished()

def openPractice():
    try:
        practiceBtn = driver.find_element_by_xpath("//span[contains(text(), 'Practice')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", practiceBtn)
        try:
            finsihedIconArray = driver.find_elements_by_xpath("//span[@class='ico finishedBigIco']")
        except NoSuchElementException:
            pass
        else:
            if len(finsihedIconArray) == 2:
                logger.debug("Practice Already Complete")
                raise EnvironmentError

        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Practice')]"))).click()
    except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, EnvironmentError):
        logger.debug("No Unfinished Practice Found")
        raise EnvironmentError
    else:
        completePractice()

def completePractice():
    logger.debug("completePractice()")
    while True:
        try:
            btnClicked = False
            # creates array of the end btn
            endBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-endsession']")
            for endBtn in endBtnArray:
                # cycles through to check if any work, meaning we have reached the end of the test
                try:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", endBtn)
                    endBtn.click()
                except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                    pass
                else:
                    logger.debug("end btn clicked")
                    sleep(.5)
                    # btn is clicked so it breaks and continues on
                    btnClicked = True
                    break 
            if btnClicked == False:
                raise EnvironmentError
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, EnvironmentError):
            # cant end test since theres questions to answer
            try:
                # clicks mpc option
                mpc = False
                mpcOptionArray = driver.find_elements_by_xpath("//div[@class='multichoice-choice']")
                for mpcOption in mpcOptionArray:
                    # Cycles through mpc options
                    try:
                        mpcOption.click()
                    except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException):
                        pass     
                    else:
                        mpc = True
                        break
                if mpc == False:
                    raise EnvironmentError
            except EnvironmentError:
                logger.debug("not a mpc question")
                # trys to answer dropdown question
                try:
                    dropD = False
                    driver.find_element_by_xpath("//select[@class='dropdown']")
                    dropdownArray = driver.find_elements_by_xpath("//select[@class='dropdown']")

                except NoSuchElementException:
                    try:
                        logger.debug("drag and also drop?")
                        driver.find_element_by_xpath("//div[@data-dropped='false']")
                    except NoSuchElementException:
                        logger.debug("not drag and also drop")
                        try:
                            logger.debug("frq")
                            driver.find_element_by_xpath("//input[@spellcheck='false']")
                        except NoSuchElementException:
                            logger.debug("not frq")
                            pass
                        else:
                            textbox = driver.find_element_by_xpath("//input[@spellcheck='false']")
                            textbox.click()
                            textbox.send_keys(".")
                            # submits answer
                            logger.debug("submit time")
                            subBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-submit']")
                            for subBtn in subBtnArray:        
                                # cycles through subBtns
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", subBtn)
                                    subBtn.click()
                                except:
                                    pass
                                else:
                                    break
                            try:
                                # if the answers correct (or its second failed attemt), next btn is shown and can be clicked
                                nextBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-next']")
                                for nextBtn in nextBtnArray:
                                    try:
                                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", nextBtn)
                                        nextBtn.click()
                                    except (ElementNotInteractableException, ElementClickInterceptedException):
                                        pass
                                    else:
                                        # moves onto next question
                                        break
                                # if all next btns dont work the answer wasnt correct and it tries again
                                try:
                                    retryBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-retry']")
                                    for retryBtn in retryBtnArray:
                                        try:
                                            retryBtn.click()
                                        except(NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                                            pass
                                        else:
                                            break
                                except:
                                    pass
                            except:
                                pass
                    else:
                        driver.find_element_by_xpath("//div[@data-dropped='false']")
                        try:
                            driver.find_element_by_xpath("//div[@class='droppable target ui-droppable']")
                        except NoSuchElementException:
                            try:
                                driver.find_element_by_xpath("//li[@class='droppable ui-droppable']")
                            except NoSuchElementException:
                                logger.debug("no drops found")
                                pass
                            else:
                                dropArray = driver.find_element_by_xpath("//li[@class='droppable ui-droppable']")
                        else:
                            dropArray = driver.find_elements_by_xpath("//div[@class='droppable target ui-droppable']")

                        # drags element to a droppable
                        dragArray = driver.find_elements_by_xpath("//div[@data-dropped='false']")
                        i=0
                        for dropElm in dropArray:
                            dragElm = dragArray[i]
                            ActionChains(driver).drag_and_drop(dragElm, dropElm).perform()
                            i+=1

                         # submits answer
                        logger.debug("submit time")
                        subBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-submit']")
                        for subBtn in subBtnArray:        
                            # cycles through subBtns
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", subBtn)
                                subBtn.click()
                            except:
                                pass
                            else:
                                break
                        try:
                            # if the answers correct (or its second failed attemt), next btn is shown and can be clicked
                            nextBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-next']")
                            for nextBtn in nextBtnArray:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", nextBtn)
                                    nextBtn.click()
                                except (ElementNotInteractableException, ElementClickInterceptedException):
                                    pass
                                else:
                                    # moves onto next question
                                    break
                            # if all next btns dont work the answer wasnt correct and it tries again
                            try:
                                retryBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-retry']")
                                for retryBtn in retryBtnArray:
                                    try:
                                        retryBtn.click()
                                    except(NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                                        pass
                                    else:
                                        break
                            except:
                                pass
                        except:
                            pass
                else:
                    try:
                        logger.debug("drop down")
                        for dropdown in dropdownArray:
                            try:
                                dropdown.click()
                            except (ElementNotInteractableException, ElementClickInterceptedException):
                                logger.debug("not drop down")
                            else:
                                # if box can be clicked it scrolls down and selects first choice
                                dropdown.send_keys(Keys.DOWN)
                                dropdown.send_keys(Keys.RETURN)
                                dropD = True

                        if dropD == False:
                            raise EnvironmentError
                    except EnvironmentError:
                        pass
                    else:
                        # submits answer
                        logger.debug("submit time")
                        subBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-submit']")
                        for subBtn in subBtnArray:        
                            # cycles through subBtns
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", subBtn)
                                subBtn.click()
                            except:
                                pass
                            else:
                                break
                        try:
                            # if the answers correct (or its second failed attemt), next btn is shown and can be clicked
                            nextBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-next']")
                            for nextBtn in nextBtnArray:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", nextBtn)
                                    nextBtn.click()
                                except (ElementNotInteractableException, ElementClickInterceptedException):
                                    pass
                                else:
                                    # moves onto next question
                                    break
                            # if all next btns dont work the answer wasnt correct and it tries again
                            try:
                                retryBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-retry']")
                                for retryBtn in retryBtnArray:
                                    try:
                                        retryBtn.click()
                                    except(NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                                        pass
                                    else:
                                        break
                            except:
                                pass
                        except:
                            pass   
            else:
                # submits answer
                logger.debug("submit time")
                subBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-submit']")
                for subBtn in subBtnArray:        
                    # cycles through subBtns
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", subBtn)
                        subBtn.click()
                    except:
                        pass
                    else:
                        break
                try:
                    # if the answers correct (or its second failed attemt), next btn is shown and can be clicked
                    nextBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-next']")
                    for nextBtn in nextBtnArray:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", nextBtn)
                            nextBtn.click()
                        except (ElementNotInteractableException, ElementClickInterceptedException):
                            pass
                        else:
                            # moves onto next question
                            break
                    # if all next btns dont work the answer wasnt correct and it tries again
                    try:
                        retryBtnArray = driver.find_elements_by_xpath("//a[@class='player-button worksheets-retry']")
                        for retryBtn in retryBtnArray:
                            try:
                                retryBtn.click()
                            except(NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                                pass
                            else:
                                break
                    except:
                        pass
                except:
                    pass
        else:
            # end btn was pressed,  
            logger.debug("Practice Complete")
            # finds/clicks exit btn
            WebDriverWait(driver, 10).until(driver.find_element_by_xpath("//div[@class='results-header-text']"))
            exitBtn = driver.find_element_by_xpath("//button[@title='Exit']")
            exitBtn.click()
            # finds/clicks okay btn
            okBtnElm = WebDriverWait(driver, 10).until(driver.find_element_by_xpath("//span[contains(text(), 'OK')]"))
            driver.execute_script("arguments[0].click()", okBtnElm)
            break 

def openMasteryTest():
    try:
        masterytestBtn = driver.find_element_by_xpath("//span[contains(text(), 'Mastery Test')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", masterytestBtn)
        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Mastery Test')]"))).click()
    except NoSuchElementException:
        logger.debug("Mastery Test Not Found")

    else:
        logger.debug("Mastery Test Opened")
        completeMasteryTest()


def completeMasteryTest():
    try:
        startTestBtn = WebDriverWait(driver, 2).until(lambda driver: driver.find_element_by_xpath("//button[@class='mastery-test-start']"))
    except TimeoutException:
        startTestBtn = WebDriverWait(driver, 2).until(lambda driver: driver.find_element_by_xpath("//button[@class='level-assessment-start']"))

    logger.debug("starting test")
    startTestBtn.click()
    questionCountArray = driver.find_elements_by_xpath("//li[@class='drop-menu-item']")
    questionCount = len(questionCountArray) + 1
    print("Questions: " + str(questionCount))
    for _ in range(questionCount):
        sleep(1)
        WebDriverWait(driver, 4).until(lambda driver: driver.find_element_by_xpath("//div[@class='questions-container']"))

        # from the whole page, find just the question-revelvent html
        wholePageSoup = BeautifulSoup(driver.page_source, 'lxml')
        questionContainer = wholePageSoup.find('div', {'class': 'questions-container'})
        questionSoup = BeautifulSoup(str(questionContainer), 'lxml')

        possibleQuestionElements = questionSoup.findAll('div', {'class': 'stem'})
        possibleQuestions = []

        for element in possibleQuestionElements:
            if element.text.count('?') != 0 or element.text.lower().count('which') != 0 or element.text.lower().count('what') != 0 or element.text.lower().count('who') or element.text.lower().count('match') or element.text.lower().count('select') != 0:
                logger.debug(element.text)
                possibleQuestions.append(element.text)

        question = ""
        for possibleQuestion in possibleQuestions: # if the question is spliced up, this should fix it (?)
            question += possibleQuestion

        if len(questionSoup.findAll('div', {'class': 'interactive-content'})) != 0: # if its a drag and drop
            logger.error('DRAG AND DROP IS WIP')
        elif len(questionSoup.findAll('div', {'class': 'inlinechoice-select'})) != 0: # if its a dropdown
            questionType = 'dropdown'
            query = answers.query(question, questionType)

            foundAnswer = query['answer']
            for answer in foundAnswer:
                logger.debug("dropwdown question")
                dropdownboxArray = driver.find_elements_by_xpath("//select[@class='inlinechoice-select']")
                i = 0
                for dropdown in dropdownboxArray:
                    dropdown.click()
                    dropdown.send_keys(foundAnswer[i])
                    dropdown.send_keys(Keys.ENTER)
                    i += 1

        elif len(possibleQuestions) == 0:
            logger.error("UNKOWN QUESTION TYPE")

        else: # multiple choice stuff
            if len(questionSoup.findAll('div', {'class': 'multichoice-choice'})) != 0: # multichoice format, most classes
                logger.debug('multichoice format')
                answerChoicesElement = driver.find_elements_by_class_name('multichoice-choice')
                answerChoicesText = questionSoup.findAll('div', {'class': 'multichoice-choice'})
                for i in answerChoicesText:
                    answerChoicesText[answerChoicesText.index(i)] = BeautifulSoup(str(i), 'lxml').find('div', {'class': 'content-inner hover-highlight'}).text
                logger.debug('answer choices '+ str(answerChoicesText))

            elif len(questionSoup.findAll('span', {'class': 'ht-interaction'})) != 0: # ht interaction format, usually for english
                logger.debug('ht interaction format')
                answerChoicesElement = driver.find_elements_by_class_name('ht-interaction')
                answerChoicesText = questionSoup.findAll('span', {'class': 'ht-interaction'})
                for i in answerChoicesText:
                    answerChoicesText[answerChoicesText.index(i)] = i.text.replace(' ', '+').replace("'", "\'").replace('"', '\"').replace('’', "\'")
                logger.debug('answer choices ' + str(answerChoicesText))

            answerCorrect = process.extractOne(answers.query(question, 'mcq')['answer'][0], answerChoicesText)[0] # get the answer to the question then find its closest match out of our choices
            answerChoicesElement[answerChoicesText.index(answerCorrect)].click()
            logger.debug(f'answer: {answerCorrect}')

        sleep(.5)
        nextBtn = driver.find_element_by_xpath("//a[@class='player-button worksheets-submit' and contains(text(),'Next')]")
        nextBtn.click()
        sleep(1)

    logger.debug("done with test")
    okBtn = driver.find_element_by_xpath("//span[@class='ui-button-text' and contains(text(),'OK')]")
    okBtn.click()
    WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(text(),'Close and return to your activities')]"))).click()


def BigBoyTest():
    try:
        bbTestOpen = False
        bbTestArray = driver.find_elements_by_xpath("//span[@class='ico testIco']")
        for bbTest in bbTestArray:
            try:
                print(bbTest)
                bbTest.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                logger.debug("big boy test is not clickable")
            else:
                logger.debug("big boy test is clickable")
                bbTestOpen = True
                break
        if bbTestOpen == False:
            raise SyntaxError

    except SyntaxError:
        print("No Big Tests Found")
    else:
        logger.debug("Mastery Test Opened")
        completeMasteryTest()


def isFRQ():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')

    except NoSuchElementException:
        logger.debug("is not FRQ")
    else:
        logger.debug("is FRQ")
        # use lxml to execute the xpath to see if these are fake frames
        soup = BeautifulSoup(driver.page_source, 'lxml')
        frqFramesSoup = soup.findAll('textarea', {'class': 'responseText'})
        logger.debug(str(len(frqFramesSoup)) + " FRQs Found")
        if len(frqFramesSoup) == 0:
            driver.switch_to.parent_frame()
            return
        frqFrames = driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')
    try:
        try:
            driver.find_element_by_xpath("//button[@class='btn buttonCorrectToggle' and @style='display:none;']")
        except NoSuchElementException:
            logger.debug("well fuck ig")
        else:
            showAnswerBtnArray = driver.find_elements_by_xpath("//button[@class='btn buttonCorrectToggle' and @style='display:none;']")
            for showAns in showAnswerBtnArray:
                driver.execute_script("arguments[0].click()", showAns)
    except:
        logger.debug("No show answer btns")
        pass
    try:
        logger.debug("looking for btn")
        driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']")
    except NoSuchElementException:
        logger.debug("no btns found or all buttons pressed, hopefully..")
    else:
        logger.debug("found btn")
        submitBtnElmArray = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        for submitBtnElm in submitBtnElmArray:
            logger.debug("scroll to btn")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
            driver.execute_script("arguments[0].click()", submitBtnElm)
            sleep(.5)
        driver.switch_to.parent_frame()
        logger.debug("FRQ(s) Answered")


def isMPC():
    try:
        driver.find_element_by_id("content-iframe")
        logger.debug("switched to i frame")
        driver.switch_to.frame("content-iframe")
        driver.find_element_by_id("mcqChoices")
    except NoSuchElementException:
        logger.debug("is not MPC")
        driver.switch_to.parent_frame()
    else:
        logger.debug("is MPC")
        script = driver.find_element_by_xpath("//script[contains(.,'IsCorrect')]").get_attribute("innerHTML")
        # logger.debug(script + '\n')
        scriptElmCut = script[20:-2]
        # logger.debug(scriptElmCut + '\n')
        parsedScript = loads(scriptElmCut)
        theEntireNumabet = ['0', '1', '2', '3']
        i = 0
        for choice in parsedScript['Choices']:  # this goes thru all the choices
            if choice['IsCorrect']:  # if the isCorrect bool is True, then the answer is correct
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


def isOrderedProblemChoice():
    try:
        logger.debug('is this an ordered problem choice?')
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        choices = WebDriverWait(driver, 0.5).until(lambda driver: driver.find_elements_by_class_name('orderedProblem-choice'))
        selectedChoice = choices[randint(0, (len(choices) - 1))]
        selectedChoice.click()

        # check if were done, if not loop back around and pick another random answer
        try:
            # is ordered problem disabled?
            driver.find_element_by_xpath("//button[@class='tutorial-nav-next disabled']")
        except NoSuchElementException:
            logger.debug("ordered problem not disabled, is complete")
            driver.switch_to.parent_frame()
        else:
            driver.switch_to.parent_frame()
            isOrderedProblemChoice()

    except:
        logger.debug('not an ordered problem choice')
        driver.switch_to.parent_frame()


def isDrag():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        driver.find_elements_by_xpath('//div[@class="drop-panel"]')
        driver.find_element_by_xpath('//div[@class="drag-panel"]')
    except NoSuchElementException:
        logger.debug("not a drag and drop question")
        driver.switch_to.parent_frame()
    else:
        logger.debug("is a drag and drop question")
        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        # scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
        # find ans btn
        showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.execute_script("arguments[0].click()", submitBtnElm)
        driver.switch_to.parent_frame()
        logger.debug("drag answered")


def ischeckboxMPC():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        driver.find_element_by_xpath("//input[@type='checkbox']")
    except NoSuchElementException:
        logger.debug("not checkbox")
        driver.switch_to.parent_frame()
    else:
        logger.debug("it is checkbox!")
        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        #scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
        # find ans btn
        showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.execute_script("arguments[0].click()", submitBtnElm)
        driver.switch_to.parent_frame()
        logger.debug("checkbox answered")


def isMultipageSlide():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        nextBtn = driver.find_element_by_id("sbsNext")
    except NoSuchElementException:
        logger.debug("not a multipage slide")
        driver.switch_to.parent_frame()
    else:
        logger.debug("is a multipage slide")
        driver.execute_script("arguments[0].click()", nextBtn)
        driver.switch_to.parent_frame()


def isAnswerBtn():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
    except NoSuchElementException:
        logger.debug("no answer toggle button found")
        driver.switch_to.parent_frame()
    else:
        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        # scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.execute_script("arguments[0].click()", submitBtnElm)
        driver.switch_to.parent_frame()


def isAnswerBtn2():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        showAnsBtnPATH = "//button[@id='showAnswer' and @style='display:none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
    except NoSuchElementException:
        logger.debug("answer button 2 not found")
        driver.switch_to.parent_frame()
    else:
        checkAnsBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@id='checkAnswer']"))
        # scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", checkAnsBtnElm)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.execute_script("arguments[0].click()", checkAnsBtnElm)
        driver.switch_to.parent_frame()


def isAnswerBtn3():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        showAnsBtnPATH = "//button[@class='cw-button answerButton btn btn-info' and @style='display: none;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
    except NoSuchElementException:
        logger.debug("answer button 3 not found")
        driver.switch_to.parent_frame()
    else:
        logger.debug("looking for done btn")
        try:
            foundDoneBtn = False
            checkAnsBtnElm = WebDriverWait(driver, 2).until(lambda driver: driver.find_element_by_xpath("//button[@class='cw-button cw-disabled doneButton btn btn-info']"))
        except TimeoutException:
            pass
        else:
            foundDoneBtn = True
        # scroll to SubBtn
        if foundDoneBtn == True:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", checkAnsBtnElm)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        if foundDoneBtn == True:
            driver.execute_script("arguments[0].click()", checkAnsBtnElm)
        driver.switch_to.parent_frame()


def isAnswerBtn4():
    '''
    check for answer btn using id system
    idk why theyre different
    bad coding i guess - soup
    '''
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        showAnsBtn = driver.find_element_by_id("answer")
    except NoSuchElementException:
        logger.debug("answer button 4 not found")
        driver.switch_to.parent_frame()
    else:
        logger.debug("looking for done btn")
        checkAnsBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('done'))
        # scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", checkAnsBtnElm)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.find_element_by_id('textinput').send_keys(' ')
        driver.execute_script("arguments[0].click()", checkAnsBtnElm)
        driver.switch_to.parent_frame()
        
def isAnswerBtn5():
    try:
        driver.find_element_by_id("content-iframe")
        driver.switch_to.frame("content-iframe")
        logger.debug("switched to frame")
        showAnsBtnPATH = "//button[@class='btn buttonCorrectToggle' and @style='display:none; visibility:hidden;']"
        showAnsBtn = driver.find_element_by_xpath(showAnsBtnPATH)
    except NoSuchElementException:
        logger.debug("no answer toggle button found")
        driver.switch_to.parent_frame()
    else:
        submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
        # scroll to SubBtn
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
        # click ans btn
        driver.execute_script("arguments[0].click()", showAnsBtn)
        # clicked
        driver.execute_script("arguments[0].click()", submitBtnElm)
        driver.switch_to.parent_frame()


def isFinished():
    logger.debug("are we done?")
    driver.switch_to.parent_frame()
    try:
        currentPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-current ng-binding']"))
        totalPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-total ng-binding']"))
        currentNUM = int(currentPage.text)
        totalNUM = int(totalPage.text)
        print(str(currentNUM)+" of "+str(totalNUM))
    except (NoSuchElementException, ValueError, TimeoutError):
        logger.debug("refreshing")
        driver.refresh()
        logger.debug("refreshed")
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//header[@class='tutorial-viewport-header']"))
        currentPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-current ng-binding']"))
        totalPage = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//span[@class='tutorial-nav-progress-total ng-binding']"))
        currentNUM = int(currentPage.text)
        totalNUM = int(totalPage.text)
        print(str(currentNUM)+" of "+str(totalNUM))
    
    if currentNUM == totalNUM:
        logger.debug("Tutorial Complete")
        driver.find_element_by_xpath("//button[@class='tutorial-nav-exit']").click()  # closes tutorial
        isComplete()

def isComplete():
    try:
        driver.find_element_by_xpath("//header[@id='mainHeader']")
    except:
        pass
    else:
        logger.debug('in course selection')

    openCourse()

    BigBoyTest()

    tutfinished = False

    while True:
        completeTut()
        driver.switch_to.parent_frame()
        if tutfinished == True:
            break

def main():  # this the real one bois
    driver.get("https://launchpad.classlink.com/loudoun")

    userURL = "//input[@id='username']"
    passURL = "//input[@id='password']"
    buttonURL = "//button[@id='signin']"
    edButtonURL = "//span[contains(text(), 'Edmentum')]"

    userElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(userURL))
    userElement.send_keys(MY_USERNAME)

    passElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(passURL))
    passElement.send_keys(MY_PASSWORD)

    logger.debug("user/pass entered, signing in...")

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

    isComplete()

if __name__ == "__main__":
    main()

logger.debug("poggers")

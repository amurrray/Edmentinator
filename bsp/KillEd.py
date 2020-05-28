import logging
import os
from json import loads
from pathlib import Path
from random import randint
from secrets import MY_PASSWORD, MY_USERNAME
from time import sleep
from printy import printy, inputy

from bs4 import BeautifulSoup
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

import answers, complimentinator

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

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
BASE_URL = "https://f2.app.edmentum.com/"

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
    sortNotStarted = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-notstarted']"))
    # we are currently above the array
    sortArray = [sortInProgress, sortNotStarted]
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
    sortInProgress = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-inprogress']"))
    sortNotStarted = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//li[@id='tab-notstarted']"))
    # we are currently above the array
    sortArray = [sortInProgress, sortNotStarted]
    for sort in sortArray:
        sort.click()
        logger.debug("sorting")
        sleep(1)
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
    try:
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//header[@class='tutorial-viewport-header']"))
        # is navNext disabled?
        driver.find_element_by_xpath("//button[@class='tutorial-nav-next disabled']")

    except NoSuchElementException:
        logger.debug('navNext is not disabled, moving to next')
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath("//button[@class='tutorial-nav-next']")).click()
        sleep(.5)
        completeTut()
    else:
        logger.debug('navNext is disabled, work to be done..')

        sleep(.5)

        isFRQ()

        isMPC()

        # isDrag()

        # ischeckboxMPC()
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
                    dropdownArray = driver.find_elements_by_xpath("//select")
                    logger.debug("drop down")
                    for dropdown in dropdownArray:
                        try:
                            dropdown.click()
                        except (ElementNotInteractableException, ElementClickInterceptedException):
                            pass
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
            exitBtn = driver.find_element_by_xpath("//button[@title='Exit']")
            exitBtn.click()
            # finds/clicks okay btn
            okBtnElm = WebDriverWait(driver, 10).until(driver.find_element_by_xpath("//span[contains(text(), 'OK')]"))
            okBtnElm.click()
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
        startTestBtn = WebDriverWait(driver, .5).until(lambda driver: driver.find_element_by_xpath("//button[@class='mastery-test-start']"))
    except TimeoutException:
        startTestBtn = WebDriverWait(driver, .5).until(lambda driver: driver.find_element_by_xpath("//button[@class='level-assessment-start']"))

    logger.debug("starting test")
    startTestBtn.click()
    sleep(.5)
    questionCountArray = driver.find_elements_by_xpath("//li[@class='drop-menu-item']")
    questionCount = len(questionCountArray) + 1
    print("Questions: " + str(questionCount))
    for _ in range(questionCount):
        queryArray = []
        # answerArray=[]
        print("line 1 time")
        isDropdown = False
        sleep(.5)
        try:
            # searches for //em and //thespan within the two //div layers. (if both are found its a cut up sentence)
            driver.find_element_by_xpath("//div[@class='stem']//div[@class='content-wrapper']//thspan")
            driver.find_element_by_xpath("//div[@class='stem']//div[@class='content-wrapper']//em")
            # creates array of all elements in the layer
            cutQueryArray = driver.find_elements_by_xpath("//div[@class='stem']//div[@class='content-wrapper']//*")     
        except NoSuchElementException:
            try:
                cutQueryArray = driver.find_elements_by_xpath("//div[@class='stem']//div//thspan")
            except NoSuchElementException:
                try:
                    line1 = driver.find_element_by_xpath("//div[@class='stem']//p/span").text
                except NoSuchElementException:
                    try:
                        line1 = driver.find_element_by_xpath("//div[@class='stem']//div/thspan").text
                    except NoSuchElementException:
                        try:
                            line1 = driver.find_element_by_xpath("//div[@class='stem']/div//p").text
                        except NoSuchElementException:
                            try:
                                line1DD = driver.find_elements_by_xpath("//div[@class='inline-choice-content interactive-content-block']/thspan").text
                            except NoSuchElementException:
                                logger.debug("No Questions Found")
                            else:
                                logger.debug("question type 5 found")
                                logger.debug("!drop down select type!")
                                isDropdown = True
                        else:
                            logger.debug("question type 4 found")
                    else:
                        logger.debug("question type 3 found")
                else:
                    logger.debug("question type 2 found")
            else:
                logger.debug("question type 1 found (cut up text type 2)")
                # combines all the text into a str var
                line1 = ""
                for cutQuery in cutQueryArray:
                    line1 += cutQuery.text
        else:
            line1 = ""
            logger.debug("cut up text found")
            # combines all the text into a str var
            for cutQuery in cutQueryArray:
                line1 += cutQuery.text

        if isDropdown == True:
            dropdownline = ' '.join([str(elem) for elem in line1DD]) 
            queryArray.append(dropdownline)
        else:
            # logger.debug("not drop down")
            queryArray.append(line1)

        # try:
        #     restArray = driver.find_elements_by_xpath("//div[@class='stem']//p/thspan")
        # except NoSuchElementException:
        #     print("no rest")
        # else:
        #     for rest in restArray:
        #         newRest = rest.text
        #         queryArray.append(newRest)
        #         print(rest)

        print(queryArray)
        queryStr = ''.join(queryArray)
        query = answers.query(queryStr)

        foundAnswer = query['answer']

        # while True:
        # finalAnswerOptionsArray = []
        # try:
        #     answerOptionsArray = driver.find_elements_by_xpath("//div[@class='content-inner hover-highlight']/thspan") #normal mpc
        #     print("mpc 1")
        #     print(answerOptionsArray)
        #     for answerOption in answerOptionsArray:
        #         print(answerOption)
        #         newAnswerOption = answerOption.text
        #         finalAnswerOptionsArray.append(newAnswerOption)
        # except NoSuchElementException:
        #     try:
        #         answerOptionsArray = driver.find_element_by_xpath("//div[@class='content-inner hover-highlight']").text #noraml mpc type 2
        #         print("mpc 2")
        #         for answerOption in answerOptionsArray:
        #             newAnswerOption = answerOption.text
        #             finalAnswerOptionsArray.append(newAnswerOption)
        #     except NoSuchElementException:
        #         try:
        #             answerOptionsArray = driver.find_elements_by_xpath("//ul[@class='multiresponse-choiceslist']//li//label").text #all that apply
        #             print("mpc 3")
        #             for answerOption in answerOptionsArray:
        #                 newAnswerOption = answerOption.text
        #                 finalAnswerOptionsArray.append(newAnswerOption)
        #         except NoSuchElementException:
        #             try:
        #                 answerOptionsArray = driver.find_elements_by_xpath("//ul[@class='multiresponse-choiceslist']//li//label").text #all that apply
        #                 print("mpc 4")
        #                 for answerOption in answerOptionsArray:
        #                     newAnswerOption = answerOption.text
        #                     finalAnswerOptionsArray.append(newAnswerOption)
        #             except NoSuchElementException:
        #                 try:
        #                     print("mpc 5")
        #                     answerOptionsArray = driver.find_element_by_xpath("//span[@class='ht-interaction']//span[@class='hottext-mc-span hottext-mc-unselected']").text #select text)
        #                     for answerOption in answerOptionsArray:
        #                         newAnswerOption = answerOption.text
        #                         finalAnswerOptionsArray.append(newAnswerOption)
        #                 except:
        #                     print("actually wtf ed")

        # answerArray.append(finalAnswerOptionsArray)
        # print(answerArray)
        print(foundAnswer)
        for answer in foundAnswer:
            try:
                # logger.debug("//*[contains(text(),'" + str(answer) + "')]")
                answerChoice = driver.find_element_by_xpath("//*[contains(text(),'" + str(answer) + "')]")
                if isDropdown == True:
                    logger.debug("dropwdown question")
                    dropdownboxArray = driver.find_elements_by_xpath("//select[@class='inlinechoice-select']")
                    i = 0
                    for dropdown in dropdownboxArray:
                        dropdown.click()
                        dropdown.send_keys(foundAnswer[i])
                        dropdown.send_keys(Keys.ENTER)
                        i += 1
                else:
                    driver.execute_script("arguments[0].click()", answerChoice)

            except NoSuchElementException:
                logger.debug("ans not available")
                try:
                    # splits answer up word for word
                    splitAnsArray = str(answer).split()
                    for word in splitAnsArray:
                        try:
                            answerChoice = driver.find_element_by_xpath("//*[contains(text(),'" + str(word) + "')]")
                        except:
                            pass
                        else:
                            logger.debug("answer found through split")
                            driver.execute_script("arguments[0].click()", answerChoice)
                            break
                except:
                    logger.debug("answer still not found")
                    # possibly drag/drop of input
                    # try:

        sleep(.5)
        nextBtn = driver.find_element_by_xpath("//a[@class='player-button worksheets-submit' and contains(text(),'Next')]")
        nextBtn.click()
        sleep(1)
    logger.debug("done with test")
    okBtn = driver.find_element_by_xpath("//span[@class='ui-button-text' and contains(text(),'OK')]")
    okBtn.click()
    closeBtn = driver.find_element_by_xpath("//button[@type='button' and contains(text(),'Close and return to your activities')]")
    ActionChains(driver).move_to_element(closeBtn).perform()
    sleep(5)
    closeBtn.click()
    # closeBtn.click()
    # driver.execute_script("arguments[0].click()", closeBtn)

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
        frqFrames = driver.find_elements_by_xpath('//*[@title="Rich Text Area. Press ALT-F9 for menu. Press ALT-F10 for toolbar. Press ALT-0 for help"]')
        logger.debug(str(len(frqFrames)) + " FRQs Found")
        if len(frqFrames) == 0:
            driver.switch_to.parent_frame()
            return

        count_arr = [str("mce_") + str(i) + str("_ifr") for i, frqFrame in enumerate(frqFrames, start=0)]
        logger.debug("found iframes: " + str(count_arr))  
        
        # shows answers for items not in iframe
        try:
            driver.find_element_by_xpath("//button[@class='btn buttonCorrectToggle' and @style='display:none;']")
        except NoSuchElementException:
            logger.debug("well fuck ig")
            pass
        else:
            logger.debug("okay good")
            showAnswerBtnArray = driver.find_elements_by_xpath("//button[@class='btn buttonCorrectToggle' and @style='display:none;']")
            for showAns in showAnswerBtnArray:
                logger.debug("in for")
                driver.execute_script("arguments[0].click()", showAns)
                submitBtnElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//button[@class='btn buttonDone' and @style='']"))
                logger.debug("scroll to btn")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", submitBtnElm)
                WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//button[@class='btn buttonDone' and @style='']")))
                driver.execute_script("arguments[0].click()", submitBtnElm)

        for frqFrame in count_arr:
            try:  # grabs chart answer
                logger.debug("looking for table ans")
                try:
                    try:
                        arrayAnswerBtn = driver.find_element_by_xpath("//button[@class='buttonExplanationToggle' and @style='display:none;']")
                        driver.execute_script("arguments[0].click()", arrayAnswerBtn)
                    except NoSuchElementException:
                        logger.debug("Cant find show answers btn")

                    tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-5 k-table']")  # gets answer table if padding is 5
                except NoSuchElementException:
                    try:
                        tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-7 k-table']")  # gets answer table if padding is 7
                    except NoSuchElementException:
                        try:
                            tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-5 k-table bgc-gray-lighter']")
                        except NoSuchElementException:
                            tableAnswerElm = driver.find_element_by_xpath("//table[@class='ed border-on padding-7 k-table bgc-gray-lighter']")

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
                    tableXPATH = '//table[@class="ed border-on padding-5 k-table mce-item-table"]'
                    driver.find_element_by_xpath(tableXPATH)
                except NoSuchElementException:
                    tableXPATH = '//table[@class="ed border-on padding-7 k-table mce-item-table"]'
                    driver.find_element_by_xpath(tableXPATH)
                logger.debug(tableXPATH)
            except NoSuchElementException:
                try:
                    logger.debug("Not Table")
                    driver.find_element_by_xpath("//p")
                except NoSuchElementException:
                    logger.error("Cant find frq textbox or chart")
                else:
                    logger.debug("normal frq")
                    answer = driver.find_element_by_xpath("//p")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center' });", answer)
                    # if its a self evaluation, use zeks complimentinator script
                    driver.switch_to.parent_frame()
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    selfEval = soup.find_all(text='How did you do?')
                    driver.switch_to.frame(frqFrame)
                    if len(selfEval) != 0 and count_arr.index(frqFrame) == len(count_arr) - 1: # if we on the last frq frame and its a selfeval
                        answer.send_keys(str(complimentinator.generateSentence()))
                    else:
                        answer.send_keys('.')  # REPLACE WITH VAR TO ANSWER
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
                        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, "//button[@class='btn buttonDone' and @style='']")))
                        submitBtnElm.click()
                        sleep(.5)
            else:
                logger.debug("yeppa")
                tableElm = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(tableXPATH))

                # logger.debug(tableElm)
                tableElmClass = tableElm.get_attribute("class")
                logger.debug(tableElmClass)
                # What the Fuck!
                TableData = TableThings(tableElm).get_all_data()

                logger.debug("Question Table: " + str(TableData))
                try:
                    logger.debug("AnswerTable: " + str(AnswerTable))
                    for x in AnswerTable:
                        for y in x:
                            print(y, end=' ')
                        print()
                except UnboundLocalError:
                    logger.debug("no Answer Table")
                # logger.debug(AnswerTable)

                columnNUM = TableThings(tableElm).get_column_count()
                logger.debug("# of Columns: "+str(columnNUM))
                doof = []
                logger.debug("doof: " + str(doof))

                for _ in range(int(columnNUM)):
                    doof.append(" ")

                for x in doof:
                    for y in x:
                        print(y, end=' ')
                    print()

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
                logger.debug("Row #: "+str(rowNUM + 1))  # +1 because arrays start @ 0

                i = 1
                for _ in range(columnNUM):
                    logger.debug("in loop")
                    tableboxPATH = "//tr["+str(rowNUM + 2)+"]/td["+str(i)+"]"  # +2 to include table header row and arrays start at 0
                    logger.debug(tableboxPATH)
                    tableboxELM = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(tableboxPATH))
                    tableboxELM.send_keys(".")  # REPLACE WITH VAR TO ANSWER
                    i += 1
                driver.switch_to.parent_frame()
                logger.debug("chart complete")

            submittedArray = driver.find_elements_by_xpath("//button[@class='btn buttonDone' and @style='display: none;']")
            logger.debug(len(frqFrames))
            logger.debug(len(submittedArray))
            if len(frqFrames) == len(submittedArray):  # check if we are on the last one
                break
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
    except (NoSuchElementException, ValueError):
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
    except NoSuchElementException:
        pass
    else:
        logger.debug('in course selection')
    doShit()


def doShit():

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
    edButtonURL = "//div[@class='container-fluid result-container no-selection']//div[7]//div[1]"

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

    doShit()

if __name__ == "__main__":
    main()

logger.debug("poggers")

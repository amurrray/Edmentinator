'''
this is a simple interface for getting answers to questions
since brainly uses javascript to render their search page,
and datadome does a pretty good job of blocking headless browsers,
im just going to leave it using manual input for answers for now.
all you really have to do is click the link and copy paste, so its not
too bad, and plus my original solution had you copying the datadome cookie
from a real browser to the cli anyway, so was never fully automatic
im sure theres a better way but this works for now.
'''

import logging
import pickle
from pathlib import Path

from fuzzywuzzy import process
from printy import inputy

from database import syncDB, sanitize

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('answers')
logger.setLevel(logging.INFO)

# constants
BASE_URL = "https://brainly.com/"
DEBUG = True

try:
    pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
except FileNotFoundError:
    pickle.dump([], open('answers.pkl', 'wb'))

def query(question, questionType, draggables=None, specificness=95):
    '''
    returns an object in the format {'question': question, 'answer': answer}
    if the answer is not found in the database, manual input of the answer
    is required. click on the url in the terminal and paste the answer
    into the input

    i know specificness is dumb. thats why i used it.
    specificness is on a scale from 0 to 100, 0 being everything matches and 100 being only exact matches

    example call: print(query('who was thomas jefferson')['answer'])
    '''
    answersDB = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))

    # generate list of all known questions
    logger.debug(answersDB)
    knownQuestions = []  # perhaps implement stop word filtering later on: https://en.wikipedia.org/wiki/Stop_words
    for answer in answersDB:
        knownQuestions.append(answer['question'])

    # find the closest match to our question
    foundQuestion = process.extractOne(question, knownQuestions)
    logger.debug(f'found question:  {foundQuestion[0]}, with confidence {str(foundQuestion[1])}')

    if foundQuestion[1] < specificness: # if the found question wasnt close enough to our question, get the answer to our question
        # generate question url so that the user can get datadome key
        question = sanitize(question)
        question = question.replace(' ', '+')
        questionUrl = f'{BASE_URL}app/ask?entry=top&q={question}'

        # make the request look like it came from a user browser EDIT: it now does come from a fkin user browser
        print(questionUrl)
        print('\n')
        answersBrainly = []
        
        if questionType == 'drag':
            for drag in draggables:
                match = inputy(f'[g]\[press enter when finished]@ [n] {drag} matches to : ')
                answerCurrent = {'drag': drag, 'match': match}
                answersBrainly.append(answerCurrent)
            
        else: # most question types
            moreAns = True
            while moreAns:
                answerCurrent = inputy(f'[g]\[press enter when finished]@ [n]answer #{len(answersBrainly)}: ')
                if answerCurrent == '':
                    moreAns = False
                else:
                    answersBrainly.append(answerCurrent)

        confirm = inputy(f'CONFIRM that the answers TO [c]{question}@ ARE [n]{str(answersBrainly)}@? \[[n]Y@/[r]n@] ')
        if confirm.lower() != 'n':
            answersDB.append({'question': question, 'questionType': questionType, 'answer': answersBrainly})
            pickle.dump(answersDB, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))
            return {'question': question, 'questionType': questionType, 'answer': answersBrainly}
        else:
            return query(question, questionType, draggables)

    else:
        for answer in answersDB:
            if foundQuestion[0] == answer['question']:
                return {'question': answer['question'], 'answer': answer['answer']}

def addDragAnswer(question, dragBoxes, dragBoxAnswers):
    '''
    inserts a drag and drop question answer to the database
    dragBoxes is a list of ids of the dragndrop boxes
    dragBoxAnswers is a list of the ids of the locations the aforementioned boxes must go to
    this is all kinda open ended so its up to you how you handle it aidan, to retrieve you can just use query
    example return of a drag question
    {'question': question, 'questionType': 'drag', 'answer': {'dragBoxes': dragBoxes, 'dragBoxAnswers': dragBoxAnswers}}
    '''
    answersDB = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
    answersDB.append({'question': question, 'questionType': 'drag', 'answer': {'dragBoxes': dragBoxes, 'dragBoxAnswers': dragBoxAnswers}})
    pickle.dump(answersDB, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))

if __name__ == "__main__":
    print(query(input('question: '), 'mcq')['answer'])

import logging
import pickle
from pathlib import Path

from fuzzywuzzy import fuzz, process
from printy import printy, inputy

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

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('answers')
logger.setLevel(logging.DEBUG)

# constants
BASE_URL = "https://brainly.com/"
DEBUG = True

# pickle.dump([{'question': 'where was george washington born', 'answer': 'westmoreland country virginia va'}], open('answers.pkl', 'wb'))

def query(question, specificness=90):
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
    logger.debug('all known questions:' + str(knownQuestions))

    # find the closest match to our question
    foundQuestion = process.extractOne(question, knownQuestions)
    print('\n')
    logger.debug('found question: ' + foundQuestion[0] + ', with confidence ' + str(foundQuestion[1]))

    if foundQuestion[1] < specificness: # if the found question wasnt close enough to our question, get the answer to our question
        # generate question url so that the user can get datadome key
        questionUrl = BASE_URL + 'app/ask?entry=top&q=' + question.replace(' ', '+')

        # make the request look like it came from a user browser EDIT: it now does come from a fkin user browser
        print(questionUrl)
        print('\n')

        answersBrainly = []
        moreAns = True
        while moreAns:
            answerCurrent = inputy(f'[g]\[press enter when finished]@ [n]answer #{len(answersBrainly)}: ')
            if answerCurrent == '':
                moreAns = False
            else:
                answersBrainly.append(answerCurrent)

        confirm = inputy(f'CONFIRM that the answers TO [c]{question}@ ARE [n]{str(answersBrainly)}@? \[[n]y@/[r]n@] ')
        if confirm.lower() == 'y':
            answersDB.append({'question': question, 'answer': str(answersBrainly)})
            pickle.dump(answersDB, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))
            return {'question': question, 'answer': str(answersBrainly)}
        else:
            return query(question)
            
    else:
        for answer in answersDB:
            if foundQuestion[0] == answer['question']:
                return {'question': answer['question'], 'answer': answer['answer']}

def pickAnswer(question, choices):
    '''
    answers must be a list of all the choices
    example call: print(pickAnswer('who was benjamin fanklin', ['thommy dad', 'beny boy']))
    '''
    answer = query(question)['answer']
    answerCorrect = process.extractOne(answer, choices)[0]
    return choices.index(answerCorrect)

if __name__ == "__main__":
    # print(query(input('question: '))['answer'])
    print(query(input('ee')))

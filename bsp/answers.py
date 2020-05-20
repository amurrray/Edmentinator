import logging
import pickle
from pathlib import Path

from fuzzywuzzy import fuzz, process

# setup logging
logging.basicConfig(level=logging.INFO, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('main')
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
    
    answersDB = pickle.load(open('answers.pkl', 'rb'))

    # generate list of all known questions
    logger.debug(answersDB)
    knownQuestions = []  # perhaps implement stop word filtering later on: https://en.wikipedia.org/wiki/Stop_words
    for answer in answersDB:
        knownQuestions.append(answer['question'])
    logger.debug('all known questions:' + str(knownQuestions))

    # find the closest match to our question
    foundQuestion = process.extractOne(question, knownQuestions)
    logger.debug('found question: ' + foundQuestion[0] + ', with confidence ' + str(foundQuestion[1]))

    if foundQuestion[1] < specificness: # if the found question wasnt close enough to our question, get the answer to our question
        # generate question url so that the user can get datadome key
        questionUrl = BASE_URL + 'app/ask?entry=top&q=' + question.replace(' ', '+')

        # make the request look like it came from a user browser EDIT: it now does come from a fkin user browser
        print(questionUrl)
        answerBrainly = input('answer: ')

        confirm = input('CONFIRM that the answer TO ' + question + ' IS ' + answerBrainly + '? [y/n] ')
        if confirm.lower() == 'y':
            answersDB.append({'question': question, 'answer': answerBrainly})
            pickle.dump(answersDB, open('answers.pkl', 'wb'))
            return {'question': question, 'answer': answerBrainly}
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
    print(query('who was thomas jefferson')['answer'])
    print(pickAnswer('who was benjamin fanklin', ['thommy dad', 'beny boy']))

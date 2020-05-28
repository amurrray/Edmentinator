import argparse
import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from shutil import copyfile

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from printy import inputy, printy

# setup logging
logging.basicConfig(level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('database')

# json credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
gc = gspread.authorize(credentials)

sheet = gc.open_by_key('1n5bKrLVK1VbQ-50wzCIGxH8wWloVQZAwLU7RSCnLsko').sheet1

# setup argparser
parser = argparse.ArgumentParser(description='edmentinator database management script')
parser.add_argument('-i', '--importd', help='imports the database from json file', action='store_true')
parser.add_argument('-e', '--export', help='exports the database to json file', action='store_true')
parser.add_argument('-s', '--sync', help='syncs with other members of the edmentinator network', action='store_true')

try:
    pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
except FileNotFoundError:
    pickle.dump([], open('answers.pkl', 'wb'))


def nextAvailableRow(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

def importFromJson():
    ''' imports db from json file '''
    answers = json.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'r'))
    copyfile(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', str(Path(__file__).resolve().parents[0]) + '/answers.BACKUP.pkl')
    printy('database backed up to answers.BACKUP.pkl', 'g')
    pickle.dump(answers, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))
    printy('answers imported to answers.pkl', 'n')

def exportToJson():
    ''' exports db to json file '''
    db = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
    json.dump(db, open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'w'))
    printy('answers exported to answers.json', 'n')

def syncDB(onlyReturnDiff=False):
    answersDB = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
    sheetList = sheet.get_all_values()[1:]

    # to measure our success later
    initAnswerDBLen = len(answersDB)
    initSheetLen = len(sheetList)

    if onlyReturnDiff: # if we're only giving the caller back what we found just dont run the rest of the function
        if initSheetLen != initAnswerDBLen:
            diff = True
        else:
            diff = False
        return {'sheet': initSheetLen, 'localDB': initAnswerDBLen, 'diff': diff}

    # build a list of all known questions for each the sheet and local db
    knownQuestionsLocal = []
    knownQuestionsSheet = []
    for answer in answersDB:
        knownQuestionsLocal.append(answer['question'])

    # download from sheet stuff
    for entry in sheetList: # iterate through the sheet and make sure we have all the answers on the sheet locally
        knownQuestionsSheet.append(entry[1])
        if entry[1] not in knownQuestionsLocal:
            answersDB.append({'question': entry[1], 'questionType': entry[2], 'answer': entry[3]})
            logger.debug(f'added {entry[1]} to local db')

    if initAnswerDBLen != len(answersDB):
        printy(f'successfully added {len(answersDB) - initAnswerDBLen} entries to the local db!', 'n')
        pickle.dump(answersDB, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))
    
    # upload to sheet stuff
    next_row = nextAvailableRow(sheet)
    queuedToUpload = []
    values = []

    for knownQuestionLocal in knownQuestionsLocal: # iterate through our local db and make sure we have all our local answers up on the sheet
        if knownQuestionLocal not in knownQuestionsSheet:
            # get our local entry from db
            answerLocal = answersDB[knownQuestionsLocal.index(knownQuestionLocal)]

            # some of our older answers dont have an questionType, but they're all mcq so its ez pz
            try:
                answerLocal['questionType']
            except KeyError:
                answerLocal['questionType'] = 'mcq'

            # throw our answer in the list to be uploaded to the sheet
            thisValueAdded = [
                datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                answerLocal['question'],
                answerLocal['questionType'],
                str(answerLocal['answer'])
            ]
            values.append(thisValueAdded)
            logger.debug(f'queued {answerLocal["question"][:69]}.. to be uploaded to sheet')

    if len(values) > 0:
        valueRange = f'A{str(next_row)}:D{str(int(next_row) + len(values) - 1)}' # basically this looks at our next available row and the total length to get the 'block' of cells we are uploading to, ie if its a 4x4 block in an empty sheet it'd be A1:D4
        queuedToUpload = {'range': valueRange, 'values': values}
        sheet.batch_update([queuedToUpload])
        printy(f'successfully uploaded {len(sheetList) + len(values) - initSheetLen} entries to the sheet!', 'n')

def checkIfSyncedUser():
    syncDiff = syncDB(onlyReturnDiff=True)
    if syncDiff['diff']:  # if we detect a difference between the sheet and our local db
        sel = inputy(f'local database has {syncDiff["localDB"]} entries, while sheet has {syncDiff["sheet"]} entries. sync with sheet? \[Y/n\]', 'r>')
        if sel.lower() != 'n':
            syncDB()

def main():
    args = parser.parse_args()

    if args.importd:
        importFromJson()
    elif args.export:
        exportToJson()
    elif args.sync:
        syncDB()
    else:
        dbLen = str(len(pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))))
        answersLen = str(len(json.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'r'))))

        # if we detect a difference in the db's, ask if user wants to sync
        checkIfSyncedUser()
        
        # json/db stuff
        printy(f'local database has {dbLen} answers', 'p')
        printy(f'json has {answersLen} answers', 'o')
        print('')

        sel = inputy('[o]import@ database from json or [p]export@ database to json? \[[o]i@/[p]e@]').lower()
        if sel == 'i':
            printy('importing..', 'o')
            importFromJson()
        elif sel == 'e':
            printy('exporting..', 'p')
            exportToJson()
    

if __name__ == '__main__':
    main()

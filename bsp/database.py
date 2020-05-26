import logging
import pickle
import json

from pathlib import Path
from shutil import copyfile
from printy import printy, inputy

# setup logging
logging.basicConfig(level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('database')

try:
    pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
except FileNotFoundError:
    pickle.dump([], open('answers.pkl', 'wb'))

def importFromJson():
    answers = json.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'r'))
    copyfile(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', str(Path(__file__).resolve().parents[0]) + '/answers.BACKUP.pkl')
    print('database backed up to answers.BACKUP.pkl')
    pickle.dump(answers, open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'wb'))
    print('answers imported to answers.pkl')

def exportToJson():
    db = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
    json.dump(db, open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'w'))
    print('answers exported to answers.json')

def main():
    dbLen = str(len(pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))))
    answersLen = str(len(json.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.json', 'r'))))

    printy('local database has ' + dbLen + ' answers', 'p')
    printy('json has ' + answersLen + ' answers', 'n')
    print('')

    sel = inputy('[n]import@ database from json or [p]export@ database to json? \[[n]i@/[p]e@]').lower()
    if sel == 'i':
        printy('importing..', 'n')
        importFromJson()
    elif sel == 'e':
        printy('exporting..', 'p')
        exportToJson()
    

if __name__ == '__main__':
    main()

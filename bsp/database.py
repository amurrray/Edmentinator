import logging
import pickle
import json
import argparse

from pathlib import Path
from shutil import copyfile
from printy import printy, inputy

# setup logging
logging.basicConfig(level=logging.DEBUG, format=('%(asctime)s %(levelname)s %(name)s | %(message)s'))
logger = logging.getLogger('database')

parser = argparse.ArgumentParser(description='edmentinator database management script')
parser.add_argument('-i', '--importd', help='imports the database from json file', action='store_true')
parser.add_argument('-e', '--export', help='exports the database to json file', action='store_true')
parser.add_argument('-s', '--sync', help='syncs with other members of the edmentinator network', action='store_true')

try:
    pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/answers.pkl', 'rb'))
except FileNotFoundError:
    pickle.dump([], open('answers.pkl', 'wb'))

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

def syncDB():
    pass

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

        printy(f'local database has {dbLen} answers', 'p')
        printy(f'json has {answersLen} answers', 'o')
        print('')

        sel = inputy('[n]import@ database from json or [p]export@ database to json? \[[n]i@/[p]e@]').lower()
        if sel == 'i':
            printy('importing..', 'o')
            importFromJson()
        elif sel == 'e':
            printy('exporting..', 'p')
            exportToJson()
    

if __name__ == '__main__':
    main()

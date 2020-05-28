import random

''' written by TongueDaddy aka zekk :)) ''' 

def generateSentence():
    # all the words unfilitered
    verbs = [{'word': 'think', 'sentsAllowed': ['sentence_1']}, {'word': 'believe', 'sentsAllowed': ['sentence_1']}, {'word': 'happy', 'sentsAllowed': ['setence_2']}, {'word': 'pleased', 'sentsAllowed': ['sentence_2']}]
    past_tents = [{'word': 'did', 'sentsAllowed': ['sentence_1']}, {'word': 'have done', 'sentsAllowed': ['sentence_1']}, {'word': 'with', 'sentsAllowed': ['sentence_2']}]
    superlative = [{'word': 'good', 'sentsAllowed': ['sentence_1', 'sentence_3']}, {'word': 'well', 'sentsAllowed': ['sentence_1', 'sentence_3']}, {'word': 'pretty well', 'sentsAllowed': ['sentence_1','sentence_3']}, {'word': 'pleased', 'sentsAllowed': ['sentence_3']}]
    after_comma = [{'word': 'this time', 'sentsAllowed': ['sentence_1']}, {'word': 'here', 'sentsAllowed': ['sentence_1']}]
    nouns = [{'word': 'assignment', 'sentsAllowed': ['sentence_2']}, {'word': 'one', 'sentsAllowed': ['sentence_2']}, {'word': 'here', 'sentsAllowed': ['sentence_2']}]

    # setting up for the allowed words
    allowed_verbs = []
    allowed_past_tents = []
    allowed_superlative = []
    allowed_after_comma = []
    allowed_nouns = []

    theEntireDictionary = [verbs, past_tents, superlative, after_comma, nouns]
    theNewDictionary = [allowed_verbs, allowed_past_tents, allowed_superlative, allowed_after_comma, allowed_nouns] # a dictionary of the allowed words

    sents = ['sentence_1', 'sentence_2', 'sentence_3']
    chosenSent = random.choice(sents)

    # iterate through all the wordTypes, and all the words in the word types, to make a complete dictionary of allowed words orginized by wordType
    for wordType in theEntireDictionary:
        for word in wordType:
            if chosenSent in word['sentsAllowed']: #: is a then
                theNewDictionary[theEntireDictionary.index(wordType)].append(word['word'])
    # print('chose ' + chosenSent)
    # print(theNewDictionary)

    # sentence structure
    if chosenSent == 'sentence_1':
        sentence = f"I {random.choice(allowed_verbs)} i {random.choice(allowed_past_tents)} {random.choice(allowed_superlative)} {random.choice(allowed_after_comma)}"
    elif chosenSent == 'sentence_2':
        sentence = f"I am {random.choice(allowed_verbs)} {random.choice(allowed_past_tents)} this {random.choice(allowed_nouns)}"
    elif chosenSent == 'sentence_3':
        sentence = f"Pretty {random.choice(allowed_superlative)}"

    # print(sentence)
    return sentence

if __name__ == "__main__":
    generateSentence()
    #i = 0          All this green is for looping
    #while i < 10:
        # generateSentence()
        #i = i + 1
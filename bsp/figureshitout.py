import logging
import answers
import json

question = 'where was george washington born'

query = str(answers.query(question))

# print("\n")
print(query)
# json.loads(query)
print(query['answer'])

with open('conc.json') as f:
    o = "{'question': 'where was george washington born', 'answer': ['westmoreland country virginia va']}"
    json.dump(o, f)


foundAnswer1 = (query['answer']) 
# foundAnswer1 = json.loads(query['answer'])
print("fuck")
print(foundAnswer1)
# what you doin doofus
# print the stupid thing use the debugger or just print doesn tmatter
# i dont think i see you type in term still
# just heads up
# your json file is wrong
print(type(foundAnswer1))
for answer in foundAnswer1:
    pass
    # print("//*[contains(text(),'" + str(answer) + "')]")       

    #fuckin pull it
    # you have caused me so much pain
    # fkin pull before you add answersi told you i fixed it i told you i made the update for list based answers yo fs-jjs-iddls lkjndfokajk sdfodfks fjknanswers
    # fifcoijfiodshj
    # i fixed it
    # you fuckin penut lid

# print("\n")
print(query)

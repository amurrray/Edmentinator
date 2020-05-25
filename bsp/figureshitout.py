import logging
import answers
import json

question = 'who was the brew man'

query = answers.query(question)

print(query)
# json.loads(query)
print(query['answer'])

for answer in query['answer']:
        print("//*[contains(text(),'" + str(answer) + "')]")       

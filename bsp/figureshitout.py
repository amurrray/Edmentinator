# array = ["soup:9273", "soup:2945", "soup:3826"] #make soup array
# print(array)

# count = len(array)   #count how many soups there are
# print(count)

# print() # print out "soup1" + "soup2" + "soup3"

# array = ["soup:9273", "soup:2945", "soup:3826"]
# arrayCount = len(array)
# print(str(arrayCount) + " soups")

# count_arr = [str("start_") + str(i) + str("_end") for i, x in enumerate(array, start=0)]

# print(count_arr)

# for x in count_arr:
#   print(x)  #entire FRQ command
#   if x == "start_"+str(arrayCount)+"_end":
#     break

# print(count_arr[0])

# Output: soup1 soup2 soup3

import json


scriptElm = 'Ed.Slide.MCQ = {"HasValue":true,"Stem":"Select the correct answer(s).","GenericFeedback":"Incorrect. Select the answer highlighted in yellow.","IsRandom":false,"Choices":[{"DisplayContent":"the terms of peace that the United States wanted from North Vietnam\u003c/p\u003e","IsCorrect":false,"Feedback":"\u003cp\u003eThe United States and North Vietnam discussed peace terms as part of the Paris Peace Accords in 1973.\u003c/p\u003e"},{"DisplayContent":"\u003cp\u003ea Vietnam military war plan that was exposed in \u003cem\u003eThe New York Times\u003c/em\u003e\u003c/p\u003e","IsCorrect":false,"Feedback":"\u003cp\u003eThe Pentagon Papers were a series of Department of Defense papers that chronicled US planning. They were published in \u003cem\u003eThe New York Times\u003c/em\u003e in 1971.\u003c/p\u003e"},{"DisplayContent":"\u003cp\u003ethe authorization for the use of US military force in Vietnam\u003c/p\u003e","IsCorrect":true,"Feedback":"\u003cp\u003eThe Gulf of Tonkin Resolution was a blank check from Congress to President Johnson to use any force needed in the conflict.\u003c/p\u003e"},{"DisplayContent":"\u003cp\u003ea plan to begin removing troops from Vietnam\u003c/p\u003e","IsCorrect":false,"Feedback":"\u003cp\u003eThe extended withdrawal of troops from Vietnam was one of Nixon\u0027s major campaign promises. He called this policy \"Vietnamization.\"\u003c/p\u003e"}],"Question":{"HasValue":true,"prompt":"","stem":"\u003cp\u003eWhat was the Gulf of Tonkin Resolution?\u003c/p\u003e","questionText":""},"Prompt":""};'

# print(scriptElm)
scriptElmCut = scriptElm[15:-1] #was [15:-1]
# scriptElmCut = scriptElm[15:] # this line isnt right for some reason # but the ; !!! # no i mean it wont cut it # the :-1 did? # gimmie lmao no ; dad?
print(scriptElmCut)
e = '''{"HasValue":true,"Stem":"Select the correct answer(s).","GenericFeedback":"Incorrect. Select the answer highlighted in yellow.","IsRandom":false,"Choices":[{"DisplayContent":"the terms of peace that the United States wa
nted from North Vietnam</p>","IsCorrect":false,"Feedback":"<p>The United States and North Vietnam discussed peace terms as part of the Paris Peace Accords in 1973.</p>"},{"DisplayContent":"<p>a Vietnam military war plan
 that was exposed in <em>The New York Times</em></p>","IsCorrect":false,"Feedback":"<p>The Pentagon Papers were a series of Department of Defense papers that chronicled US planning. They were published in <em>The New Yo
rk Times</em> in 1971.</p>"},{"DisplayContent":"<p>the authorization for the use of US military force in Vietnam</p>","IsCorrect":true,"Feedback":"<p>The Gulf of Tonkin Resolution was a blank check from Congress to Pres
ident Johnson to use any force needed in the conflict.</p>"},{"DisplayContent":"<p>a plan to begin removing troops from Vietnam</p>","IsCorrect":false,"Feedback":"<p>The extended withdrawal of troops from Vietnam was on
e of Nixon's major campaign promises. He called this policy "Vietnamization."</p>"}],"Question":{"HasValue":true,"prompt":"","stem":"<p>What was the Gulf of Tonkin Resolution?</p>","questionText":""},"Prompt":""} '''
# json.loads(scriptElmCut)
# json.loads(e) #there u go see the line 1 colum 220 @aidan #is it the U? lmao tf
# dad?? hello? ignore 
# where is the json str
# yes lmfao

# the json isnt formatted correctly, there is still some weird thing wthit
#print("bruh")

# s see if you can fix the json
#mmhmm no fucking clue can i end share for like 5 min sike i cant figure out how lmao
#i ts json, sue json valideators and look for incorrect chars thh==
#english? its json, theres a format for it, theres online formatters and validators also the TCD discord ight
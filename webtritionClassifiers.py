import exrex
from NBC import NBC

topicTrainingSet = []

daysOfWeek = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)(|s)"
days = "( |today|tomorrow|((on|this|next) "+daysOfWeek+"))"
meals = "(breakfast|brunch|lunch|dinner)"
times = "(at what time|what time|when) "
hoursQuestions = ("(tell me about hours)|(i would like to know about hours)"
                  "|("+ times + "is " + meals + " (|open)" + days + ")"
                  "|("+ times + "does " + meals + " " + days + " (start|open|close|end))"
                  "|(" + times + " does the dining hall open for " + meals + " " + days + ")"
                  "|(what are the " + meals + " hours " + days + ")")
hoursSet = ["hours"]*100 + list(exrex.generate(hoursQuestions))

foodFilters = "(vegetarian|without meat|meat free|vegan|gluten free|without gluten|free of gluten)"
foodQuestionForms = "(what's|what's for|what's being served for|what will there be for|what is going to be at|what food is going to be at|what will the dining hall serve for| what will the dining hall be serving for)"
foodQuestions = ("(tell me about food)|(i would like to know about food)|(what's for " + meals + ")"
                 "|(" + foodQuestionForms + " " + meals + " " + days + "(|(doesn't have gluten)|( that is " + foodFilters + ")))"
                 "|(tell me about " + meals + " in the dining hall " + days + ")")
foodSet = ["food"]*100 + list(exrex.generate(foodQuestions))

basicPromptsRegex = "(what's for |) " + meals
basicPrompts = list(exrex.generate(basicPromptsRegex))
# print basicPrompts
notQuestions = ["no thank you", "no thanks", "that's all for now", "no more questions", "nope", "that's it", "no"]
questions = ["yes", "yes please", "I have another question"]

combinedSet = hoursSet + foodSet

topicClassifier = NBC()
topicClassifier.addToSet(hoursSet, "hours")
topicClassifier.addToSet(foodSet, "food")
topicClassifier.train()

questionClassifier = NBC()
questionClassifier.addToSet(hoursSet + foodSet + basicPrompts + questions, "question")
questionClassifier.addToSet(notQuestions*100, "None")
questionClassifier.train()

dayClassifier = NBC()
dayClassifier.addToSetChooseCategory(combinedSet, ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
dayClassifier.train()

mealClassifier = NBC()
mealClassifier.addToSetChooseCategory(combinedSet, ["breakfast", "brunch", "lunch", "dinner"])
mealClassifier.train()

glutenClassifier = NBC()
glutenClassifier.addToSet(basicPrompts*100, "None")
glutenClassifier.addToSetIfContains(foodSet, ["gluten"], "gluten free")
glutenClassifier.train()

veganClassifier = NBC()
veganClassifier.addToSet(basicPrompts*100, "None")
veganClassifier.addToSetChooseCategory(foodSet, ["vegan"])
veganClassifier.train()

vegetarianClassifier = NBC()
vegetarianClassifier.addToSet(basicPrompts*100, "None")
vegetarianClassifier.addToSetIfContains(foodSet, ["vegetarian", "meat free", "without meat"], "vegetarian")
vegetarianClassifier.train()

glutenClassifier.enableCheat("gluten", "gluten free")
veganClassifier.enableCheat("vegan", "vegan")
vegetarianClassifier.enableCheat("vegetarian", "vegetarian")

if __name__=="__main__":
    topicClassifier.save("topicClassifier.txt")
    dayClassifier.save("dayClassifier.txt")
    mealClassifier.save("mealClassifier.txt")
    glutenClassifier.save("glutenClassifier.txt")
    veganClassifier.save("veganClassifier.txt")
    vegetarianClassifier.save("vegetarianClassifier.txt")
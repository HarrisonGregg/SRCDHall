#TODO: fix all states that print out all meals
import sys
sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pymongo')
sys.path.insert(0,'/usr/local/bin/')
import time
import re
import pymongo
from pymongo import MongoClient

from webtritionClassifiers import topicClassifier
from webtritionClassifiers import questionClassifier
from webtritionClassifiers import dayClassifier
from webtritionClassifiers import mealClassifier
from webtritionClassifiers import glutenClassifier
from webtritionClassifiers import veganClassifier
from webtritionClassifiers import vegetarianClassifier

debug = False

client = MongoClient('mongodb://harrisongregg:troublerice2outofdepth@ds043220.mongolab.com:43220/dineoncampus')
db = client.dineoncampus
posts = db.posts

meals = ["breakfast", "brunch", "lunch", "dinner", "dinner"]
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
daysAbbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
hours = [["eight","eleven"],["ten","two"],["eleven fifteen", "one fourty-five"],["four","seven"],["five","six thirty"]]

def getToday():
    return daysAbbr.index(time.strftime("%a"))  

def getDay(d):
    today = getToday()
    if d == today or d == None:
        return "today"
    if d == (today+1)%7:
        return "tomorrow"
    return "on " + days[d]

def getHours(m, d):
    if d == None:
        d = getToday()
    if not isOpen(d):
        return "The dining hall is not serving " + meals[m] + " " + getDay(d) + "."
    if d >= 5:
        if m == 3:
            m = 4
        if m == 0 or m == 2:
            m = 1
    else:
        if m == 1:
            m = 0
    return "The dining hall is open for " + meals[m] + " " + getDay(d) + " from " + hours[m][0] + " to " + hours[m][1] + "."

def isOpen(d):
    diff = d - getToday()
    dt = datetime.datetime.now() + datetime.timedelta(days=diff)
    params = {"date":dt.date().isoformat()}
    for day in db.days.find(params):
        return day["open"]:
print isOpen(2)

def retrieveFood(m, d, glutenFree, vegetarian, vegan):
    foods = []

    params = {"day": d, "meal": meals[m]}

    if vegan:
        params["vegan"] = True
    elif vegetarian:
        params["vegetarian"] = True
    if glutenFree:
        params["glutenFree"] = True

    # print(params)
    for post in posts.find(params):
        foods.append(post["name"])
    return foods

def getFood(m, d, glutenFree, vegetarian, vegan):
    foods = retrieveFood(m, d, glutenFree, vegetarian, vegan)

    if len(foods) == 0:
        return "There is no food for " + meals[m] + " " + getDay(d) + " that matches those criteria.\n"

    response = "The "
    if(vegan):
        response += "vegan "
    elif(vegetarian):
        response += "vegetarian "
    if(glutenFree):
        response += "gluten free "
    response +=  "food the dining hall is serving for " + meals[m] + " " + getDay(d) + " is "

    for food in foods[:-1]:
        response += food + ", "
    response += "and " + foods[-1] + "."

    return response

def parseDay(day):
    if day == "None":
        return None
    d = -1
    day = day.lower()
    if day in days:
        d = days.index(day)
    today = getToday()
    if day == "today":
        d = today
    if day == "tomorrow":
        d = (today+1)%7
    return d

def parseMeal(meal):
    if meal == "None":
        return None
    return meals.index(meal)

def getResponse(state, text, params):
    anotherQuestion = " Would you like to ask another question?"
    didntUnderstant = "I'm sorry, I didn't understand that. "
    response = "Error: invalid state"

    d = params.get("d", None) 
    m = params.get("m", None) 
    vegan = params.get("vegan", False) 
    vegetarian = params.get("vegetarian", False) 
    glutenFree = params.get("glutenFree", False)

    if state == "start":
        state = "foodOrHours"
        response = "I can answer questions about the Simon's Rock dining hall. Is your question regarding dining hall food or hours?"
    elif state == "restart":
        if questionClassifier.classify(text) == "question":
            state = "foodOrHours"
            response = "Is your question regarding dining hall food or hours?"
        else:
            state = "end"
            response = "I hope I was able to provide the information you desired. Please visit again soon."
    elif state == "foodOrHours":
        if topicClassifier.classify(text) == "food":
            state = "food"
            response = "What day and meal do you want to know the food of?"
        elif topicClassifier.classify(text) == "hours":
            state = "hours"
            response = "What meal would you like to know the hours of?"
        else:
            response = didntUnderstant + "Is your question regarding dining hall food or hours?"
    elif state == "hours":
        d = parseDay(dayClassifier.classify(text))
        m = parseMeal(mealClassifier.classify(text))
        if d == None and m == None:
            response = didntUnderstant + "What meal would you like to know the hours of?"
        else:
            response = getHours(m, d) + anotherQuestion
            state = "restart"
    elif state == "food":
        d = parseDay(dayClassifier.classify(text))
        m = parseMeal(mealClassifier.classify(text))
        glutenFree = glutenClassifier.classify(text) == "gluten free"
        vegan = veganClassifier.classify(text) == "vegan"
        vegetarian = vegetarianClassifier.classify(text) == "vegetarian"

        numResults = len(retrieveFood(m, d, glutenFree, vegetarian, vegan))
        if d == None and m == None:
            response = "I'm sorry, I didn't understand that. What day and meal do you want to know the food of?"
        elif numResults == 0:
            response = "I'm sorry, there are no results matching those criteria." + anotherQuestion
            state = "restart"
        else:
            response = "There are " + str(numResults) + " items that match those criteria.  Would you like to add any filters, such as vegetarian or gluten free?"
            state = "addFilter"
    elif state == "addFilter":
        if d == None:
            d = parseDay(dayClassifier.classify(text))
        if m == None:
            m = parseMeal(mealClassifier.classify(text))
        glutenFree = glutenFree or glutenClassifier.classify(text) == "gluten free"
        vegan = vegan or veganClassifier.classify(text) == "vegan"
        vegetarian = vegetarian or vegetarianClassifier.classify(text) == "vegetarian"
        response = getFood(m, d, glutenFree, vegetarian, vegan) + anotherQuestion
        state = "restart"
                    
    # return response, state, d, m
    params = {"d":d, "m":m, "vegan":vegan, "vegetarian":vegetarian, "glutenFree":glutenFree}
    return state, response, params

if __name__=='__main__':
    debug = True
    state = "start"
    text = ""
    params = {}
    while True:
        state, response, params = getResponse(state, text, params)
        if state == "end":
            print response
            break
        text = raw_input(response + "\n")
        


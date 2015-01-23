import random

from naiveBayesClassifier import tokenizer
from naiveBayesClassifier.trainer import Trainer
from naiveBayesClassifier.classifier import Classifier

class MyClassifier:
    def __init__(self, data):
        self.classifier = Classifier(data, tokenizer)

    def classify(self, s, fullResult=False):
        if s[-1] == "?":
            s = s[:-1]
        result = self.classifier.classify(s)
        if fullResult:
            return result
        if len(result) == 0:
            return "None"
        if len(result) == 1:
            return result[0][0]
        if result[0][1] == result[1][1]:
            return "None"
        return result[0][0]

class NBC:
    def __init__(self):
        self.trainingSet = []
        self.trainer = Trainer(tokenizer)
        self.classifier = None
        self.cheat = False
        self.cheatString = ""
        self.cheatResponse = ""

    def test(self, sampleRate=0.1, retrain=False):
        testTrainer = self.trainer
        testSet = []
        if retrain:
            testTrainer = Trainer(tokenizer)
        for x in self.trainingSet:
            if random.random() < sampleRate:
                testSet.append(x)
            else:
                if retrain:
                    testTrainer.train(x['text'], x['category'])
        numCorrectlyClassified = 0
        testClassifier = MyClassifier(testTrainer.data)
        incorrectlyClassified = []
        for x in testSet:
            result = testClassifier.classify(x['text'])
            if result == x['category']:
                numCorrectlyClassified += 1
            else:
                incorrectlyClassified.append(x)
                print("incorrectly classified: " + x['text'])
                print("expected:       " + x['category'])
                print("classification: " + result)
        print("Correctly classified: " + str(numCorrectlyClassified) + "/" + str(len(testSet)))
        return incorrectlyClassified

    def reinforce(self, n=10):
        incorrectlyClassified = self.test()
        for x in incorrectlyClassified:
            for i in range(n):
                self.trainer.train(x['text'], x['category'])

    def save(self, fileName):
        print(self.trainer.data)
        f = open(fileName, "w")
        f.write(self.trainer.data)
        f.close()

    def load(self, fileName):
        f = open(fileName, "r")
        data = f.read()
        f.close()
        self.classifier = Classifier(data)

    def train(self):
        random.shuffle(self.trainingSet)
        self.trainer = Trainer(tokenizer)
        for x in self.trainingSet:
            self.trainer.train(x['text'], x['category'])
        self.classifier = MyClassifier(self.trainer.data)

    def classify(self, s, fullResult=False):
        if self.cheat and not fullResult:
            if self.cheatString in s:
                return self.cheatResponse
            return "None"
        return self.classifier.classify(s, fullResult)

    def addToSet(self, texts, category):
        for text in texts:
            self.trainingSet.append({"text":text, "category": category})

    def addDictsToSet(self, dicts, n = 1):
        for x in dicts:
            for i in range(n):
                self.trainingSet.append(x)

    def addToSetChooseCategory(self, texts, categories):
        for text in texts:
            b = False
            for category in categories:
                if category in text:
                    self.trainingSet.append({"text":text, "category": category})    
                    b = True
                    break
            if not b:
                self.trainingSet.append({"text":text, "category": "None"})  

    def addToSetIfContains(self, texts, substrs, category):
        for text in texts:
            b = False
            for substr in substrs:
                if substr in text:
                    self.trainingSet.append({"text":text, "category": category})    
                    b = True
                    break
            if not b:
                self.trainingSet.append({"text":text, "category": "None"})  

    def enableCheat(self, s, response):
        self.cheat = True
        self.cheatString = s
        self.cheatResponse = response
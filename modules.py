import random, sys, werkzeug, os, string
from csv import DictReader

#file that will hold all pre written modules for the humanity web 

#filter words synonymes 
def filter(text):
    lists= []
    word = ""

    for x in range(0,len(text)):
        def tryer(text):
            try:
                text[x + 1]
            except IndexError:
                return True
            return False
        if text[x] == " ":
            lists.append(word)
            word = ""
            continue
        elif tryer(text) == True:
            word += text[x]
            lists.append(word)
            word = ""
            continue
        word += text[x]
    #print(lists)
    return lists
#done filtering words 
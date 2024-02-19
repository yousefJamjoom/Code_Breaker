# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 15:15:48 2022

@author: youse
"""
import copy
import random
import Querry as querry
from tkinter import *
import timeit

root = Tk()
root.title("Ai Code Breaker")
root.geometry("440x800")

class predicate:
    
    def __init__(self, name,*args):
        self.name = name
        if len(args) == 1:
            self.constant = args[0]
        elif len(args) > 1:
            self.constant = [args[0],args[1]]
        else :
            self.constant = None
    
    def getValue(self, constant):
        if self.name == "color":
            var = constant[0]
        elif self.name == "position":
            var = constant[1]
        else:
            var = constant
            
        if self.constant == var:
            return True
        else:
            return None
            
    def shape(self):
        return "{}({})".format(self.name,self.constant)
    
    
    
class And:

    def __init__(self, *args):
        self.elements = args
        self.value = None
    
            
    # returns the symbols in a natural language that can be easily understand       
    def shape(self):  
        string = "("
        for elem in self.elements:
            if elem != self.elements[-1]:
                string += "{} ^ ".format(elem.shape())
            else :
                string += "{})".format(elem.shape()) 
        return string
    
    def add(self,elem):
        self.elements += (elem,)
            
    def getValue(self,constant):
        value = True
        for elem in self.elements:
            check = elem.getValue(constant)
            if check == None:
                value = None
                continue
            elif check:
                continue
            else:
                value = False
                break
        return value
    
class Or:
    
    def __init__(self, *args):
        self.elements = args
        self.value = None
    
            
    # returns the symbols in a natural language that can be easily understand       
    def shape(self):  
        string = "("
        for elem in self.elements:
            if elem != self.elements[-1]:
                string += "{} v ".format(elem.shape())
            else :
                string += "{})".format(elem.shape()) 
        return string
    
    def add(self,elem):
        self.elements += (elem,)
            
    def getValue(self,constant):
        value = False
        for elem in self.elements:
            check = elem.getValue(constant)
            if check == None:
                value = None
                continue
            elif check:
                value = True
                break
        return value
    
class Not:
    
    def __init__(self, elem):
        self.elem = elem
        
    def shape(self):
        return"~{}".format(self.elem.shape())
        
    def getValue(self, constant):
        check = self.elem.getValue(constant)
        if check == None:
            return None
        else:
            return not check 
        
class Implies:
    
    def __init__(self, elem1, elem2):
        self.elem1 = elem1
        self.elem2 = elem2
        
    def shape(self):
        return "({})-->({})".format(self.elem1.shape(),self.elem2.shape())
    
    def getValue(self, constant):
        e1Value = self.elem1.getValue(constant)
        e2Value = self.elem2.getValue(constant)
        if e2Value == True or e1Value == False:
            return True
        elif e1Value == None or e2Value == None:
            return None
        else:
            return False
        
class Bi:
    
    def __init__(self, elem1, elem2):
        self.elem1 = elem1
        self.elem2 = elem2
            
    def shape(self):
        return "({})<-->({})".format(self.elem1.shape(),self.elem2.shape())
    
    def getValue(self, constant):
        e1Value = self.elem1.getValue(constant)
        e2Value = self.elem2.getValue(constant)
        if e2Value == None or e1Value == None:
            return None
        elif e1Value == e2Value:
            return True
        else:
            return False
        
class Zor:
    
    def __init__(self, elem1, elem2):
        self.elem1 = elem1
        self.elem2 = elem2
            
    def shape(self):
        return "({}) != ({})".format(self.elem1.shape(),self.elem2.shape())
    
    def getValue(self, constant):
        e1Value = self.elem1.getValue(constant)
        e2Value = self.elem2.getValue(constant)
        if e2Value == None or e1Value == None:
            return None
        elif e1Value == e2Value:
            return False
        else:
            return True
        
class onlyN:
    
    def __init__(self, ntv,*args): # ntv stand for: number of true values
        self.ntv = ntv
        self.elements = args
        self.value = None
    
            
    # returns the symbols in a natural language that can be easily understand       
    def shape(self):  
        string = "("
        for elem in self.elements:
            if elem != self.elements[-1]:
                string += "{} !{}! ".format(elem.shape(),self.ntv)
            else :
                string += "{})".format(elem.shape()) 
        return string
    
    def add(self,elem):
        self.elements += (elem,)
            
    def getValue(self,values):
        List = []
        for elem in self.elements:
            if elem.constant == None:
                return None
            List.append(elem.constant)
            
        check = 0
        if self.elements[0].name == "color":
            for value in values:
                if value[0] in List :
                    check += 1
        else:
            for value in values:
                if value in List :
                    check += 1
        
        if check == self.ntv:
            return None
        else:
            return False
        
Querry = querry.readQuerry()
kb = And(onlyN(5,predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo")))


my_canvas = Canvas(root, width = 420, height = 640, highlightthickness=0)
my_canvas.grid(row=0, column=0)

class info:
    
    def __init__(self,kb, Querry):
        self.kb = kb
        self.Querry = Querry
        self.sum = 0
        self.List = [0]*40
        self.LengthQ = len(self.Querry)
        self.List7 = []
        self.BayQuerry = []
        self.ClueQuerry = []
        self.sp = False
        
    def updateQuerry(self, Querry):
        self.Querry = Querry
        self.LengthQ = len(Querry)
        
Info= info(kb, Querry)

def showPick():
    List = []
    for value in Info.pick:
        if value[0] != "green":
            List.append(value[0])
        else:
            List.append("#09AF98")
    x = 50
    y = 50*Info.sum + 20*(Info.sum-1)        
    for value in List:
        Circle = my_canvas.create_oval(x-30,y-30,x+30,y+30, fill=value)
        x+=80

def writeSuperQuerry():
    List = []
    for move in Info.Querry:
        for goal in Info.Querry:
             clue = getClue(move, goal)
             W = clue[0]
             B = clue[1]
             kbTrial = copy.deepcopy(Info.kb)
             kbTrial.add(onlyN(B,predicate("belongsTo",move[0]),predicate("belongsTo",move[1]),predicate("belongsTo",move[2]),predicate("belongsTo",move[3]),predicate("belongsTo",move[4])))
             kbTrial.add(onlyN(W,predicate("color",move[0][0]),predicate("color",move[1][0]),predicate("color",move[2][0]),predicate("color",move[3][0]),predicate("color",move[4][0])))      
             querry = getNewQuerry(kbTrial)
             List.append([move, goal, querry])
             
    with open("SuperQuerry.txt", "w") as f:
        for value in List:
             if value == List[-1]:
                 f.write(value[0]+"U"+value[1]+"U"+getListString(value[2]))
             else:
                 f.write(value[0]+"U"+value[1]+"U"+getListString(value[2])+"\n")


def getListString(List):
    string = ""
    for value in List:
        if value == List[-1] :
            string += value
        else:
            string = string + value + "|"
            
    return string

def getNewQuerry(kb):
    newQuerry = []
    for value in Info.Querry:
        check = kb.getValue(value)
        if check or check == None:
            newQuerry.append(value)
    return newQuerry             
 
def setNewQuerry():
    #Info.List = [0]*40
    newQuerry = []
   # newBayQuerry = []
    for index in range(len(Info.Querry)):
        check = Info.kb.getValue(Info.Querry[index])
        if check or check == None:
            pickFilter(Info.Querry[index])
            newQuerry.append(Info.Querry[index])
         #   newBayQuerry.append(Info.BayQuerry[index])
    print(len(newQuerry))
    if len(newQuerry) == 0:
        print("yes :",Info.Querry)
    
    #Info.BayQuerry = newBayQuerry        
    Info.updateQuerry(newQuerry)
    # print(Info.List)
 
    
def Play(clue, x, y):
    Info.sum += 1
# =============================================================================
#   
#     if Info.sum == 1 or len(Info.Querry) > 100:
#         index = random.randint(0,len(Info.Querry)-1)
#         pick = Info.Querry[index]
#     else:
#         pick = getOptimalMove()
# =============================================================================
        
    if Info.sum == 1:
        index = random.randint(0,len(Info.Querry)-1)
        pick = Info.Querry[index]
        print("\n",pick)
    else:     
        #start = timeit.default_timer()
# =============================================================================
#         if False and (clue == [3,0] or clue == [3,1]) and Info.sum == 2: #x >= 1) or (clue == [4,0] and x >= 2) or (clue == [4,1] and x >= 3)) and ((Info.sum == 3 and y == 0) or (Info.sum == 4 and y == 1) or (Info.sum == 5 and y == 2)):
#             pick = specialCase(clue, x, y)
#             Info.sp = True
#         else:
# =============================================================================
        pick = BayesianPick(clue)
        #stop = timeit.default_timer()
        #print('Time: ', stop - start)
   
    if Info.sum == 1:
        Info.List7 = []
    else:
        Info.List7.append(clue)
        
    print(pick,"\n\n")
    Info.pick = pick
    print("Pick is :\n", pick)
    showPick()
    

def PlayAlone(goal, clue, x, y):
    if Info.BayQuerry == []:
        Info.BayQuerry = [1/Info.LengthQ]*Info.LengthQ
       # print(Info.BayQuerry)
    Play(clue, x, y)
    clue = getClueM(Info.pick, goal)
# =============================================================================
#     print("Clue = ",clue)
#     print("Pick = ",Info.pick)
#     print("Goal = ",goal)
# =============================================================================
    W = clue[0]
    B = clue[1]
    # print(len(Info.Querry))
    if B != 5:
        Info.kb.add(onlyN(B,predicate("belongsTo",Info.pick[0]),predicate("belongsTo",Info.pick[1]),predicate("belongsTo",Info.pick[2]),predicate("belongsTo",Info.pick[3]),predicate("belongsTo",Info.pick[4])))
        Info.kb.add(onlyN(W,predicate("color",Info.pick[0][0]),predicate("color",Info.pick[1][0]),predicate("color",Info.pick[2][0]),predicate("color",Info.pick[3][0]),predicate("color",Info.pick[4][0])))
        setNewQuerry()
        return PlayAlone(goal,clue, x, y)+1
    else:
        return 1

def countAveragePlay(nGames, x, y, count): # nGames stands for: number of games
    Sum = 0
    List = []
    counter = 0
    cases = 0
    worst = []
    while(cases != nGames):
        counter += 1
        Info.sp = False
        #print(Info.List7)
        Info.kb = And(onlyN(5,predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo"),predicate("belongsTo")))
        Info.updateQuerry(Querry)
        Info.sum = 0
        Info.BayQuerry = []
        index = random.randint(0,len(Info.Querry)-1)
        goal = Querry[index]
        # print("Goal is :\n",goal)
        start = timeit.default_timer()    
        score = PlayAlone(goal, None, x, y)
        stop = timeit.default_timer()   
        print('Time: ', stop - start)
        if score >= 7:
            List.append(score)
        if score >= 8:
            worst.append(Info.List7)
            worst.append("-><-")
        Sum += score
        cases += 1
        print(score," Special Case = ",Info.sp," Game =",counter, "Sim = ",count)
    print("the average score is = ", (Sum/nGames), "X = ",x,"Y = ", y, " Bad Games = ",List);
    return ("the average score is = "+ str(Sum/nGames)+ " X = "+str(x)+" Y = "+str(y)+ " Bad Games = "+str(List)+" Worst games = "+str(worst))
      

def getClueM(move, goal):
    W = 0
    B = 0
    List = []
    for value in move:
        if value in goal:
            B+=1
        List.append(value[0])
        
    for value in goal:
        if value[0] in List:
            W += 1
    
    # print([W,B])
    return [W,B]

def getKnowledgeSize(clue, move):
    W = clue[0]
    B = clue[1]
    kbTrial = copy.deepcopy(Info.kb)
    kbTrial.add(onlyN(B,predicate("belongsTo",move[0]),predicate("belongsTo",move[1]),predicate("belongsTo",move[2]),predicate("belongsTo",move[3]),predicate("belongsTo",move[4])))
    kbTrial.add(onlyN(W,predicate("color",move[0][0]),predicate("color",move[1][0]),predicate("color",move[2][0]),predicate("color",move[3][0]),predicate("color",move[4][0])))      
    newQuerry = []
    for move in Info.Querry:
        check = kbTrial.getValue(move)
        if check or check == None:
            newQuerry.append(move)
            
    lsolutions = len(newQuerry)
    dsolutions = len(Info.Querry)
    
    if lsolutions != 0:        
        return dsolutions/lsolutions
    else:
        return 0
    
def findValue(move):
    List = []
    Clues = [[2,0],[2,1],[2,2],[3,0],[3,1],[3,2],[3,3],[4,0],[4,1],[4,2],[4,3],[4,4],[5,0],[5,1],[5,2],[5,3],[5,5]]
    for clue in Clues:
        List.append(getKnowledgeSize(clue, move))
        
    return sum(List)

def getOptimalMove():
    if len(Info.Querry) == 1:
        return Info.Querry[0]
    
    List = []
    for move in Info.Querry:
        List.append([move, findValue(move)])
        
    Sum = -1
    index = 0
    
    if len(List) == 0:
        print(Info.Querry)
    for i in range(len(List)):
        value = List[i][1]
        if Sum < value:
            Sum = value
            index = i
    return List[index][0]
      
    
def getClue():
    while True:
        pick = input("pick: ")
        pick = pick.split(" ")
        B = 0
        W = 0
        for i in range(len(pick)):
            if i == 0:
                pick[i] = [pick[i],"one"]
            if i == 1:
                pick[i] = [pick[i],"two"]
            if i == 2:
                pick[i] = [pick[i],"three"]
            if i == 3:
                pick[i] = [pick[i],"four"]
            if i == 4:
                pick[i] = [pick[i],"five"]
        List = []
        print(Info.pick, pick)
        for value in Info.pick:
            if value in pick:
                B += 1
            List.append(value[0])
        for value in pick:
            if value[0] in List:
                W +=1
                
        if B == 5:
            print("End")
        else:
            print("{} {}\n".format(B,W))
    


def pickFilter(pick):
    List = [0]*40
    for value in pick:
        List[colorFilter(value[0])+positionFilter(value[1])] += 1
        
    for i in range(len(List)):
        Info.List[i] += List[i]
            
def getPickValue(pick):
    Sum = 0
    for value in pick:
        Sum += Info.List[colorFilter(value[0])+positionFilter(value[1])]
        
    Sum = Sum/(Info.LengthQ*5)
    return Sum

def colorFilter(value):
    if value == "blue":
        return 0
    elif value == "green":
        return 5
    elif value == "red":
        return 10
    elif value == "yellow":
        return 15
    elif value == "purple":
        return 20
    elif value == "orange":
        return 25
    elif value == "black":
        return 30
    elif value == "white":
        return 35
    
def positionFilter(value):
    if value == "one":
        return 0
    elif value == "two":
        return 1
    elif value == "three":
        return 2
    elif value == "four":
        return 3
    elif value == "five":
        return 4

def intelligentPick():
    getDreamPick()
    Sum = 0
    index = -1
    for i in range(len(Info.Querry)):
        if Sum == 0 or Sum < utility(Info.Querry[i]):
            Sum = utility(Info.Querry[i])
            index = i
    return Info.Querry[index]
    
def getDreamPick():
    dreamPick = []
    Colors = ["blue","green","red","yellow","purple","orange","black","white"]
    Positions = ["one","two","three","four","five"]
    values = []
    for color in Colors:
        for position in Positions:
            values.append([color,position])
    for e in range(5):
        most = 0
        index = -1
        for i in range(len(Info.List))[e:]:
            if most == 0 or most < Info.List[i]:
                most = Info.List[i]
                index = i
            i+=4
        dreamPick.append([values[index], Positions[e]])
    
    Info.dreamPick = dreamPick

def utility(pick):
    goal = Info.dreamPick
    Sum = 0
    for i in range(len(pick)):
        if pick[i] == goal[i]:
            Sum += 1
            
    return Sum

     # 2W - 3W - 4W - 5W - 1B2W - 2B2W - 1B3W - 2B3W - 3B3W - 1B4W - 2B4W - 3B4W - 4B4W - 1B5W - 2B5W - 3B5W - 5B5W
def AiPick(x,y,z):
    #getDreamPick()
    propValue = 0
    Sum = 0
    picked = [] 
    List = []
    #print(".............................................................")
    for pick in Info.Querry:
        getPickPlates(pick)
        # print(Info.plates)
        pickValue = 0
        k = getPickValue(pick)
        
        #for goal in Info.Querry:
        #    c = getClueM(pick,goal)
        m = getSumPlatesValue()
        if Info.plates not in List:
            List.append(pick)
            List.append(Info.plates)
           # v = getPickValue(goal)
           # print("Here is M = ",m," K = ",k)
        pickValue += (x*m+y*k)
        if Sum == 0 or Sum < pickValue:
            Sum = pickValue
            picked = pick
    if len(List) <= 6:
        print(List)
    return picked

def checkInList(value, List):
    for i in range(len(List)):
        if value == List[i][:2]:
            return [i,False]
    return [0,True]

def countList(List):
    count = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for value in List:
           if value[1] == [2,0]:
               count[0] += 1
           elif value[1] == [2,1]:
               count[1] += 1
           elif value[1] == [2,2]:
               count[2] += 1
           elif value[1] == [3,0]:
               count[3] += 1
           elif value[1] == [3,1]:
               count[4] += 1
           elif value[1] == [3,2]:
               count[5] += 1
           elif value[1] == [3,3]:
               count[6] += 1
           elif value[1] == [4,0]:
               count[7] += 1
           elif value[1] == [4,1]:
               count[8] += 1
           elif value[1] == [4,2]:
               count[9] += 1
           elif value[1] == [4,3]:
               count[10] += 1
           elif value[1] == [4,4]:
               count[11] += 1
           elif value[1] == [5,0]:
               count[12] += 1
           elif value[1] == [5,1]:
               count[13] += 1
           elif value[1] == [5,2]:
               count[14] += 1
           elif value[1] == [5,3]:
               count[15] += 1
           elif value[1] == [5,5]:
               count[16] += 1

    print("[2,0] =",count[0],"[2,1] =",count[1],"[2,2] =",count[2],"[3,0] =",count[3],"[3,1] =",count[4],"[3,2] =",count[5],"[3,3] =",count[6],"[4,0] =",count[7],"[4,1] =",count[8],"[4,2] =",count[9],"[4,3] =",count[10],"[4,4] =",count[11],"[5,0] =",count[12],"[5,1] =",count[13],"[5,2] =",count[14],"[5,3] =",count[15],"[5,5] =",count[16])
               
def getSumPlatesValue():
    x = 0
    for plate in Info.plates:
        x += plate[1]
    return x
    
def getPlateValue(clue):
    for plate in Info.plates:
        if plate[0] == clue:
            return plate[1]
                
def getPickPlates(pick):
    Info.plates = []
    plates = [[2,0],[3,0],[4,0],[5,0],[2,1],[2,2],[3,1],[3,2],[3,3],[4,1],[4,2],[4,3],[4,4],[5,1],[5,2],[5,3],[5,5]]
    for plate in plates:
        Info.plates.append([plate, setPlateValue(pick,plate)])
        
def setPlateValue(move, plate):
    W = plate[0]
    B = plate[1]
    kbTrial = copy.deepcopy(Info.kb)
    kbTrial.add(onlyN(B,predicate("belongsTo",move[0]),predicate("belongsTo",move[1]),predicate("belongsTo",move[2]),predicate("belongsTo",move[3]),predicate("belongsTo",move[4])))
    kbTrial.add(onlyN(W,predicate("color",move[0][0]),predicate("color",move[1][0]),predicate("color",move[2][0]),predicate("color",move[3][0]),predicate("color",move[4][0])))      
    newQuerry = 0
    for move in Info.Querry:
        check = kbTrial.getValue(move)
        if check != False:
            newQuerry+= 1       
    
    if newQuerry != 0:        
        return Info.LengthQ/newQuerry
    else:
        return 0
    

def BayesianPick(clue):
    maxValue = 0
    pick = Info.Querry[0]
    if Info.LengthQ >20:
        pE = getClueProb(clue)
    for index in range(len(Info.Querry)):
        if Info.LengthQ >20:
            pH = 1/Info.LengthQ
            EgivenH = Info.ClueQuerry[index]
            upper = EgivenH*pH
            lower = pE
            if lower != 0 :
                value = upper/lower
            else:
                value = 0
            if value <= maxValue:
                maxValue = value
                pick = Info.Querry[index]
        else:
            value = findValue(Info.Querry[index])
            if value >= maxValue:
                maxValue = value
                pick = Info.Querry[index]
    return pick

def getClueProb(clue):
    Sum = 0
    Info.ClueQuerry = [0]*Info.LengthQ
    for index in range(Info.LengthQ):
        for move in Info.Querry:
            value = getClueM(move, Info.Querry[index])
            if clue == value:
                Info.ClueQuerry[index] += 1
                Sum += 1
    return Sum

def getClueValues():
  
    pDict = {"[2, 0]":0,"[2, 1]":0,"[2, 2]":0,"[3, 0]":0,"[3, 1]":0,"[3, 2]":0,"[3, 3]":0,"[4, 0]":0,"[4, 1]":0,"[4, 2]":0,"[4, 3]":0,"[4, 4]":0,"[5, 0]":0,"[5, 1]":0,"[5, 2]":0,"[5, 3]":0,"[5, 5]":0}
    for goal in Info.Querry:
        for move in Info.Querry:
            pDict[str(getClueM(move, goal))] += 1
    return pDict

def getCondProb(goal):
    Sum = 0
    Clues = [[2,0],[2,1],[2,2],[3,0],[3,1],[3,2],[3,3],[4,0],[4,1],[4,2],[4,3],[4,4],[5,0],[5,1],[5,2],[5,3],[5,5]]
    for clue in Clues:
        for move in Info.Querry:
            if getClueM(move, goal) == clue:
                Sum += 1
    return Sum/Info.LengthQ


def specialCase(x, y, z):
    while True:
        value = Querry[random.randint(0, len(Querry)-1)]
        clue = getClueM(value, Info.pick)
        if ((clue[0] != 3 or clue[1] != 0) and x == [3,0]) or ((clue[0] != 4 or clue[1] != 3) and x == [3,1]):
            continue
        #print("Case = ",clue)
        return value

frame = Frame(root, bg = "white")
frame2 = Frame(root, bg = "white")
button1 = Button(frame, padx=40, pady=10, text="", bg="gray")
button2 = Button(frame, padx=40, pady=10, text="", bg="gray")
button3 = Button(frame, padx=40, pady=10, text="", bg="gray")
button4 = Button(frame, padx=40, pady=10, text="", bg="gray")
button5 = Button(frame, padx=40, pady=10, text="", bg="gray")
button6 = Button(frame2, padx=40, pady=10, text="", bg="gray")
button7 = Button(frame2, padx=40, pady=10, text="", bg="gray")
button8 = Button(frame2, padx=40, pady=10, text="", bg="gray")
button9 = Button(frame2, padx=40, pady=10, text="", bg="gray")
button10 = Button(frame2, padx=40, pady=10, text="", bg="gray")
button1.pack(side=LEFT)
button2.pack(side=LEFT)
button3.pack(side=LEFT)
button4.pack(side=LEFT)
button5.pack(side=LEFT)
button6.pack(side=LEFT)
button7.pack(side=LEFT)
button8.pack(side=LEFT)
button9.pack(side=LEFT)
button10.pack(side=LEFT)

def hoverB(e):
    source = str(e.widget)[9:]
    List= findButtons(source)
    for button in List:
        if button["bg"] != "#000101":
            button["bg"] = "black"
    
def hoverW(e):
    source = str(e.widget)[10:]
    if len(source) == 6:
        source = source+"6"
    else:
        source = source[:-1]+str(int(source[-1])+5)
    List= findButtons(source)
    for button in List:
        button["bg"] = "white"
        
def UnhoverB(e):
    source = str(e.widget)[9:]
    List= findButtons(source)
    # print(e.type)
    for button in List:
        if int(e.type) == 8:
            if button["bg"] == "#000101":
                button["bg"] = "#000101"
                
            else:
                button["bg"] = "gray"
        else:
            button["bg"] = "#000101"
def UnhoverW(e):
    source = str(e.widget)[10:]
    if len(source) == 6:
        source = source+"6"
    else:
        source = source[:-1]+str(int(source[-1])+5)
    List= findButtons(source)
    for button in List:
        button["bg"] = "gray"

def setColorB(e):
    UnhoverB(e) 
    
def setColorW(e):
    source = str(e.widget)[10:]
    if len(source) == 6:
        source = source+"6"
    else:
        source = source[:-1]+str(int(source[-1])+5)
    White = len(findButtons(source))
    Black = 0
    buttons = [button1,button2,button3,button4,button5,button6,button7,button8,button9,button10]
    for button in buttons[:5]:
        if button["bg"] == "#000101":
          Black += 1 
              
        
          
    Info.kb.add(onlyN(Black,predicate("belongsTo",Info.pick[0]),predicate("belongsTo",Info.pick[1]),predicate("belongsTo",Info.pick[2]),predicate("belongsTo",Info.pick[3]),predicate("belongsTo",Info.pick[4])))
    Info.kb.add(onlyN(White,predicate("color",Info.pick[0][0]),predicate("color",Info.pick[1][0]),predicate("color",Info.pick[2][0]),predicate("color",Info.pick[3][0]),predicate("color",Info.pick[4][0])))      
    # print(len(Info.kb.elements))
    # print(len(querry))
    for button in buttons:
        button["bg"] = "gray"
        
    setNewQuerry()
    Play([White,Black], 0, 0)
    
def findButtons(source):
    List = []
    if len(source) == 6 or source == "button1":
        List.append(button1)
        return List
    elif source == "button6":
        List.append(button6)
        return List
    elif source == "button2":
        List.append(button2)
        return List+findButtons(source[:-1]+"1")
    elif source == "button3":
        List.append(button3)
        return List+findButtons(source[:-1]+"2")
    elif source == "button4":
        List.append(button4)
        return List+findButtons(source[:-1]+"3")
    elif source == "button5":
        List.append(button5)
        return List+findButtons(source[:-1]+"4")
    elif source == "button7":
        List.append(button7)
        return List+findButtons(source[:-1]+"6")
    elif source == "button8":
        List.append(button8)
        return List+findButtons(source[:-1]+"7")
    elif source == "button9":
        List.append(button9)
        return List+findButtons(source[:-1]+"8")
    elif source == "button10":
        List.append(button10)
        return List+findButtons(source[:-2]+"9")    
    
button1.bind("<Enter>", hoverB)
button2.bind("<Enter>", hoverB)
button3.bind("<Enter>", hoverB)
button4.bind("<Enter>", hoverB)
button5.bind("<Enter>", hoverB)
button6.bind("<Enter>", hoverW)
button7.bind("<Enter>", hoverW)
button8.bind("<Enter>", hoverW)
button9.bind("<Enter>", hoverW)
button10.bind("<Enter>", hoverW)

button1.bind("<Leave>", UnhoverB)
button2.bind("<Leave>", UnhoverB)
button3.bind("<Leave>", UnhoverB)
button4.bind("<Leave>", UnhoverB)
button5.bind("<Leave>", UnhoverB)
button6.bind("<Leave>", UnhoverW)
button7.bind("<Leave>", UnhoverW)
button8.bind("<Leave>", UnhoverW)
button9.bind("<Leave>", UnhoverW)
button10.bind("<Leave>", UnhoverW)

button1.bind("<Button>", setColorB)
button2.bind("<Button>", setColorB)
button3.bind("<Button>", setColorB)
button4.bind("<Button>", setColorB)
button5.bind("<Button>", setColorB)
button6.bind("<Button>", setColorW)
button7.bind("<Button>", setColorW)
button8.bind("<Button>", setColorW)
button9.bind("<Button>", setColorW)
button10.bind("<Button>", setColorW)


Play(None, 0, 0)
# getClue()


myLabel = Label(root, padx = 120, pady = 20, bg = "white", text= "Give me a Hint ^^", font=(None, 19))
myLabel.grid(row = 8, column = 0) 

my_canvas["bg"] = "gray"
root["bg"] = "gray"

frame.grid(row = 9, column = 0)
frame2.grid(row = 10, column = 0)

root.mainloop()

# =============================================================================
# def randomAvaragePlay():
#     results = ""
#     count = 0
#     for i in range(1):
#         count += 1
#         List = [[0,0],[4,3]]
#         start = timeit.default_timer()
#         results += countAveragePlay(1000, List[i][0], List[i][1], count) + "\n"
#         stop = timeit.default_timer()   
#         print('Time: ', stop - start)
#     print(results)
# randomAvaragePlay()
# =============================================================================

    
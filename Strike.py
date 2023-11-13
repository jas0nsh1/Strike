# Jason Shi, Yoosung Lee, Atharv Kashyap, Hanchen Liu
from cmu_graphics import *
import math
import random
from PIL import Image
import os
from threading import Thread

def onAppStart(app):
    loadMap(app)
    reset(app)
    app.p1WinCounter = 0
    app.p2WinCounter = 0
    thread = Thread(target=playSound)
    thread.start()

def playSound():
    file = "BGM.wav"
    print('playing sound using native player')
    os.system("afplay " + file)

def reset(app):
    loadPlayers(app)
    app.roundIndex = 0
    app.roundCount = 1
    app.textBox = []
    app.tempTextBox = []
    app.red = rgb(255,1,119)
    app.blue = rgb(0,50,255)
    app.playerCircleR = 10
    app.titleScreen = Image.open('titleS.png')
    app.titleScreen = CMUImage(app.titleScreen)
    app.player1Cities = set()
    app.player2Cities = set()
    app.player1Turn = True
    app.player2Turn = False
    app.moveCount = 0
    app.select1 = False
    app.select2 = False
    app.hintCity1 = None
    app.hintCity2 = None
    app.hintCity1 = 'None'
    app.hintCity2 = 'None'
    app.miss = False
    app.nextTurn = False
    app.nextMove = False
    app.drawInstruction = True
    app.paused = False
    app.gameOver = False
    app.winner = None

def redrawAll(app):
    drawMap(app)
    drawRound(app)
    drawSideText(app)
    drawScoreBoard(app)
    drawPlayers(app)
    drawShadow(app)
    drawHint(app)
    drawNextTurn(app)
    drawStrikeResult(app)
    drawInstructions(app)
    drawTieCondition(app)
    
def drawInstructions(app):
    if app.drawInstruction == True:
        drawRect(0,0, app.width, app.height)
        imageWidth, imageHeight = getImageSize(app.titleScreen)
        drawImage(app.titleScreen, app.width/2, app.height/2, align='center', width = imageWidth*0.8, height = imageHeight*0.8)
        drawLabel("Press 'space' to PLAY", app.width/2, 750, fill = 'white', size = 24)

def onKeyPress(app, key):
    
    if key == 'enter' and app.paused:
        app.paused = False
        app.nextTurn = True
    elif key == 'escape' and app.paused:
        app.paused = False
        app.miss = False
        app.nextMove = True
    elif key == 'r' and app.paused:
        reset(app)
    elif key == 'space':
        app.drawInstruction = False
    elif key == 's' and not app.paused:
        app.p1WinCounter = 0
        app.p2WinCounter = 0

        ### chat implementation ###

    elif key == 'n':
        if app.player1Turn:
            app.tempTextBox.append('P1: nice move!')
            app.tempTextBox += app.textBox
            app.textBox = []
            for i in range(len(app.tempTextBox)):
                app.textBox.append(app.tempTextBox[i])
            app.tempTextBox = []
        else:
            app.tempTextBox.append('P2: nice move!')
            app.tempTextBox += app.textBox
            app.textBox = []
            for i in range(len(app.tempTextBox)):
                app.textBox.append(app.tempTextBox[i])
            app.tempTextBox = []

    elif key == 'm':
        if app.player1Turn:
            app.tempTextBox.append('P1: oops!')
            app.tempTextBox += app.textBox
            app.textBox = []
            for i in range(len(app.tempTextBox)):
                app.textBox.append(app.tempTextBox[i])
            app.tempTextBox = []
        else:
            app.tempTextBox.append('P2: oops!')
            app.tempTextBox += app.textBox
            app.textBox = []
            for i in range(len(app.tempTextBox)):
                app.textBox.append(app.tempTextBox[i])
            app.tempTextBox = []

def onMousePress(app, mouseX, mouseY):
    if not app.paused:
        if app.player1Turn and distance(mouseX, mouseY, app.cx0, app.cy0) <= 10:
            app.cx0 = mouseX
            app.cy0 = mouseY
            app.select1 = True
            app.isDragging = True
        elif app.player2Turn and distance(mouseX, mouseY, app.cx1, app.cy1) <= 10:
            app.cx1 = mouseX
            app.cy1 = mouseY
            app.select2 = True
            app.isDragging = True
        elif pointInRect(app, mouseX, mouseY, 0):
            capture(app)
        elif pointInRect(app, mouseX, mouseY, 1):
            strike(app)
        elif pointInRect(app, mouseX, mouseY, 2):
            wait(app)

def onMouseDrag(app, mouseX, mouseY):
    if not app.paused:
        if app.player1Turn and app.select1:
            app.cx0 = mouseX
            app.cy0 = mouseY
        elif app.player2Turn and app.select2:
            app.cx1 = mouseX
            app.cy1 = mouseY

def onMouseRelease(app, mouseX, mouseY):
    if not app.paused:
        if app.player1Turn and app.select1:
            app.isDragging = False
            app.select1 = False

            bestCity = None
            bestDistance = 2000
            for city in app.cities:
                cx, cy = app.cities[city]
                if distance(mouseX, mouseY, cx, cy) < bestDistance and isMoveLegal(app, app.player1, city):
                    bestCity = city
                    bestDistance = distance(mouseX, mouseY, cx, cy)
            
            app.player1 = bestCity
            app.cx0, app.cy0 = app.cities[bestCity]
            app.moveCount += 1

        elif app.player2Turn and app.select2:
            app.isDragging = False
            app.select2 = False

            bestCity = None
            bestDistance = 2000
            for city in app.cities:
                cx, cy = app.cities[city]
                if distance(mouseX, mouseY, cx, cy) < bestDistance and isMoveLegal(app, app.player2, city):
                    bestCity = city
                    bestDistance = distance(mouseX, mouseY, cx, cy)
            
            app.player2 = bestCity
            app.cx1, app.cy1 = app.cities[bestCity]
            app.moveCount += 1
        
def isMoveLegal(app, currCity, city):
    if (currCity, city)  in app.paths or (city, currCity) in app.paths:
        return True
    else:
        return False

def loadPlayers(app):
    cityNames = list(app.cities.keys())
    # has duplicates which is a problem
    randomNum1 = random.randrange(len(cityNames)-1)
    randomNum2 = random.randrange(len(cityNames)-1)
    if randomNum1 == randomNum2:
        if randomNum1 != 8:
            randomNum2 += 1
        else:
            randomNum2 -= 1
    app.player1 = cityNames[randomNum1]
    app.player2 = cityNames[randomNum2]
    app.cx0, app.cy0 = app.cities[app.player1]
    app.cx1, app.cy1 = app.cities[app.player2]

def loadMap(app):
    app.mapUrl = Image.open('map3.png')
    app.mapUrl = CMUImage(app.mapUrl)
    app.cities = {'Brasilia':(800, 400),
                  'Caracas':(600, 120),
                  'Cayenne': (690, 150),
                  'Santiago':(650, 600),
                  'Quito':(560, 250),
                  'Manaus':(730, 270),
                  'Cusco':(615, 395),
                  'Montevideo':(765, 545),
                  'Salvador':(930, 340)}

    
    app.paths = {('Montevideo', 'Santiago'), ('Montevideo', 'Brasilia'), 
                  ('Cusco','Quito'),('Quito', 'Caracas'), 
                 ('Caracas', 'Cayenne'), ('Cayenne', 'Manaus'), 
                 ('Quito', 'Manaus'), ('Manaus', 'Brasilia'), 
                 ('Brasilia','Montevideo'), ('Brasilia', 'Cusco'), 
                 ('Caracas', 'Manaus'), ('Brasilia', 'Santiago'),
                 ('Manaus', 'Salvador'), ('Brasilia', 'Salvador'),
                 ('Cusco', 'Montevideo'), ('Brasilia', 'Quito')}

def distance(x0, y0, x1, y1):
    return math.sqrt((x1-x0)**2 + (y1-y0)**2)

def pointInRect(app, x, y, i):
    x0 = 728 + i*140
    y0 = 689
    x1 = 831 + i*140
    y1 = 792
    return (x0 <= x and x <= x1 and y0 <= y and y <= y1)

def strike(app):
    if app.player1Turn:
        if app.player1 == app.player2:
            app.gameOver = True
            app.paused = True
            app.winner = app.player1
            app.p1WinCounter += 1
        else:
            app.miss = True
            app.moveCount += 1
    elif app.player2Turn:
        if app.player2 == app.player1:
            app.gameOver = True
            app.paused = True
            app.winner = app.player2
            app.p2WinCounter += 1
        else:
            app.miss = True
            app.moveCount += 1

def wait(app):
    app.moveCount += 1

def capture(app):
    if app.player1Turn and app.player1 not in app.player1Cities:
        app.player1Cities.add(app.player1)
        if app.player1 in app.player2Cities:
            app.player2Cities.remove(app.player1)
        app.moveCount += 1
            
    if app.player2Turn and app.player2 not in app.player2Cities:
        app.player2Cities.add(app.player2)
        if app.player2 in app.player1Cities:
            app.player1Cities.remove(app.player2)  
        app.moveCount += 1

def getButtonName(i):
    if i == 0: return 'Capture'
    elif i == 1: return 'Shoot'
    elif i == 2: return 'Wait'

def drawMap(app):
    imageWidth, imageHeight = getImageSize(app.mapUrl)
    drawImage(app.mapUrl, app.width/2, app.height/2, align='center', width = imageWidth*0.8, height = imageHeight*0.8)
    #Draw Lines
    for (city1, city2) in app.paths:
        x0, y0 = app.cities[city1]
        x1, y1 = app.cities[city2]
        drawLine(x0, y0, x1, y1,fill='white',dashes=(5, 5)) 

    #Draw cities
    for city in app.cities:
        cx, cy = app.cities[city]
        drawRect(cx + 20, cy -20, 100, 20, fill = 'black', border='white',borderWidth = 0.5)
        drawLabel(city, cx + 25, cy - 15, bold = False,fill='white',size = 15, align = 'top-left')
        if city in app.player1Cities:
            borderColor = app.blue
            circleR = 25
            borderSize = 10
        elif city in app.player2Cities:
            borderColor = app.red
            circleR = 25
            borderSize = 10
        else:
            borderColor = 'white'
            circleR = 15
            borderSize = 0
        drawCircle(cx, cy, circleR, fill='white', border = borderColor, borderWidth=borderSize) 

        if app.player1Turn and app.player2 in app.player1Cities:
            drawCircle(app.cx1, app.cy1, 10, fill = app.red)
        elif app.player2Turn and app.player1 in app.player2Cities:
            drawCircle(app.cx0, app.cy0, 10, fill = app.blue)

    #Draw Buttons
    for i in range(3):
        drawRect(728 + i*140, 689, 103, 103, opacity = 0)
        drawLabel(getButtonName(i), 780 + i*140, 805, size = 15, bold = True, fill = 'white', opacity = 0)
        #Draw player last seen 

def drawShadow(app):
    if app.hintCity1 != 'None':
        x1, y1 = app.cities[app.hintCity1]
        drawCircle(x1, y1, app.playerCircleR, fill = app.blue, opacity = 50)
    if app.hintCity2 != 'None':
        x2, y2 = app.cities[app.hintCity2]
        drawCircle(x2, y2, app.playerCircleR, fill = app.red, opacity = 50)

def drawScoreBoard(app):
    drawRect(1200, 130, 280, 140, fill = 'black', border = 'white',align='top-left')
    drawRect(1200, 130, 280, 100, fill = 'black', border = 'white',align='top-left')
    drawLabel('Score', 1335, 160, fill='white', size = 20)
    drawLabel(f'P1: {app.p1WinCounter}', 1260, 194, fill='white', size = 20)
    drawLabel(f'P2: {app.p2WinCounter}', 1415, 194, fill='white', size = 20)
    drawLabel(f"Press 's' to reset scores", 1337, 250, fill='white', size=15)

def drawRound(app):
    drawRect(250, 30, 190, 50, fill = 'black', border = 'white')
    drawLabel(f'Round:{app.roundCount}', 370, 55, fill='white', size = 24)

### chat implementation ###
def drawSideText(app):
    #draws the text box
    drawRect(50, 200, 300, 450, fill = 'black', border = 'white',align='top-left')
    drawRect(50, 150, 300, 50, fill = 'black', border = 'white',align='top-left')
    drawRect(50, 700, 150, 50, fill = 'black', border = 'white',align='top-left')
    drawRect(200, 700, 150, 50, fill = 'black', border = 'white',align='top-left')

    drawLabel("'n' = nice!", 85, 720, fill = 'white', size = 20,align='top-left')
    drawLabel("'m' = oops!", 225, 720, fill = 'white', size = 20,align='top-left')

    drawLabel('Chat Box', 200, 175, fill = 'white', size = 30)

    
    #draws the box based off of sideTextGen
    for i in range(len(app.textBox)):
        i = i % 9
        drawRect(50, 600 - (50*i) , 300, 50, fill = 'black', border = 'white',align='top-left')
        drawLabel(app.textBox[i], 85, 625 - (50*i), fill = 'white', size = 18,align='top-left')

def drawHint(app):
    drawRect(980, 30, 500, 110, fill = 'black', border = 'white',align='top-left')
    drawLabel(f'Player 1 last seen: {app.hintCity1}', 1000, 50, size= 24, fill='white',align='top-left')
    drawLabel(f'Player 2 last seen: {app.hintCity2}', 1000, 100, size= 24, fill='white',align='top-left')

def drawPlayers(app):
    drawRect(100, 30, 200, 50, fill = 'black', border = 'white')
    if app.player1Turn == True:
        drawLabel('Player 1 Turn', 200, 55, fill = 'white', size = 24)
        drawCircle(300, 55, 10, fill = app.blue,border='white')
        drawCircle(app.cx0, app.cy0, app.playerCircleR, fill = app.blue)
    else:
        drawLabel('Player 2 Turn', 200, 55, fill = 'white', size = 24)
        drawCircle(300, 55, 10, fill = app.red,border='white')
        drawCircle(app.cx1, app.cy1, app.playerCircleR, fill = app.red)

def drawNextTurn(app):
    if app.paused and not app.nextTurn:
        drawRect(0,0, app.width, app.height, opacity = 100)
        drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
        drawLabel("Oppenent's Turn", app.width/2, app.height/2-30, fill='white',size=25)
        drawLabel("Press 'enter' to continue",app.width/2, app.height/2+20, fill='white',size=25)
    
def drawStrikeResult(app):
    if app.winner == app.player1:
        drawRect(0,0, app.width, app.height, opacity = 50)
        drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
        drawLabel('Player 1 Shoots Player 2!', app.width/2, app.height/2-30, fill='white',size=25)
        drawLabel('Player 1 wins!', app.width/2, app.height/2+15,fill='white', size=25)
        drawLabel("Press 'r' to restart", app.width/2, app.height/2+40,fill='white', size=16)
        

    if app.winner == app.player2:
        drawRect(0,0, app.width, app.height, opacity = 50)
        drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
        drawLabel('Player 2 Shoots Player 1!', app.width/2, app.height/2-30, fill='white',size=25)
        drawLabel('Player 2 wins!', app.width/2, app.height/2+15,fill='white', size=25)
        drawLabel("Press 'r' to restart", app.width/2, app.height/2+40,fill='white', size=16)
    
    if app.miss:
        drawRect(0,0, app.width, app.height, opacity = 50)
        drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
        drawLabel('Target Missed!', app.width/2, app.height/2-30, fill='white',size=25)
        drawLabel("Press 'esc' to continue",app.width/2, app.height/2+20, fill='white',size=25)
    
def onStep(app):
    if app.gameOver:
        return
    
    if app.player1 in app.player2Cities:
        app.hintCity1 = app.player1
    if app.player2 in app.player1Cities:
        app.hintCity2 = app.player2
    
    if app.moveCount == 2 and app.nextTurn == False:
        app.paused = True
    elif app.moveCount == 2 and app.paused == False:
        app.moveCount = 0
        app.player1Turn, app.player2Turn = not app.player1Turn, not app.player2Turn
        app.nextTurn = False
        app.roundIndex += 1
        if app.roundIndex % 2 == 0:
            app.roundCount += 1
    
    if app.miss:
        app.paused = True
    if app.nextMove:
        app.nextMove = False

    if app.roundCount == 10:
        app.gameOver = True
        app.paused = True

def tieCondition(app):
    if app.roundCount == 10:
        if len(app.player1Cities) > len(app.player2Cities):
            app.winner = app.player1
            app.gameOver = True
            app.paused = True
            app.p1WinCounter +=1
        elif len(app.player1Cities) < len(app.player2Cities):
            app.winner = app.player2
            app.gameOver = True
            app.paused = True
            app.p2WinCounter +=1 
        elif len(app.player1Cities) == len(app.player2Cities):
            app.gameOver = True
            app.paused = True



def drawTieCondition(app):
    if app.roundCount == 10:    
        if len(app.player1Cities) > len(app.player2Cities):
            drawRect(0,0, app.width, app.height, opacity = 50)
            drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
            drawLabel('Player 1 Wins by Majority Cities!', app.width/2, app.height/2, fill='white',size=25)
            drawLabel("Press 'r' to restart", app.width/2, app.height/2+40,fill='white', size=16)

        elif len(app.player1Cities) < len(app.player2Cities):
            drawRect(0,0, app.width, app.height, opacity = 50)
            drawRect(app.width/2, app.height/2, 400, 150, align = 'center', border='white', borderWidth=3)
            drawLabel('Player 2 Wins by Majority Cities!', app.width/2, app.height/2, fill='white',size=25)
            drawLabel("Press 'r' to restart", app.width/2, app.height/2+40,fill='white', size=16)

        elif len(app.player1Cities) == len(app.player2Cities):
            drawRect(0,0, app.width, app.height, opacity = 50)
            drawRect(app.width/2, app.height/2, 900, 170, align = 'center', border='white', borderWidth=3)
            drawLabel('Our game was a stalemate... Neither of us won. Yet both of us lost.', app.width/2, app.height/2-30, fill='white',size=25)
            drawLabel('And worse still... that unshakable feeling that nothing was ever really finished.', app.width/2, app.height/2+15,fill='white', size=25)
            drawLabel("Press 'r' to restart", app.width/2, app.height/2+50,fill='white', size=16)

def main():
    runApp(1920, 1080)

main()
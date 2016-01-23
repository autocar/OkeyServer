from random import shuffle
import json
import socket

def Err(msg):
    return json.dumps({"status": 0, "message": msg})

def getHand(s,hand):
    msg = {"status": 1,"cards":[{"color":i[0],"number":i[1]} for i in hand]}
    s.sendall(json.dumps(msg))

def ThrowCard(data, turn, player):
    if not "cards" in data:
        return False, "Parse cards error"
    if len(data['cards']) != 24:
        return False, "Cards amount error"
    return True

def TakeCard(data, turn ,cardStack, discard):
    if not "from" in data:
        return False, "Where to take card?"
    if data['from'] != "deck" and data['from'] != "discard":
        return False, "Wrong place"
    if data['from'] == "deck":
        if len(cardStack) == 0:
            return False, "Deck is already empty"
        newcard = cardStack.pop()
        return True, json.dumps({"status": 1,"card":{"color":newcard[0],"number":newcard[1]}})
    elif data['from'] == "discard":
        if turn == 0:
            LastPlayer = 3
        else:
            LastPlayer = turn - 1
        if len(discard[LastPlayer]) == 0:
            return False,"No cards there"
        newcard = discard[LastPlayer].pop()
        return True, json.dumps({"status": 1,"card":{"color":newcard[0],"number":newcard[1]}})

def RecvDataChk(data,turn):
    if not "player" in data or data['player'] < 1 or data['player'] > 4:
        return False,"Player number fault"
    if data['player'] != turn + 1:
        return False, "Not this player's round"
    if not "action" in data:
        return False, "No action specified"
    return True, ""


def Game(s,logType):
    colors = ["blue","yellow","red","black"]
    cardStack = [(i,j) for i in colors for j in range(1,14)] * 2
    shuffle(cardStack)
    shuffle(cardStack)

    player = []
    discard = [ [],[],[],[] ]
    for i in range(0,4):
        player.append([cardStack.pop() for j in range(0,14)])
        for j in range(0,10):
            player[i].append(("empty",-1))

    turn = 0
    while True:
        gameState = 0
        while True:
            data = json.dumps(s.recv(2048))

            errState,errMsg = RecvDataChk(data,turn)

            if not errState:
                s.sendall(Err(errMsg))
                continue

            if data['action'] == "hand":
                getHand(s,player[turn])
            elif data['action'] == "take":
                if gameState != 0:
                    s.sendall(Err("You've take the card already"))
                    continue
                takeState, takeMsg = TakeCard(data, turn, cardStack, discard)
                if takeState:
                    s.sendall(takeMsg)
                else:
                    s.sendall(Err(takeMsg))
            elif data['action'] == "throw":
                throwState,throwMsg = ThrowCard(data, turn, player)


        if turn == 3:
            turn = 0
        else:
            turn = turn + 1


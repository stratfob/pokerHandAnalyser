import pandas as pd

def historyToHands(textFile):
    hands = textFile.read().split('\n\n')
    return hands    

def getHandNumber(hand):
    index = hand.index('PokerStars Hand #')
    endIndex = hand.find(': ', index)
    index += len('PokerStars Hand #')
    return hand[index:endIndex]

def getDateTime(hand):
    index = hand.index(') - ')
    endIndex = hand.find('\n', index)
    index += len(') - ')
    return hand[index:endIndex]
    
def getAmountPutInBlinds(hand, playerName):
    if playerName + ': posts ' in hand:
        lineIndex = hand.index(playerName + ': posts ') 
        amountIndex = hand.find('$',lineIndex)
        return float(hand[amountIndex+1:hand.find('\n',amountIndex)])
    else:
        return 0.00
    
def streetAction(hand, playerName, streetText):
    try:
        hand = hand[hand.index('*** ' + streetText + ' ***'):hand.index('*** SUMMARY ***')]
        index = hand.index(playerName + ': ')+len(playerName + ': ')
        endIndex = hand.find(' ', index)
        if '\n' in hand[index:endIndex]:
            endIndex = endIndex = hand.find('\n', index)
        
        action = hand[index:endIndex]
        if action == 'doesn\'t' or action == 'shows':
            action = ''
        
        return action
    except:
        return ''


def getAmountPutIn(hand,playerName):
    amount = getAmountPutInBlinds(hand,playerName)
    hand = hand[hand.index('*** HOLE CARDS ***'):hand.index('*** SUMMARY ***')]
    
    lines = hand.split('\n')
    for line in lines:
        if playerName in line:
            line = line.replace (' and is all-in', '')
            if 'calls' in line or 'bets' in line:
                amount += float(line[line.rfind('$')+1:])
            elif 'raises' in line:
                # make sure that previous money put in isn't counted twice
                
                amount += (float(line[line.rfind('$')+1:]) - amount)
            elif 'returned to' in line:
                amount -= float(line[line.rfind('$')+1:line.index(')')])
    return amount   
    
    
def getDealtCards(hand, playerName):
    startIndex = hand.index('Dealt to ' + playerName + ' ')
    startIndex = hand.find('[', startIndex)
    endIndex = hand.find('\n', startIndex)
    return hand[startIndex:endIndex]
    
    
def getStreet(hand, streetText):
    try:
        lineIndex = hand.index('*** ' + streetText + ' ***')
        startIndex = hand.find('[', lineIndex)
        if streetText != 'FLOP':
            startIndex = hand.find('[', startIndex+1)
        endIndex = hand.find('\n', startIndex)
        return hand[startIndex:endIndex]
    except:
        return ''

def getHandWinResult(hand, playerName):
    hand = hand[hand.index('*** SUMMARY ***'):]
    lineWithPlayerIndex = hand.index(playerName) 
    lineWithPlayer = hand[lineWithPlayerIndex:]
    
    if 'folded' in lineWithPlayer:
        return False
    if 'collected' in lineWithPlayer:
        return True
    if 'won' in lineWithPlayer:
        return True
    else:
        return False

def getAmountCollected(hand, playerName):
    hand = hand[hand.index('*** SUMMARY ***'):]
    lineWithPlayerIndex = hand.index(playerName) 
    lineWithPlayer = hand[lineWithPlayerIndex:]
    
    if 'collected' in lineWithPlayer or 'won' in lineWithPlayer:
        return float(lineWithPlayer[lineWithPlayer.index('$')+1:\
                              lineWithPlayer.find(')',lineWithPlayer.index('$'))])
    else:
        return 0.00

def getTablePosition(hand, playerName):
    
    # make more acccurate
    hand = hand[hand.index('*** SUMMARY ***'):]
    lineWithPlayerIndex = hand.index(playerName) 
    lineWithPlayer = hand[lineWithPlayerIndex:]
    if 'button' in lineWithPlayer:
        return 'Button'
    elif 'small blind' in lineWithPlayer:
        return 'Small Blind'
    elif 'big blind' in lineWithPlayer:
        return 'Big Blind'
    else:
        return 'Middle/UTG'
    

    
def main():
    playerName = 'Benzer586'
    
    textFile = open('hand history.txt', 'rt')
    hands = historyToHands(textFile)
    
    myDataFrame = pd.DataFrame(columns = ['handNumber'\
                                          ,'date'\
                                          ,'cards'\
                                          ,'preFlopAction'\
                                          ,'flop'\
                                          ,'flopAction'\
                                          ,'turn'\
                                          ,'turnAction'\
                                          ,'river'\
                                          ,'riverAction'\
                                          ,'win'\
                                          ,'amountCollected'\
                                          ,'position'\
                                          ,'blind'\
                                          ,'amountPutIn'\
                                          ,'profit'])
    #print(hands[0])
    handNumber = 1
    for hand in hands:
        myDataFrame.loc[handNumber] = [getHandNumber(hand)\
                       ,getDateTime(hand)\
                       ,getDealtCards(hand,playerName)\
                       ,streetAction(hand,playerName,'HOLE CARDS')\
                       ,getStreet(hand, 'FLOP')\
                       ,streetAction(hand,playerName,'FLOP')\
                       ,getStreet(hand, 'TURN')\
                       ,streetAction(hand,playerName, 'TURN')\
                       ,getStreet(hand, 'RIVER')\
                       ,streetAction(hand,playerName, 'RIVER')\
                       ,getHandWinResult(hand,playerName)\
                       ,getAmountCollected(hand, playerName)\
                       ,getTablePosition(hand,playerName)\
                       ,getAmountPutInBlinds(hand, playerName)\
                       ,getAmountPutIn(hand, playerName)\
                       ,getAmountCollected(hand, playerName)-getAmountPutIn(hand, playerName)]
        handNumber += 1
    textFile.close()
    
    myDataFrame['profit'].cumsum().plot()
    myDataFrame.to_csv('test.csv')
    
if __name__ == '__main__':
    main()
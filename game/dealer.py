import random
from game.player import Player
from game.cards import Cards, ActionCards,PropertyCards, MoneyCards

class Dealer():
    def __init__(self):
        pass

    def initialiseRentActionCards(self):
        def addART(x):
            return 'ART' + x
        
        rentCardList = ['LbBr'] * 2 + ['OrPk'] * 2+ ['RdYl'] * 2 + ['DbDg'] * 2+['LgBl'] * 2 + ['XX'] * 3
        return list(map(addART,rentCardList))

    def initialiseActionCards(self):
        return ['ASD']*3+['AFD']*3+['ADB']*2+['AJN']*3+['APG']*10+['AIB']*3+['ADC']*3+['AHT']*2+['AHS']*3+['ADR']*2

    def initialiseAllActionCards(self):
        return self.initialiseActionCards() + self.initialiseRentActionCards()

    def initialiseMoneyCards(self):
        return ['M1']*6+['M2']*5+['M3']*3+['M4']*3+['M5']*2+['M10']*1

    def initialisePropertyWildCards(self):
        def addPWC(x):
            return 'PWC' + x
        
        propertyWildCardList = ['XX']*2 + ['RdYl'] * 2 + ['OrPk'] * 2 + ['LbBl'] * 1 + ['DgBl'] * 1 + ['LgBl'] * 1 + ['LbBr'] * 1 + ['DbDg'] * 1
        return list(map(addPWC,propertyWildCardList))

    def initialiseAllPropertyCards(self):
        return self.initialisePropertyCards() + self.initialisePropertyWildCards()

    def initialisePropertyCards(self):
        return ['PBr']*2 + ['PDb']* 2 + ['PLg']*2 + ['PBl'] * 4 + ['POr']*3 + ['PRd'] * 3 + ['PDg'] * 3 + ['PPk'] * 3 + ['PYl'] * 3 + ['PLb'] * 3 
        #Br - c87137ff, Db - 1919a6ff, Lb - 40c4ebff,  Lg - 00ff79ff , Dg - 17a537ff, Rd- ff0000ff, Yl- ffd42aff, Or- fa6b0bff , Pk - e84fe8ff , Bk - 

    def initialiseCards(self):
        self.drawPile = self.initialiseAllActionCards() + self.initialiseMoneyCards() + self.initialiseAllPropertyCards()
        self.discardedCards = []
    
    def shuffleCards(self):
        random.shuffle(self.drawPile)
        # print(self.drawPile)

    def createCardObject(self, id):
        idmap = {'A':ActionCards, 'P':PropertyCards, 'M':MoneyCards}
        return idmap[id[0]](id)

    def distributeCards(self, players):
        for player in players:
            for _ in range(5):
                card = self.createCardObject(self.drawPile.pop())
                player.handCards.append(card)    
            
            print(f'###########User-{player.id}############')
            [print(handcard) for handcard in player.handCards]
        # return players

    # def verifyExchange(self,players, action, playerId, propertyCardId, fromColor):
    #     jsnPresent = input(f'User {playerId} - do you have a JSN card? 1 or 0')
    #     player2 = players.findPlayerById(playerId)
    #     player2.playCard() #TODO - Pass JSN 
    #     if jsnPresent:
    #         print('Cannot go further')
    #         return False

    #     propertySet = self.findPropertySetByColor(fromColor)
    #     if propertySet.isFullSet() and action == 'SD':
    #         return False

    #     return True

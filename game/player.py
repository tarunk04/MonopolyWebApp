from game.cards import PropertySet, MoneyCards, ActionCards
from time import sleep

class Players():
    def __init__(self, numPlayers):
        if not 2<=numPlayers<=5:
            print('Players between 2 and 5 only')
        self.numPlayers = numPlayers
        self.players = []
        for playerNum in range(self.numPlayers):
            self.players.append(Player(playerNum))

    def findPlayerById(self, playerId):
        return [player for player in self.players if player.id == playerId][0]

class Player():
    def __init__(self, id):
        self.name = None
        self.pRoomId = None
        self.id = 'U'+str(id)
        self.handCards = []
        self.exchangeBuffer = []
        self.propertyCollection = []
        self.bankCollection = []
        self.fullSets = 0
        self.cardsToPlay = 3
        self.moneyValue = 0
        self.totalValue = 0
        self.chance = False
        self.chanceNo = -1
        self.initialisePropertyCollection()

    def hasWon(self):
        if self.fullSets >=3:
            return True
        else:
            return False

    def drawCards(self, dealer):
        if len(self.handCards)==0:
            numCards = 5
        else:
            numCards = 2

        self.handCards+= [dealer.createCardObject(dealer.drawPile.pop()) for _ in range(numCards)]

    def initialisePropertyCollection(self):
        colors  = ['Bl','Lg','Lb','Db','Dg','Br','Or','Pk','Yl','Rd']
        self.propertyCollection = [PropertySet(color) for color in colors]

    def findMoneyCardById(self, moneyCardId):
        return [moneyCard for moneyCard in self.bankCollection if moneyCard.id == moneyCardId][0]

    def findEncashedActionCardById(self, actionCardId):
        return [actionCard for actionCard in self.bankCollection if actionCard.id == actionCardId][0]

    def findPropertySetByColor(self, color):
        return [propertySet for propertySet in self.propertyCollection if propertySet.color == color][0]

    def findActionCardById(self, actionCardId): #Only for House Hotel actionCard . Not very sure whether to keep this or not
        if actionCardId[1:3] == 'HT':
            return [propertySet.hotel for propertySet in self.propertyCollection if propertySet.hotel.id == actionCardId][0]

        elif actionCardId[1:3] == 'HS':
            return [propertySet.house for propertySet in self.propertyCollection if propertySet.house.id == actionCardId][0]

        else:
            print('Action card should have been house or hotel')

    def arrangeWildCard(self, propertyCardId, fromColor, toColor):
        fromPropertySet = self.findPropertySetByColor(fromColor)
        toPropertySet = self.findPropertySetByColor(toColor)

        propertyCard = fromPropertySet.findPropertyCardById(propertyCardId)
        fromPropertySet.remove(propertyCard)
        toPropertySet.append(propertyCard)

    def PassGo(self, dealer):
        self.drawCards(dealer)

    def House(self,actionCard):
        toColor = input('Enter the color of the property Set to which the House is to be added.')
        propertySet = self.findPropertySetByColor(toColor)
        if propertySet.addHouse(actionCard):
            self.totalValue += actionCard.value

    def Hotel(self,actionCard):
        toColor = input('Enter the color of the property Set to which the Hotel is to be added.')
        propertySet = self.findPropertySetByColor(toColor)
        if propertySet.addHotel(actionCard):
            self.totalValue+= actionCard.value
    
    def DealBreaker(self, players):
        playerId = input('Enter the user ID')
        fromColor = input('Enter the set color')
        self.requestCard(players, playerId = playerId, fromColor = fromColor) #asks and arranges card on successful request
        
    def SlyDeal(self, players):
        playerId = input('Enter the user ID')
        fromColor = input('Enter the set color')
        propertyCardId = input('Enter the id of the property Card')
        self.requestCard(players, playerId = playerId, propertyCardId = propertyCardId, fromColor = fromColor)

    def ForcedDeal(self, players):
        playerId = input('Enter the player ID')
        takePropertyColor = input('Enter the set color from which to take the property')
        takePropertyCardId = input('Enter the id of the property Card to take')
        givePropertyColor = input('Enter the set color from which to give the property')
        givePropertyCardId = input('Enter the id of the property Card to give')
        success = self.requestCard(players, playerId = playerId, propertyCardId = takePropertyCardId, fromColor = takePropertyColor)
        # if success:
        player = players.findPlayerById(playerId)
        player.requestCard(players, playerId= self.id, propertyCardId = givePropertyCardId,fromColor = givePropertyColor)

    def DebtCollector(self, players):
        playerId = input('Enter the player ID')
        self.requestCard(players, playerId=playerId, money = 5)

    def ItsMyBirthday(self, players):
        self.requestCard(players, money= 2)

    def RentCard(self, actionCard, dealer, players):
        doubleRent = False
        if self.chanceNo < self.cardsToPlay:
            if 'ADR' in [card.id for card in self.handCards]:
                if int(input('Do you want to play double the rent? 1 for yes')):
                    doubleRentCard = [card for card in self.handCards if card.id=='ADR'][0]
                    dealer.discardedCards.append(doubleRentCard.id)
                    self.handCards.remove(doubleRentCard)
                    self.chanceNo += 1
                    doubleRent = True
        propertyColor = input('Enter the set color for which to take the rent.')
        propertySet = self.findPropertySetByColor(propertyColor)
        moneyToAsk = propertySet.currentRent()
        if doubleRent:
            moneyToAsk*=2

        print(f'User {self.id} wants {moneyToAsk} money.')
        if actionCard.id == 'ARTXX':
            playerId = input('Enter the id of the player from whom to take the rent')
            self.requestCard(players, playerId = playerId, money = moneyToAsk)
            return True
        
        self.requestCard(players, money = moneyToAsk)
        return True


    def requestPropertySet(self, player, propertySet):
        if not propertySet.isFullSet():
            print('The property set is not complete. Cannot use deal breaker!!')
            return 0
        jsn = player.wantToPlayJSN()
        if not jsn:
            for _ in range(propertySet.currentSetSize()):
                self.exchangeBuffer.append(propertySet.propertyCards.pop())

            if propertySet.hotel:
                self.exchangeBuffer.append(propertySet.hotel)
                propertySet.hotel = None
            if propertySet.house:
                self.exchangeBuffer.append(propertySet.house)
                propertySet.house = None
            return True
        else:
            print('Handle JSN Case') 
            jsnCard = [card for card in player.handCards if card.id == 'AJN'][0]
            player.handCards.remove(jsnCard)
            return False

    def requestPropertyCard(self, player,propertySet, propertyCard):
        jsn = player.wantToPlayJSN()
        if not jsn:
            propertySet.propertyCards.remove(propertyCard)
            player.totalValue -= propertyCard.value
            self.totalValue += propertyCard.value
            self.exchangeBuffer.append(propertyCard)
            return True
        else:
            print('Handle JSN Case') 
            jsnCard = [card for card in player.handCards if card.id == 'AJN'][0]
            player.handCards.remove(jsnCard)
            return False
        
    def enoughMoney(self, money, valueCollected):
        if valueCollected >= money:
            return True
        return False

    def noCardsLeft(self):
        if len(self.bankCollection)==0 and not any([len(propertySet.propertyCards) >0 for propertySet in self.propertyCollection]):
            return True
        
        return False

    def giveMoney(self, player, money): #Self - Player giving money, player - player receiving money
        if self.moneyValue < money:
            print('Cannot be paid through money only')
        elif self.totalValue < money:
            print('Need to give all cards except PWCXX')
        else:
            print('Only money enough')

        self.showBankCollection()
        self.showPropertyCollection()

        # cardsToGive = []
        valueCollected = 0
        while not self.noCardsLeft() and not self.enoughMoney(money, valueCollected):
            cardToGiveId = input('Enter what cardID to give:')
            if cardToGiveId[0] == 'M':
                cardToGive = self.findMoneyCardById(cardToGiveId)
                self.bankCollection.remove(cardToGive)
                self.moneyValue-= cardToGive.value
                valueCollected += cardToGive.value
                player.exchangeBuffer.append(cardToGive)

            elif cardToGiveId[0] == 'P':
                cardToGiveSetColor = input('Enter the color of the set from which to take the property card')
                cardToGiveSet = self.findPropertySetByColor(cardToGiveSetColor)
                cardToGive = cardToGiveSet.findPropertyCardById(cardToGiveId)
                cardToGiveSet.removePropertyCard(cardToGive)
                valueCollected += cardToGive.value
                player.exchangeBuffer.append(cardToGive)

            elif cardToGiveId[0] == 'A':
                fromPropertySet = int(input('Enter where to pick the card from? Bank (0) or Porperty Set (1)'))
                if not fromPropertySet:
                    cardToGive = self.findEncashedActionCardById(cardToGiveId)
                    self.bankCollection.remove(cardToGive)
                    self.moneyValue-= cardToGive.value
                    valueCollected += cardToGive.value
                    player.exchangeBuffer.append(cardToGive)

                else: 
                    cardToGiveSetColor = input('Enter the color of the set from which to take the property card')
                    cardToGiveSet = self.findPropertySetByColor(cardToGiveSetColor)
                    cardToGive = cardToGiveSet.findActionCardById(cardToGiveId)
                    cardToGiveSet.removePropertyCard(cardToGive)
                    self.totalValue -= cardToGive.value
                    valueCollected += cardToGive.value
                    player.exchangeBuffer.append(cardToGive)
    
        #Choose cards and give
    def showExchangeBuffer(self):
        print('Exchange Buffer: ')
        for card in self.exchangeBuffer:
            print(card, end=' ')
        print()

    def arrangeCards(self, players):
        # print('+++++++++++++++++++')
        self.showExchangeBuffer()
        if len(self.exchangeBuffer)!= 0:
            # print('The length of exchangeBuffer is', len(self.exchangeBuffer))
            for card in self.exchangeBuffer:
                # print(card)
                # self.showExchangeBuffer()
                if isinstance(card, ActionCards):
                    card.playCard(self, None, players)
                else:
                    card.playCard(self)
            self.exchangeBuffer.clear()
        
        # #For debugging only
        # print('Debugging only')
        # self.showExchangeBuffer()
        # print('+++++++++++++++++++')

        while True:
            self.showPropertyCollection()
            arrange = int(input('Wish to arrange?Property(1) or Hotel/House(2) or None(-1)'))
            if arrange == -1:
                # self.showBankCollection()
                # self.showPropertyCollection()
                break
            
            elif arrange == 1:
                pickPropertyColor = input('Enter the set color from which to pick the property')
                pickPropertyCardId = input('Enter the id of the property Card to pick')
                keepPropertyColor = input('Enter the set color from which to keep the property')
                
                pickPropertySet = self.findPropertySetByColor(pickPropertyColor)
                keepPropertySet = self.findPropertySetByColor(keepPropertyColor)
                pickPropertyCard = pickPropertySet.findPropertyCardById(pickPropertyCardId)
                pickPropertySet.removePropertyCard(pickPropertyCard)
                keepPropertySet.addPropertyCard(pickPropertyCard)
                
            elif arrange == 2:
                pickPropertyColor = input('Enter the set color from which to pick the property')
                pickPropertyCardId = input('Enter the id of the property Card to pick')
                keepPropertyColor = input('Enter the set color from which to keep the property')
                
                hotel = input('Enter 1 for hotel and 0 for house')
                if hotel:
                    pickPropertySet = self.findPropertySetByColor(pickPropertyColor)
                    keepPropertySet = self.findPropertySetByColor(keepPropertyColor)
                    pickActionCard = pickPropertySet.removeHotel()
                    keepPropertySet.addHotel(pickActionCard)
                else:
                    pickPropertySet = self.findPropertySetByColor(pickPropertyColor)
                    keepPropertySet = self.findPropertySetByColor(keepPropertyColor)
                    pickActionCard = pickPropertySet.removeHouse()
                    keepPropertySet.addHouse(pickActionCard)

    def wantToPlayJSN(self):
        if 'AJN' in [card.id for card in self.handCards]:
            return int(input(f'Do you, player {self.id}, want to play JSN? 1 or 0'))
        return 0

    def requestMoney(self, player, money):
        jsn = player.wantToPlayJSN()
        if not jsn:
            # self.exchangeBuffer = player.giveMoney(self, money)
            player.giveMoney(self, money)
            for card in self.exchangeBuffer:
                player.totalValue -= card.value
                self.totalValue += card.value
                if isinstance(card, MoneyCards) or (isinstance(card, ActionCards) and card.isCashed):
                    player.moneyValue -= card.value
                    self.moneyValue += card.value
            return True
        else:
            print('Handle JSN Case') 
            jsnCard = [card for card in player.handCards if card.id == 'AJN'][0]
            player.handCards.remove(jsnCard)
            return False

    def requestCard(self, players, playerId=None, propertyCardId=None, fromColor=None,money = None):
        if propertyCardId and fromColor and playerId: #PropertyCard from a particular player. Eg - SlyDeal/ ForcedDeal
            print('Expected SD or Fd')
            player = players.findPlayerById(playerId)
            propertySet = player.findPropertySetByColor(fromColor)
            propertyCard = propertySet.findPropertyCardById(propertyCardId)
            if self.requestPropertyCard(player,propertySet, propertyCard): #Returns true or false. In case of True, the exchange buffer of the player is filled with the required cards. He can then arrange the acquired cards.
                self.arrangeCards(players)
                #Arrange cards
                # pass

        elif fromColor and playerId: #Property Set from a particular player. Eg - DealBreaker
            player = players.findPlayerById(playerId)
            propertySet = player.findPropertySetByColor(fromColor)
            if self.requestPropertySet(player, propertySet):
                #Arrange Cards
                self.arrangeCards(players)
                # pass

        elif money and playerId: #Money from a particular player. Eg - Multicolor Rent/ DebtCollector
            player = players.findPlayerById(playerId)
            if self.requestMoney(player, money):
                #Arrange Cards
                self.arrangeCards(players)
                # pass

        elif money:
            for player in players.players:
                if player.id == self.id:
                    continue #Don't collect rent from one self
                print(f'Player - {player.id} turn to pay rent to {self.id}.')
                self.requestMoney(player, money)
            if len(self.exchangeBuffer)>0:
                #Arrange Cards
                self.arrangeCards(players)
                # pass

    def showPropertyCollection(self):
        print('Property:', end= ' ')
        for propertySet in self.propertyCollection:
            if len(propertySet.propertyCards) == 0:
                continue
            print(f'Color - {propertySet.color}: ', end = ' ')
            for propertyCard in propertySet.propertyCards:
                print(propertyCard.id, end = ' ')
            if propertySet.isFullSet():
                print('(FullSet)', end = ' ')
            if propertySet.house:
                print('(+House)', end = ' ')
            if propertySet.hotel:
                print('(+Hotel)', end = ' ')                
            print(end = ', ')
        print()
    
    def showBankCollection(self):
        print('Money:', end=' ')
        for card in self.bankCollection:
            print(card, end= ' ')
        print()

    def showHandCards(self):
        print('Cards you have: ')
        for i, card in enumerate(self.handCards):
            print(i, card)

    def discardCards(self,drawPile):
        extraCards = len(self.handCards) - 7
        self.showHandCards()
        for _ in range(extraCards):
            removeIndex = int(input('Which Card to remove?'))
            drawPile.insert(0,self.handCards.pop(removeIndex)) 

    def playCard(self,socketio = None, dealer = None, players= None,  card = None):
        #TODO Automatically play the card specified and don't ask the user.
        if self.chanceNo == 1:
            self.showPropertyCollection()
            self.showBankCollection()        
        self.showHandCards()

        playIndex =-2
        def setValue(data):
            nonlocal playIndex
            playIndex = int(data['value'])
            print(f'Received Value: {playIndex}')

        socketio.emit('take_input',{},room=self.pRoomId, callback= setValue)
        while playIndex==-2:
            print('Waiting for input')
            sleep(1)
            continue
        # playIndex = int(input('Which card to Play? -1 to pass.'))
        #TODO Take input from JS
        if playIndex == -1:
            return -1

        if isinstance(self.handCards[playIndex], ActionCards):
            self.handCards[playIndex].playCard(self, dealer = dealer, players = players)
        else:
            self.handCards[playIndex].playCard(self)
        playedCard = self.handCards.pop(playIndex)
        dealer.discardedCards.append(playedCard.id)
        self.showPropertyCollection()
        self.showBankCollection()
        return 0
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

    def json_game_data(self):
        return {'players': { player.id: {
                    'chance':player.chance,
                    'chance_no':player.chanceNo,
                    'username':player.name,
                    'proom_id':player.pRoomId,            
                    'moneyValue':player.moneyValue,
                    'totalValue':player.totalValue,
                    'bank_collection':[card.id for card in player.bankCollection],
                    'property_collection':{propertySet.color:propertySet.getAllCards() for propertySet in player.propertyCollection}
                    } for player in self.players}
                }

class Player():
    def __init__(self, id):
        self.name = None
        self.pRoomId = None
        self.roomId = None
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
        self.jsnPlayed = False
        self.doubleRent = False
        self.initialisePropertyCollection()

    def hasWon(self):
        # if self.fullSets >=3:
        if sum([propertySet.isFullSet() for propertySet in self.propertyCollection]) >=3:
            return True
        else:
            return False

    def drawCards(self, dealer):
        if len(self.handCards)==0:
            numCards = 5
        else:
            numCards = 2

        try:
            self.handCards+= [dealer.createCardObject(dealer.drawPile.pop()) for _ in range(numCards)]
        except Exception as e:
            print(f"Error occured in drawing cards: {e}")
            return False
        return True

    def initialisePropertyCollection(self):
        colors  = ['Bl','Lg','Lb','Db','Dg','Br','Or','Pk','Yl','Rd','XX'] #Added extra color bin
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

    def json_player_data(self):
        return {'id':self.id,
        'chance':self.chance,
        'name':self.name,
        'proom_id':self.pRoomId,
        'handcards':[card.id for card in self.handCards]}

    def json_player_collection_data(self):
        return {'moneyValue':self.moneyValue,
                    'totalValue':self.totalValue,
                    'bank_collection':[card.id for card in self.bankCollection],
                    'property_collection':{propertySet.color:propertySet.getAllCards() for propertySet in self.propertyCollection} 
                }

    def arrangeWildCard(self, propertyCardId, fromColor, toColor):
        fromPropertySet = self.findPropertySetByColor(fromColor)
        toPropertySet = self.findPropertySetByColor(toColor)

        propertyCard = fromPropertySet.findPropertyCardById(propertyCardId)
        fromPropertySet.remove(propertyCard)
        toPropertySet.append(propertyCard)

    def PassGo(self, dealer, socketio):
        if not self.drawCards(dealer):
            return False
        self.sendMessageToAll(f'{self.name} played a PassGo.',socketio)
        return True

    def House(self,actionCard, players, socketio):
        if not any([propertySet.isFullSet() for propertySet in self.propertyCollection]):
            self.sendMessageToPlayer('No full set present!!!', socketio)
            print("No full set to take!!!")
            return False
        self.sendMessageToPlayer('Choose the color of the property Set to which the House is to be added.', socketio)
        receivedData = self.modified_input('choose_own_set', socketio)
        toColor = receivedData['color']
        # toColor = input('Enter the color of the property Set to which the House is to be added.')
        propertySet = self.findPropertySetByColor(toColor)
        if not propertySet.addHouse(actionCard):
            return False
        self.totalValue += actionCard.value
        self.sendMessageToAll(f'{self.name} added a House to {toColor} set.',socketio)
        return True

    def Hotel(self,actionCard, players, socketio):
        if not any([propertySet.isFullSet() for propertySet in self.propertyCollection]):
            self.sendMessageToPlayer('No full set present!!!', socketio)
            print("No full set present!!!")
            return False
        self.sendMessageToPlayer('Choose the color of the property Set to which the Hotel is to be added.', socketio)
        receivedData = self.modified_input('choose_own_set', socketio)
        toColor = receivedData['color']
        # toColor = input('Enter the color of the property Set to which the Hotel is to be added.')
        propertySet = self.findPropertySetByColor(toColor)
        if not propertySet.addHotel(actionCard):
            return False
        self.totalValue+= actionCard.value
        self.sendMessageToAll(f'{self.name} added a House to {toColor} set.',socketio)
        return True
    
    def DealBreaker(self, players, socketio):
        if not any([propertySet.isFullSet() for player in players.players for propertySet in player.propertyCollection  if player.id != self.id]):
            self.sendMessageToPlayer('No full set to take!!!', socketio)
            print("No full set to take!!!")
            return False
        # playerId = input('Enter the user ID')
        # fromColor = input('Enter the set color')
        receivedData = self.modified_input('choose_others_set', socketio)
        playerId = receivedData['playerId']
        fromColor = receivedData['color']
        self.sendMessageToAll(f'DealBreaker played. {self.name} wants {fromColor} set from {playerId}.', socketio)
        if not self.requestCard(players, playerId = playerId, fromColor = fromColor, socketio= socketio): #asks and arranges card on successful request
            return False
        return True
        
    def SlyDeal(self, players, socketio):
        if not any([len(propertySet.propertyCards)> 0 for player in players.players for propertySet in player.propertyCollection]): #NOTE this
            self.sendMessageToPlayer('No property to take!!!', socketio)
            print('No property to take !!!')
            return False
        # playerId = input('Enter the user ID')
        # fromColor = input('Enter the set color')
        receivedData = self.modified_input('choose_others_property', socketio)
        propertyCardId = receivedData['value']
        playerId = receivedData['playerId']
        fromColor = receivedData['color']
        # propertyCardId = input('Enter the id of the property Card')
        self.sendMessageToAll(f'SlyDeal Played. {self.name} wants a {propertyCardId} property from {playerId}.', socketio)
        if not self.requestCard(players, playerId = playerId, propertyCardId = propertyCardId, fromColor = fromColor, socketio=socketio):
            return False
        return True

    def ForcedDeal(self, players, socketio):
        if not any([len(propertySet.propertyCards) >0 for propertySet in self.propertyCollection]):
            self.sendMessageToPlayer('No property to give.', socketio)
            print('No property to give!!!')
            return False

        if not any([len(propertySet.propertyCards)> 0 for player in players.players for propertySet in player.propertyCollection if player.id != self.id]): #NOTE this
            self.sendMessageToPlayer('No property to take.', socketio)
            print('No property to take !!!')
            return False

        receivedData = self.modified_input('choose_others_property', socketio)
        # playerId = input('Enter the player ID')
        # takePropertyColor = input('Enter the set color from which to take the property')
        # takePropertyCardId = input('Enter the id of the property Card to take')
        takePropertyCardId = receivedData['value']
        playerId = receivedData['playerId']
        takePropertyColor = receivedData['color']
        # givePropertyColor = input('Enter the set color from which to give the property')
        # givePropertyCardId = input('Enter the id of the property Card to give')
        receivedData = self.modified_input('choose_own_property', socketio)
        givePropertyCardId = receivedData['value']
        givePropertyColor = receivedData['color']
        
        self.sendMessageToAll(f'ForcedDeal Played. {self.name} wants a {takePropertyCardId} property in exchange of {givePropertyCardId} property from {playerId}.', socketio)

        if not self.requestCard(players, playerId = playerId, propertyCardId = takePropertyCardId, fromColor = takePropertyColor, socketio=socketio):
            return False
        # if success:
        if self.jsnPlayed:
            self.jsnPlayed = False
            return True
        player = players.findPlayerById(playerId)
        if not player.requestCard(players, playerId= self.id, propertyCardId = givePropertyCardId,fromColor = givePropertyColor, socketio= socketio):
            print('Atomicity to be handled') #TODO:
            return False
        return True

    def DebtCollector(self, players, socketio):
        # playerId = input('Enter the player ID')
        if len(players.players) == 2:
            playerId  = [player.id for player in players.players if self.id != player.id][0]
        else:
            self.sendMessageToPlayer('Choose the player from whom you want to collect $5 M.', socketio)
            receivedData = self.modified_input('choose_player', socketio)
            playerId = receivedData['playerId']
        
        self.sendMessageToAll(f'DebtCollector Played. {self.name} wants $5 M from {playerId}.', socketio)

        if not self.requestCard(players, playerId=playerId, money = 5,socketio= socketio):
            return False
        return True

    def ItsMyBirthday(self, players, socketio): #Although not required
        self.sendMessageToAll(f"It is {self.name}'s birthday. Hand him a $2 M gift.", socketio)
        if not self.requestCard(players, money= 2, socketio= socketio):
            return False
        return True

    def RentCard(self, actionCard, dealer, players, socketio):
        if actionCard.id[3:5] == "XX":
            # propertyColor = input('Enter the set color for which to take the rent.')
            self.sendMessageToPlayer('Choose the set color for which to take the rent.', socketio)
            receivedData = self.modified_input('choose_own_set', socketio)
            propertyColor = receivedData['color']
        else:
            propertyColor1, propertyColor2 = actionCard.id[3:5], actionCard.id[5:7]
            if self.findPropertySetByColor(propertyColor1).currentSetSize()>0 and self.findPropertySetByColor(propertyColor2).currentSetSize()>0:
                receivedData = self.modified_input('choose_value', socketio, dataToSend = {'message':'Choose the color code of the property set for which you want the rent: ','0':propertyColor1,'1':propertyColor2})
                propertyColorIndex = int(receivedData['value'])
                # propertyColorIndex = int(input(f'Choose the color code of the property set where you would like to add this card: 0 for {propertyColor1}, 1 for {propertyColor2}')) #TODO:
                propertyColor = propertyColor1 if propertyColorIndex == 0 else propertyColor2
            elif self.findPropertySetByColor(propertyColor1).currentSetSize()>0:
                propertyColor = propertyColor1
            elif self.findPropertySetByColor(propertyColor2).currentSetSize()>0:
                propertyColor = propertyColor2
            else:
                self.sendMessageToPlayer('No poperty card of any of these colours!!!!',socketio)
                print('No poperty card of any of these colours!!!!')
                return False

        if self.chanceNo < self.cardsToPlay:
            if 'ADR' in [card.id for card in self.handCards]:
                receivedData = self.modified_input('choose_value', socketio, dataToSend = {'message':'Do you want to play double the rent?:','0':'No','1':'Yes'})
                if int(receivedData['value']):
                # int(input('Do you want to play double the rent? 1 for yes')):
                    self.doubleRent = True
        propertySet = self.findPropertySetByColor(propertyColor)
        moneyToAsk = propertySet.currentRent()

        message = f'Rent Card played for property {propertyColor}'
        if self.doubleRent:
            moneyToAsk*=2
            message+=' with double rent'
        message += '.'
        print(f'User {self.id} wants {moneyToAsk} money.')
        message +=f'User {self.name} wants ${moneyToAsk} M '
        if actionCard.id == 'ARTXX':
            if len(players.players) == 2:
                playerId  = [player.id for player in players.players if self.id != player.id][0]
            else:
                receivedData = self.modified_input('choose_player', socketio)
                playerId = receivedData['playerId']
                # playerId = input('Enter the id of the player from whom to take the rent')
            message += f'from {playerId}.'
            self.sendMessageToAll(message,socketio)
            if not self.requestCard(players, playerId = playerId, money = moneyToAsk, socketio= socketio):
                return False
            return True
        message+= 'from everyone.'
        self.sendMessageToAll(message, socketio)
        if not self.requestCard(players, money = moneyToAsk, socketio= socketio):
            return False #TODO: Atomicity
        return True


    def requestPropertySet(self, player, propertySet, socketio):
        if not propertySet.isFullSet():
            print('The property set is not complete. Cannot use deal breaker!!')
            return 0
        jsn = player.wantToPlayJSN(socketio)
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
            self.sendMessageToAll(f'Player {player.name} played a Just Say No.', socketio)
            print('Handle JSN Case') 
            jsnCard = [card for card in player.handCards if card.id == 'AJN'][0]
            player.handCards.remove(jsnCard)
            return False

    def requestPropertyCard(self, player,propertySet, propertyCard, socketio):
        jsn = player.wantToPlayJSN(socketio)
        if not jsn:
            propertySet.propertyCards.remove(propertyCard)
            player.totalValue -= propertyCard.value
            # self.totalValue += propertyCard.value
            self.exchangeBuffer.append(propertyCard)
            return True
        else:
            self.sendMessageToAll(f'Player {player.name} played a Just Say No.', socketio)
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

    def giveMoney(self, player, money, socketio): #Self - Player giving money, player - player receiving money
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
            # cardToGiveId = input('Enter what cardID to give:')
            receivedData = self.modified_input('choose_own_card', socketio)
            cardToGiveId = receivedData['value'] #value, color, collection
            if cardToGiveId[0] == 'M':
                cardToGive = self.findMoneyCardById(cardToGiveId)
                self.bankCollection.remove(cardToGive)
                # self.moneyValue-= cardToGive.value
                valueCollected += cardToGive.value
                player.exchangeBuffer.append(cardToGive)

            elif cardToGiveId[0] == 'P':
                cardToGiveSetColor = receivedData['color']
                # cardToGiveSetColor = input('Enter the color of the set from which to take the property card')
                cardToGiveSet = self.findPropertySetByColor(cardToGiveSetColor)
                cardToGive = cardToGiveSet.findPropertyCardById(cardToGiveId)
                cardToGiveSet.removePropertyCard(cardToGive)
                valueCollected += cardToGive.value
                player.exchangeBuffer.append(cardToGive)

            elif cardToGiveId[0] == 'A':
                fromPropertySet = 0 if receivedData['collection'] == 'bankCollection' else 1
                # fromPropertySet = int(input('Enter where to pick the card from? Bank (0) or Porperty Set (1)'))
                if not fromPropertySet:
                    cardToGive = self.findEncashedActionCardById(cardToGiveId)
                    self.bankCollection.remove(cardToGive)
                    # self.moneyValue-= cardToGive.value
                    valueCollected += cardToGive.value
                    player.exchangeBuffer.append(cardToGive)

                else: 
                    cardToGiveSetColor = receivedData['color']
                    # cardToGiveSetColor = input('Enter the color of the set from which to take the property card')
                    cardToGiveSet = self.findPropertySetByColor(cardToGiveSetColor)
                    cardToGive = cardToGiveSet.findActionCardById(cardToGiveId)
                    cardToGiveSet.removePropertyCard(cardToGive)
                    # self.totalValue -= cardToGive.value
                    valueCollected += cardToGive.value
                    player.exchangeBuffer.append(cardToGive)

            socketio.emit('player_collection_data',self.json_player_collection_data(), room = self.pRoomId)
            self.sendMessageToPlayer(f'Value collected: {valueCollected} (out of {money}).', socketio)
        
        #Choose cards and give
    def showExchangeBuffer(self):
        print('Exchange Buffer: ')
        for card in self.exchangeBuffer:
            print(card, end=' ')
        print()

    def arrangeExchangeBuffer(self, players, socketio):
        self.showExchangeBuffer()
        if len(self.exchangeBuffer)!= 0:
            # print('The length of exchangeBuffer is', len(self.exchangeBuffer))
            for card in self.exchangeBuffer:
                # print(card)
                # self.showExchangeBuffer()
                if isinstance(card, ActionCards):
                    card.playCard(self, None, players, socketio)
                else:
                    card.playCard(self, socketio)
            self.exchangeBuffer.clear()
        
        # #For debugging only
        # print('Debugging only')
        # self.showExchangeBuffer()
        # print('+++++++++++++++++++')

    def arrangeCards(self, players, socketio):
        # print('+++++++++++++++++++')
        while True:
            self.showPropertyCollection()
            # arrange = int(input('Wish to arrange?Property(1) or Hotel/House(2) or None(-1)'))
            arrange = 1 #TODO: Hardcoded for now
            
            if arrange == 1:
                receivedData = self.modified_input('choose_own_property', socketio)
                pickPropertyCardId = receivedData['value']
                pickPropertyColor = receivedData['color']
                # pickPropertyColor = input('Enter the set color from which to pick the property')
                # pickPropertyCardId = input('Enter the id of the property Card to pick')
                #HERE
                if not pickPropertyCardId[1:3] == 'WC':
                    keepPropertyColor = pickPropertyCardId[1:3]
                elif pickPropertyCardId[3:5] == 'XX':
                    # color = input('Enter the color code of the property set where you would like to add this card: ')
                    receivedData = self.modified_input('choose_own_set', socketio)
                    keepPropertyColor = receivedData['color']
                else:
                    color1, color2 = pickPropertyCardId[3:5], pickPropertyCardId[5:7]
                    receivedData = self.modified_input('choose_value', socketio, dataToSend = {'message':'Choose the color code of the property set where you would like to add this card','0':color1,'1':color2})
                    colorIndex = int(receivedData['value'])
                    # colorIndex = int(input(f'Choose the color code of the property set where you would like to add this card: 0 for {color1}, 1 for {color2}'))
                    keepPropertyColor = color1 if colorIndex == 0 else color2

                # propertySet = self.findPropertySetByColor(keepPropertyColor)
                # if not propertySet.addPropertyCard(self):#Some error in adding property - Full set
                #     # Try adding it to XX:
                #     mixedPropertySet = self.findPropertySetByColor('XX')
                #     if not mixedPropertySet.addPropertyCard(self):
                #         return False
                # player.totalValue += self.value #Arranging doesn't change values
                # return True
                ###############
                # receivedData =self.modified_input('choose_own_set', socketio)
                # keepPropertyColor = receivedData['color']
                # keepPropertyColor = input('Enter the set color from which to keep the property')
                
                pickPropertySet = self.findPropertySetByColor(pickPropertyColor)
                keepPropertySet = self.findPropertySetByColor(keepPropertyColor)
                pickPropertyCard = pickPropertySet.findPropertyCardById(pickPropertyCardId)
                pickPropertySet.removePropertyCard(pickPropertyCard)
                keepPropertySet.addPropertyCard(pickPropertyCard)
                
            elif arrange == 2:
                pickPropertyColor = input('Enter the set color from which to pick the property')
                # pickPropertyCardId = input('Enter the id of the property Card to pick')
                keepPropertyColor = input('Enter the set color in which to keep the property')
                
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

            break

    def wantToPlayJSN(self, socketio):
        if 'AJN' in [card.id for card in self.handCards]:
            receivedData = self.modified_input('choose_value', socketio, dataToSend = {'message':'Do you want to play JSN?','0':'No','1':'Yes'}) # returns {'value':1/0}
            return int(receivedData['value'])
            # return int(input(f'Do you, player {self.id}, want to play JSN? 1 or 0'))
        return 0

    def requestMoney(self, player, money, socketio):
        jsn = player.wantToPlayJSN(socketio)
        if not jsn:
            # self.exchangeBuffer = player.giveMoney(self, money)
            player.giveMoney(self, money, socketio)
            for card in self.exchangeBuffer:
                player.totalValue -= card.value
                # self.totalValue += card.value #Handled in exchangeBuffer -> card.playCard
                if isinstance(card, MoneyCards) or (isinstance(card, ActionCards) and card.isCashed):
                    player.moneyValue -= card.value
                    # self.moneyValue += card.value #Handled in exchangeBuffer -> card.playCard
            return True
        else:
            self.sendMessageToAll(f'Player {player.name} played a Just Say No.', socketio)
            print('Handle JSN Case') 
            jsnCard = [card for card in player.handCards if card.id == 'AJN'][0]
            player.handCards.remove(jsnCard)
            return False

    def requestCard(self, players, playerId=None, propertyCardId=None, fromColor=None,money = None, socketio = None):
        if propertyCardId and fromColor and playerId: #PropertyCard from a particular player. Eg - SlyDeal/ ForcedDeal
            print('Expected SD or Fd')
            player = players.findPlayerById(playerId)
            propertySet = player.findPropertySetByColor(fromColor)
            propertyCard = propertySet.findPropertyCardById(propertyCardId)
            try:
                jsnSafe = self.requestPropertyCard(player,propertySet, propertyCard, socketio) #Returns true or false. In case of True, the exchange buffer of the player is filled with the required cards. He can then arrange the acquired cards. In case of false, Just Say No has been played against the player.
                if not jsnSafe:
                    self.jsnPlayed = True
            except Exception as e:
                print(f'Some error occured while requesting card: {e}')
                return False
                #Arrange cards
                # pass

        elif fromColor and playerId: #Property Set from a particular player. Eg - DealBreaker
            player = players.findPlayerById(playerId)
            propertySet = player.findPropertySetByColor(fromColor)
            try:
                self.requestPropertySet(player, propertySet, socketio)
                #Arrange Cards
            except Exception as e:
                print(f'Some error occured while requesting card: {e}')
                return False
                # pass

        elif money and playerId: #Money from a particular player. Eg - Multicolor Rent/ DebtCollector
            player = players.findPlayerById(playerId)
            try:
                self.requestMoney(player, money, socketio)
                #Arrange Cards
            except Exception as e:
                print(f'Some error occured while requesting card: {e}')
                return False
                # pass

        elif money:
            for player in players.players:
                if player.id == self.id:
                    continue #Don't collect rent from one self
                player.sendMessageToAll(f'Player - {player.name} turn to pay rent to {self.name}.',socketio)
                print(f'Player - {player.id} turn to pay rent to {self.id}.')
                try:
                    self.requestMoney(player, money, socketio)
                except Exception as e:
                    print(f'Some error occured while requesting card: {e}')
                    return False
            # if len(self.exchangeBuffer)>0:
            #     #Arrange Cards
            #     self.arrangeCards(players, socketio)
                # pass
        self.arrangeExchangeBuffer(players, socketio)
        return True

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

    def discardCards(self,drawPile, socketio):
        extraCards = len(self.handCards) - 7
        self.showHandCards()
        for _ in range(extraCards):
            removeIndex = int(self.modified_input('take_input', socketio)['value'])
            # removeIndex = int(input('Which Card to remove?'))
            drawPile.insert(0,self.handCards.pop(removeIndex).id) 

    def sendMessageToPlayer(self,message, socketio):
        socketio.emit('notification',message, room=self.pRoomId)

    def sendMessageToAll(self, message, socketio):
        socketio.emit('notification', message , room = self.roomId)

    def clearMessage(self, socketio):
        socketio.emit('notification', '' , room = self.roomId)
        
    def modified_input(self, funcToCall, socketio, dataToSend={}):
        data =None
        def setValue(receivedData):
            nonlocal data
            data = receivedData
            # playIndex = int(data['value'])
            print(f'Received Data: {receivedData}')

        socketio.emit(funcToCall,dataToSend,room=self.pRoomId, callback= setValue)
        while data is None:
            print('Waiting for input')
            sleep(1)
            continue
        return data

    def playCard(self,socketio = None, dealer = None, players= None,  card = None):
        #TODO Automatically play the card specified and don't ask the user.
        if self.chanceNo == 1:
            self.showPropertyCollection()
            self.showBankCollection()        
        self.showHandCards()

        ##=================
        playIndex = int(self.modified_input('take_input', socketio)['value'])
        ##==================
        # playIndex = int(input('Which card to Play? -1 to pass.'))
        
        if playIndex == -1:
            return -1
            
        elif playIndex == -2:
            self.arrangeCards(players,socketio)
            return 0

        if isinstance(self.handCards[playIndex], ActionCards):
            success = self.handCards[playIndex].playCard(self, dealer = dealer, players = players, socketio= socketio)
        else:
            success = self.handCards[playIndex].playCard(self, socketio = socketio)
        
        if not success:
            print('Hand not played')
            # self.chanceNo -=1 #Not decreasing. Instead increasing only on success.
            return
        
        playedCard = self.handCards.pop(playIndex)
        dealer.discardedCards.append(playedCard.id)
        self.chanceNo +=1

        if self.doubleRent:
            doubleRentCard = [card for card in self.handCards if card.id=='ADR'][0]
            dealer.discardedCards.append(doubleRentCard.id) #TODO:X
            self.handCards.remove(doubleRentCard)
            self.chanceNo += 1 #TODO:X
            self.doubleRent = False

        self.showPropertyCollection()
        self.showBankCollection()
        return 0
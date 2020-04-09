from time import sleep

class Cards():
    def __init__(self, id):
        self.id = id
        self.value = self.cardValue(id)

    def __str__(self):
        return self.id + ' ' + str(self.value)

    def cardValue(self, id):
        if id[0] == 'M':
            return int(id[1:])
        #10 - edc344ff
        if id in ['ADB']: #ba94cdff
            return 5
        elif id in ['AHT','AJN','PDb','PDg','PWCDbDg','PWCDgBl','PWCLbBl']: #63bde4ff
            return 4

        elif id in ['ASD','AFD','ADC','AHS','ARTXX', 'PYl','PRd','PWCRdYl']:#c1e38bff
            return 3

        elif id in ['AIB','POr','PPk','PLg','PBl','PWCLgBl','PWCOrPk']: #daad79ff
            return 2

        elif id in ['ADR','APG','PBr','PLb','PLbBr'] or id.startswith('ART'): #ffe476ff
            return 1

        elif id in ['PWCXX']:
            return 0

        else:
            print('Card Value not listed')
            return 0

class MoneyCards(Cards):
    def __init__(self,id):
        super().__init__(id)

    def playCard(self, player, socketio):
        player.bankCollection.append(self)
        player.moneyValue += self.value #added Value
        player.totalValue += self.value #added Value
        player.sendMessageToAll(f'{player.name} added ${self.value} M to bank.', socketio)
        return True

class PropertySet():
    def __init__(self,color):
        self.color = color
        self.propertyCards = []
        self.fullSetSize = len(self.rentMapFunc(color)) if color !='XX' else -1 #This way it won't be of full size ever. So, don't need to handle house and hotels separately!!!
        # self.currentSetSize = len(self.propertyCards)
        self.house = None
        self.hotel = None
        # self.rentList = self.rentMapFunc(self.color)

    def getAllCards(self):
        allCards = [card.id for card in self.propertyCards]
        if self.house:
            allCards.append(self.house.id)
        if self.hotel:
            allCards.append(self.hotel.id)
        return allCards

    def currentSetSize(self):
        return len(self.propertyCards)

    def currentRent(self):
        baseRent = self.rentMapFunc(self.color)[self.currentSetSize()-1]
        totalRent = baseRent
        if self.house:
            totalRent+= self.house.value
        if self.hotel:
            totalRent+= self.hotel.value

        return totalRent

    def rentMapFunc(self, color):
        rentMap = {'Bl':[1,2,3,4],
        'Lg':[1,2],
        'Db':[3,8],
        'Lb':[1,2,3],
        'Dg':[2,4,7],
        'Or':[1,3,5],
        'Rd':[2,3,6],
        'Yl':[2,4,6],
        'Pk':[1,2,4],
        'Br':[1,2]}
        return rentMap[color]

    def isFullSet(self):
        if self.fullSetSize == self.currentSetSize():
            return True
        return False
    
    def isEmptySet(self):
        if self.currentSetSize() == 0:
            return True
        return False     

    def findPropertyCardById(self,propertyCardId):
        return [propertyCard for propertyCard in self.propertyCards if propertyCard.id == propertyCardId][0]
    

    def addPropertyCard(self, propertyCard):
        if self.isFullSet():
            print('The propertyset is full. See TODO ') #TODO add extra property Set color in the propertyCollection
            return False
        # self.currentSetSize+=1
        self.propertyCards.append(propertyCard)
        return True

    def removePropertyCard(self, propertyCard):
        if self.isEmptySet():
            print('The propertySet is empty')
            return False
        if self.house or self.hotel:
            print('Cannot remove property from a full set having hotel/ house. First remove the hotel/ house (if any).')
            return False
        # self.currentSetSize-=1
        self.propertyCards.remove(propertyCard)
        return True

    def addHouse(self, actionCard):
        if not self.isFullSet():
            print('The propertySet is not Full')
            return False
        if self.house:
            print('The set already has a house')
            return False
        self.house = actionCard
        return True

    def removeHouse(self):
        actionCard = self.house
        self.house = None
        return actionCard

    def removeHotel(self):
        actionCard = self.hotel
        self.hotel = None
        return actionCard

    def addHotel(self, actionCard):
        if not self.isFullSet():
            print('The propertySet is not Full')
            return False
        if self.hotel:
            print('The set already has a hotel')
            return False
        # if not self.house:
        #     print('Cannot attach a hotel before adding house')
        #     return False
        self.hotel = actionCard
        return True

    # def swapCards(self, player, propertyCardID, toPropertySetColor):
    #     propertyCard = [propertyCard for propertyCard in self.propertyCards if propertyCard.id == propertyCardID][0] 
    #     fromPropertySetColor = self.color
    #     if propertyCard.id[3:5] != 'XX':
    #         colorA, colorB = propertyCard.id[3:5], propertyCard.id[5:7]
    #         toPropertySetColor = colorA if colorB == fromPropertySetColor else colorB
        
    #     else:
    #         toPropertySetColor = input('Enter the color code of the property set to which you wish to transfer this property')

    #     toPropertySet = [propertySet for propertySet in player.propertyCollection if propertySet.color == toPropertySetColor]
    #     self.remove(propertyCard)
    #     toPropertySet.append(propertyCard)


class PropertyCards(Cards):
    def __init__(self,id):
        super().__init__(id)

    def playCard(self, player, socketio):
        if not self.id[1:3] == 'WC':
            color = self.id[1:3]
        elif self.id[3:5] == 'XX':
            # color = input('Enter the color code of the property set where you would like to add this card: ')
            player.sendMessageToPlayer('Choose the color code of the property set where you would like to add this card.', socketio)
            receivedData = player.modified_input('choose_own_set', socketio)
            color = receivedData['color']
        else:
            color1, color2 = self.id[3:5], self.id[5:7]
            receivedData = player.modified_input('choose_value', socketio, dataToSend = {'message':'Choose the color code of the property set where you would like to add this card','0':color1,'1':color2})
            colorIndex = int(receivedData['value'])
            # colorIndex = int(input(f'Choose the color code of the property set where you would like to add this card: 0 for {color1}, 1 for {color2}'))
            color = color1 if colorIndex == 0 else color2

        propertySet = player.findPropertySetByColor(color)
        if not propertySet.addPropertyCard(self):#Some error in adding property - Full set
            # Try adding it to XX:
            mixedPropertySet = player.findPropertySetByColor('XX')
            color = 'XX'
            if not mixedPropertySet.addPropertyCard(self):
                return False
        player.sendMessageToAll(f'{player.name} added a {self.id} card to the {color} property set.', socketio)
        player.totalValue += self.value #added Value
        return True
        # player.propertyCollection.append(self)

class ActionCards(Cards):
    def __init__(self,id):
        super().__init__(id)
        self.banked = 0
    
    def isCashed(self):
        return self.banked

    def actionInstructionFunc(self, functionInitials):
        actionInstruction = {'SD':'Steal a property from the player of your choice. (Cannot be part of a full set). Play into center to use.', 'FD':'Swap any property with another player. (Cannot be part of a full set.) Play into center to use.', 'DB':'Steal a complete set of properties from any player. (Includes any buildings.) Play into center to use.','JN':'Use any time when an action card is played against you. Play into center to use.','DC':'Force any player to pay you $5 M. Play into center to use.', 'IB':'All players give you $2 M as a gift. Play into center to use.','DR':'Needs to be played with a rent card. Play into center to use.','HS':'Add onto any full set you own to add $3 M to the rent value. (Except railroads and utilities.)','HT':'Add onto any full set you own to add $4 M to the rent value. (Except railroads and utilities.)','PG':'Draw 2 extra cards. Play into center to use.','RT':['All players pay you rent for properties you own in one of these colors. Play into center to use.','Force one player to pay you rent for properties you own in one of these colors. Play into center to use.']}
        return actionInstruction[functionInitials]

    def actionMapFunc(self, functionInitials):
        actionMap = {'SD':'SlyDeal','FD':'ForcedDeal', 'DB':'DealBreaker','JN':'JustSayNo','DC':'DebtCollector', 'IB':'ItsMyBirthday','DR':'DoubleRent','HS':'House','HT':'Hotel','PG':'PassGo','RT':'RentCard'}
        return actionMap[functionInitials]

    def playCard(self, player, dealer, players, socketio):
        if not self.banked:
            bank =-2
            def setValue(data):
                nonlocal bank
                bank = int(data['value'])
                print(f'Received Value: {bank}')
            socketio.emit('choose_value',{'message':'How do you want to play this Action Card?','0':'Action','1':'Cash'},room=player.pRoomId, callback= setValue)
            while bank==-2:
                print('Waiting for input')
                sleep(1)
                continue
            # bank = int(input('1 for Cash and 0 for Action.'))
        else:
            bank = 1
        if bank:
            self.banked =1
            player.bankCollection.append(self)
            player.moneyValue += self.value #Added Value
            player.totalValue += self.value #added Value
            player.sendMessageToAll(f'{player.name} added ${self.value} M to bank.', socketio)
            return True

        functionInitials = self.id[1:3]
        if functionInitials == 'RT':
            function = self.actionMapFunc(functionInitials)
            if not player.__getattribute__(function)(self, dealer, players, socketio):
                return False
        elif functionInitials == 'JN':
            player.sendMessageToPlayer('Cannot play just say no until an action has been taken against you.', socketio)
            print('Cannot play just say no until an action has been taken against you')
            return False
        elif functionInitials == 'DR':
            player.sendMessageToPlayer('Can play this card only with a rent card.', socketio)
            print('Can play this card only with a rent card.')
            return False
        elif functionInitials == 'PG':
            function = self.actionMapFunc(functionInitials)
            if not player.__getattribute__(function)(dealer, socketio):
                return False
        elif functionInitials in ['HS','HT']:
            function = self.actionMapFunc(functionInitials)            
            if not player.__getattribute__(function)(self,players, socketio):
                return False
        else: # DB, SD, FD, IB, DC
            function = self.actionMapFunc(functionInitials)            
            if not player.__getattribute__(function)(players, socketio):
                return False

        # dealer.discardedCards.append(self.id)
        return True

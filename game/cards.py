class Cards():
    def __init__(self, id):
        self.id = id
        self.value = self.cardValue(id)

    def __str__(self):
        return self.id + ' ' + str(self.value)

    def cardValue(self, id):
        if id[0] == 'M':
            return int(id[1:])
        
        if id in ['ADB']:
            return 5
        elif id in ['AHT','AJN','PDb','PDg','PWCDbDg','PWCDgBl']:
            return 4

        elif id in ['ASD','AFD','ADC','AHS','ARTXX', 'PYl','PRd','PWCRdYl']:
            return 3

        elif id in ['AIB','PDg','POr','PPk','PLg','PBl','PWCLbBr','PWCLbBl','PWCLgBl','PWCOrPk']:
            return 2

        elif id in ['ADR','APG','PBr','PLb'] or id.startswith('ART'):
            return 1

        elif id in ['PWCXX']:
            return 0

        else:
            print('Card Value not listed')
            return 0

class MoneyCards(Cards):
    def __init__(self,id):
        super().__init__(id)

    def playCard(self, player):
        player.bankCollection.append(self)
        player.moneyValue += self.value #added Value
        player.totalValue += self.value #added Value

class PropertySet():
    def __init__(self,color):
        self.color = color
        self.propertyCards = []
        self.fullSetSize = len(self.rentMapFunc(color))
        # self.currentSetSize = len(self.propertyCards)
        self.house = None
        self.hotel = None
        # self.rentList = self.rentMapFunc(self.color)

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
        if not self.house:
            print('Cannot attach a hotel before adding house')
            return False
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

    def playCard(self, player):
        if not self.id[1:3] == 'WC':
            color = self.id[1:3]
        else:
            color = input('Enter the color code of the property set where you would like to add this card: ')

        propertySet = player.findPropertySetByColor(color)
        if propertySet.addPropertyCard(self):
            player.totalValue += self.value #added Value
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

    def playCard(self, player, dealer, players):
        if not self.banked:
            bank = int(input('1 for Cash and 0 for Action.'))
        else:
            bank = 1
        if bank:
            self.banked =1
            player.bankCollection.append(self)
            player.moneyValue += self.value #Added Value
            player.totalValue += self.value #added Value
            return 

        functionInitials = self.id[1:3]
        if functionInitials == 'RT':
            function = self.actionMapFunc(functionInitials)
            player.__getattribute__(function)(self, dealer, players)
        elif functionInitials == 'JN':
            print('Cannot play just say no until an action has been taken against you')
        elif functionInitials == 'DR':
            print('Can play this card only with a rent card.')
        elif functionInitials == 'PG':
            function = self.actionMapFunc(functionInitials)
            player.__getattribute__(function)(dealer)
        elif functionInitials in ['HS','HT']:
            function = self.actionMapFunc(functionInitials)            
            player.__getattribute__(function)(self)
        else:
            function = self.actionMapFunc(functionInitials)            
            player.__getattribute__(function)(players)

        dealer.discardedCards.append(self)

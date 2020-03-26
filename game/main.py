#everyWhere snakeCase
import random 
from dealer import Dealer
from player import Players

random.seed(0)

if __name__ == '__main__':
    numPlayers = 2
    players = Players(numPlayers)
    dealer = Dealer()
    dealer.initialiseCards()
    dealer.shuffleCards()
    # print(len(dealer.drawPile), set(dealer.drawPile))
    # print(dealer.discardedCards)

    dealer.distributeCards(players.players)
    playerChance = 0
    player = players.players[playerChance]
    while(not player.hasWon()):
        print('+++++++++++++++++++++++++++++')
        print(f'Player - {player.id}')
        print('+++++++++++++++++++++++++++++')
        # print(player.handCards,player.propertyCollection, player.bankCollection)
        player.chance =True
        player.drawCards(dealer)
        
        print(len(dealer.drawPile), len(player.handCards))

        player.chanceNo = 1
        while player.chanceNo <= player.cardsToPlay:
            val = player.playCard( dealer  = dealer, players = players)
            player.chanceNo +=1 
            if val == -1:
                break

        if len(player.handCards)>7:
            player.discardCards(dealer.drawPile)

        if player.hasWon():
            print('***************************************')
            print(f'Player - {player.id} has won the game.')
            print('***************************************')
            break

        player.chance = False
        playerChance = (playerChance+1)%numPlayers
        player = players.players[playerChance]    
from flask import Flask , render_template, redirect, request
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import random
from game.dealer import Dealer
from game.player import Players

random.seed(0)

app = Flask(__name__,template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

numPlayers = 0
playersNames = []

rooms = {}

@app.route('/')
def homePage():
    return render_template('index.html')

# @app.route('/rooms/<roomid>/')
# def lobbyPage(roomid):
#     return render_template('lobby.html', roomid = roomid)

# @app.route('/rooms/<roomid>/board')
# def gamePage(roomid):
#     return render_template('board.html', roomid = roomid)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    msg = 'Client disconnected'
    send(msg, broadcast=True)

@socketio.on('enter_lobby')
def handleNewEntryLobby(room):
    emit('modify_lobby',rooms[room],room=room)

# @socketio.on('enter_board')
# def handleNewEntryBoard(room, player):
#     emit('modify_public',rooms[room], room=room)

@socketio.on('cue_to_start')
def handleStartingCue(room):
    emit('game_setup',rooms[room], room=room)
    emit('game_data',{'users':rooms[room]},room=room)
    for (player, id) in rooms[room]:
        emit('player_data', {'username':player}, room=id)
    initialise_game(room)

@socketio.on('join')
def on_join(data): #TODO Number of players restriction
    username = data['username']
    room = data['room']
    if data['exists']==0:
        send(f'Room does not exist. Creating a new room - {room}.') #TODO
        rooms[room]=[]

    else:
        send(f'Room exists. Joining the room - {room}')
    
    rooms[room].append((username, request.sid))

    join_room(room)
    send(username + ' has entered the room.', room=room) #Send only to the members in the room

def initialise_game(room):
    numPlayers = len(rooms[room])
    players = Players(numPlayers)
    dealer = Dealer()
    dealer.initialiseCards()
    dealer.shuffleCards()
    dealer.distributeCards(players.players)

    socketio.emit('game_data',{'drawpile':dealer.drawPile[-5:],'playpile':dealer.discardedCards[-5:]}, room = room)

    for ((username, p_roomid), player) in zip(rooms[room], players.players):
        # emit('player_data', player, room=id)
        socketio.emit('game_data',{'id':player.id,'name':username,'bank_collection':player.bankCollection,'property_collection':{propertySet.color:propertySet.propertyCards for propertySet in player.propertyCollection}}, room = room)
        socketio.emit('player_data',{'id':player.id,'name':username,'handcards':[card.id for card in player.handCards]}, room=p_roomid)

#     playerChance = 0
#     player = players.players[playerChance]
#     while(not player.hasWon()):
#         print('+++++++++++++++++++++++++++++')
#         print(f'Player - {player.id}')
#         print('+++++++++++++++++++++++++++++')
#         # print(player.handCards,player.propertyCollection, player.bankCollection)
#         player.chance =True
#         player.drawCards(dealer)
        
#         print(len(dealer.drawPile), len(player.handCards))

#         player.chanceNo = 1
#         while player.chanceNo <= player.cardsToPlay:
#             val = player.playCard( dealer  = dealer, players = players)
#             player.chanceNo +=1 
#             if val == -1:
#                 break

#         if len(player.handCards)>7:
#             player.discardCards(dealer.drawPile)

#         if player.hasWon():
#             print('***************************************')
#             print(f'Player - {player.id} has won the game.')
#             print('***************************************')
#             break

#         player.chance = False
#         playerChance = (playerChance+1)%numPlayers
#         player = players.players[playerChance]    

# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send(username + ' has left the room.', room=room)

if __name__ == '__main__':
	socketio.run(app)
from flask import Flask , render_template, redirect, request
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import random
import logging
from game.dealer import Dealer
from game.player import Players

# random.seed(0)

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

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

def json_game_data(players, dealer):
    
    return {'drawpile':dealer.drawPile,
     'playpile':dealer.discardedCards,
    'players': { player.id: {
                'chance':player.chance,
                'chance_no':player.chanceNo,
                'username':player.name,
                'proom_id':player.pRoomId,
                'bank_collection':[card.id for card in player.bankCollection],
                'property_collection':{propertySet.color:[card.id for card in propertySet.propertyCards] for propertySet in player.propertyCollection}
                } for player in players.players}
    }

def json_player_data(player,dealer):
    return {'id':player.id,
    'chance':player.chance,
    'name':player.name,
    'proom_id':player.pRoomId,
    'handcards':[card.id for card in player.handCards]}

def initialise_game(room):
    numPlayers = len(rooms[room])
    players = Players(numPlayers)
    dealer = Dealer()
    dealer.initialiseCards()
    dealer.shuffleCards()
    dealer.distributeCards(players.players)
    for ((username, p_roomid), player) in zip(rooms[room], players.players):
        player.name = username
        player.pRoomId = p_roomid

    socketio.emit('game_data',json_game_data(players,dealer), room = room)
    socketio.emit('player_data',json_player_data(player,dealer), room=p_roomid)

    # for ((username, p_roomid), player) in zip(rooms[room], players.players):
        # emit('player_data', player, room=id)
        # socketio.emit('game_data',json_game_data(players,dealer), room = room)

    playerChance = 0
    player = players.players[playerChance]
    while(not player.hasWon()):
        print('+++++++++++++++++++++++++++++')
        print(f'Player - {player.id}')
        print('+++++++++++++++++++++++++++++')
        player.chance =True
        # p_roomid = rooms[room][playerChance][1]
        # socketio.emit('player_data',json_player_data(player,dealer), room = player.pRoomId)
        # print(player.handCards,player.propertyCollection, player.bankCollection)
        player.drawCards(dealer)
        player.chanceNo = 1

        socketio.emit('player_data',json_player_data(player,dealer), room = player.pRoomId)
        socketio.emit('game_data',json_game_data(players,dealer), room = room)
        
        print(len(dealer.drawPile), len(player.handCards))
        while player.chanceNo <= player.cardsToPlay:
            val = player.playCard(socketio= socketio, dealer  = dealer, players = players) #TODO check the value of val
            if val == -1:
                break
            player.chanceNo +=1 
            socketio.emit('player_data',json_player_data(player,dealer), room = player.pRoomId)    
            socketio.emit('game_data',json_game_data(players,dealer), room = room)

        if len(player.handCards)>7:
            player.discardCards(dealer.drawPile)
            socketio.emit('player_data',json_player_data(player,dealer), room = player.pRoomId)        
            socketio.emit('game_data',json_game_data(players,dealer), room = room)

        if player.hasWon():
            print('***************************************')
            print(f'Player - {player.id} has won the game.')
            print('***************************************')
            break

        player.chance = False
        socketio.emit('player_data',json_player_data(player,dealer), room = player.pRoomId)        

        playerChance = (playerChance+1)%numPlayers
        player = players.players[playerChance]    

# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send(username + ' has left the room.', room=room)

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=8000, debug= False)
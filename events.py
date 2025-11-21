from flask import session, request
from flask_socketio import emit, join_room, leave_room
import random
import string

# Game State Storage (In-Memory)
# rooms = {
#     'ROOM_CODE': {
#         'players': {
#             'sid1': {'username': 'User1', 'ready': False, 'score': 0},
#             'sid2': {'username': 'User2', 'ready': False, 'score': 0}
#         },
#         'turn': 'sid1',
#         'number': 42,
#         'status': 'waiting' | 'playing' | 'finished'
#     }
# }
rooms = {}

def register_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
        # Logic to remove player from room and notify others
        for room_code, room_data in rooms.items():
            if request.sid in room_data['players']:
                del room_data['players'][request.sid]
                emit('player_left', {'sid': request.sid}, to=room_code)
                if not room_data['players']:
                    del rooms[room_code]
                break

    @socketio.on('create_room')
    def handle_create_room(data):
        username = data.get('username', 'Guest')
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        rooms[room_code] = {
            'players': {
                request.sid: {'username': username, 'ready': False, 'score': 0, 'role': 'host'}
            },
            'status': 'waiting'
        }
        
        join_room(room_code)
        emit('room_created', {'room_code': room_code, 'sid': request.sid}, to=request.sid)
        print(f"Room {room_code} created by {username}")

    @socketio.on('join_room')
    def handle_join_room(data):
        room_code = data.get('room_code').upper()
        username = data.get('username', 'Guest')
        
        if room_code in rooms:
            if len(rooms[room_code]['players']) < 2:
                rooms[room_code]['players'][request.sid] = {
                    'username': username, 
                    'ready': False, 
                    'score': 0, 
                    'role': 'guest'
                }
                join_room(room_code)
                
                # Notify everyone in room
                players_list = [
                    {'sid': sid, 'username': p['username'], 'role': p['role']} 
                    for sid, p in rooms[room_code]['players'].items()
                ]
                emit('player_joined', {'players': players_list}, to=room_code)
                print(f"{username} joined room {room_code}")
            else:
                emit('error', {'message': 'Room is full'}, to=request.sid)
        else:
            emit('error', {'message': 'Room not found'}, to=request.sid)

    @socketio.on('chat_message')
    def handle_chat(data):
        room_code = data.get('room_code')
        message = data.get('message')
        if room_code in rooms:
            username = rooms[room_code]['players'][request.sid]['username']
            emit('chat_message', {'username': username, 'message': message}, to=room_code)

    @socketio.on('avatar_jump')
    def handle_jump(data):
        room_code = data.get('room_code')
        if room_code in rooms:
            emit('avatar_jump', {'sid': request.sid}, to=room_code, include_self=False)

    @socketio.on('start_game')
    def handle_start_game(data):
        room_code = data.get('room_code')
        if room_code in rooms:
            # If game is already playing, resend the game state
            if rooms[room_code].get('status') == 'playing':
                # Build player names dict
                player_names = {sid: p['username'] for sid, p in rooms[room_code]['players'].items()}
                emit('game_started', {
                    'first_turn': rooms[room_code]['turn'],
                    'players': list(rooms[room_code]['players'].keys()),
                    'player_names': player_names
                }, to=request.sid)
                return
            
            # Generate secret number
            rooms[room_code]['number'] = random.randint(1, 100)
            rooms[room_code]['status'] = 'playing'
            
            # Coin flip logic
            players = list(rooms[room_code]['players'].keys())
            first_player = random.choice(players)
            rooms[room_code]['turn'] = first_player
            
            # Build player names dict
            player_names = {sid: p['username'] for sid, p in rooms[room_code]['players'].items()}
            
            emit('game_started', {
                'first_turn': first_player,
                'players': players,
                'player_names': player_names
            }, to=room_code)

    @socketio.on('make_guess')
    def handle_guess(data):
        room_code = data.get('room_code')
        guess = int(data.get('guess'))
        
        if room_code in rooms:
            secret_number = rooms[room_code]['number']
            current_player_sid = request.sid
            
            result = ''
            if guess == secret_number:
                result = 'win'
                emit('game_over', {'winner': current_player_sid, 'number': secret_number}, to=room_code)
                rooms[room_code]['status'] = 'finished'
            else:
                if guess < secret_number:
                    result = 'low'
                else:
                    result = 'high'
                
                # Switch turn
                players = list(rooms[room_code]['players'].keys())
                next_turn = [p for p in players if p != current_player_sid][0]
                rooms[room_code]['turn'] = next_turn
                
                emit('turn_result', {
                    'guess': guess,
                    'result': result,
                    'player': current_player_sid,
                    'next_turn': next_turn
                }, to=room_code)

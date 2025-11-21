from flask import session, request
from flask_socketio import emit, join_room, leave_room
import random
import string

# Game State Storage (In-Memory)
# rooms = {
#     'ROOM_CODE': {
#         'players': {
#             'sid1': {'username': 'User1', 'ready': False, 'score': 0, 'role': 'host'},
#             'sid2': {'username': 'User2', 'ready': False, 'score': 0, 'role': 'guest'}
#         },
#         'turn': 'sid1',
#         'number': 42,
#         'status': 'waiting' | 'playing' | 'finished',
#         'rematch_votes': set()
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
                
                # If room empty, delete it
                if not room_data['players']:
                    del rooms[room_code]
                else:
                    # If game was playing, maybe pause or end?
                    # For now, let's reset status if less than 2 players
                    if len(room_data['players']) < 2:
                        room_data['status'] = 'waiting'
                        emit('waiting_for_players', {'players': list(room_data['players'].keys())}, to=room_code)
                break

    @socketio.on('create_room')
    def handle_create_room(data):
        username = data.get('username', 'Guest')
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        rooms[room_code] = {
            'players': {
                request.sid: {'username': username, 'ready': False, 'score': 0, 'role': 'host'}
            },
            'status': 'waiting',
            'rematch_votes': set()
        }
        
        join_room(room_code)
        emit('room_created', {'room_code': room_code, 'sid': request.sid}, to=request.sid)
        print(f"Room {room_code} created by {username}")

    @socketio.on('join_room')
    def handle_join_room(data):
        room_code = data.get('room_code').upper()
        username = data.get('username', 'Guest')
        
        if room_code not in rooms:
            emit('error', {'message': 'Room not found'}, to=request.sid)
            return

        room = rooms[room_code]
        
        # Check for reconnection (same username)
        existing_sid = None
        for sid, player in room['players'].items():
            if player['username'] == username:
                existing_sid = sid
                break
        
        if existing_sid:
            # Reconnection: Swap SID
            player_data = room['players'].pop(existing_sid)
            room['players'][request.sid] = player_data
            
            if room.get('turn') == existing_sid:
                room['turn'] = request.sid
            
            # Update rematch votes if needed
            if existing_sid in room['rematch_votes']:
                room['rematch_votes'].remove(existing_sid)
                room['rematch_votes'].add(request.sid)

            join_room(room_code)
            print(f"{username} reconnected to {room_code}")
        
        elif len(room['players']) < 2:
            # New Player
            room['players'][request.sid] = {
                'username': username, 
                'ready': False, 
                'score': 0, 
                'role': 'guest'
            }
            join_room(room_code)
            print(f"{username} joined {room_code}")
        else:
            emit('error', {'message': 'Room is full'}, to=request.sid)
            return

        # Broadcast updated player list
        players_list = [
            {'sid': sid, 'username': p['username'], 'role': p['role']} 
            for sid, p in room['players'].items()
        ]
        player_names = {sid: p['username'] for sid, p in room['players'].items()}
        
        emit('player_joined', {
            'players': list(room['players'].keys()),
            'player_names': player_names
        }, to=room_code)

    @socketio.on('start_game')
    def handle_start_game(data):
        room_code = data.get('room_code')
        if room_code not in rooms:
            return

        room = rooms[room_code]
        
        # Check player count
        if len(room['players']) < 2:
            player_names = {sid: p['username'] for sid, p in room['players'].items()}
            emit('waiting_for_players', {
                'players': list(room['players'].keys()),
                'player_names': player_names
            }, to=request.sid)
            return

        # If already playing, just send state to requester
        if room['status'] == 'playing':
            player_names = {sid: p['username'] for sid, p in room['players'].items()}
            emit('game_started', {
                'first_turn': room['turn'],
                'players': list(room['players'].keys()),
                'player_names': player_names
            }, to=request.sid)
            return

        # Start new game
        room['number'] = random.randint(1, 100)
        room['status'] = 'playing'
        room['rematch_votes'] = set()
        
        # Random start
        players = list(room['players'].keys())
        first_player = random.choice(players)
        room['turn'] = first_player
        
        player_names = {sid: p['username'] for sid, p in room['players'].items()}
        
        print(f"Starting game in {room_code}. Number: {room['number']}. Turn: {player_names[first_player]}")
        
        emit('game_started', {
            'first_turn': first_player,
            'players': players,
            'player_names': player_names
        }, to=room_code)

    @socketio.on('make_guess')
    def handle_guess(data):
        room_code = data.get('room_code')
        guess = int(data.get('guess'))
        
        if room_code not in rooms:
            return
            
        room = rooms[room_code]
        secret_number = room['number']
        current_player_sid = request.sid
        
        # Validate turn
        if room['turn'] != current_player_sid:
            return

        result = ''
        if guess == secret_number:
            result = 'win'
            room['status'] = 'finished'
            emit('game_over', {'winner': current_player_sid, 'number': secret_number}, to=room_code)
        else:
            if guess < secret_number:
                result = 'low'
            else:
                result = 'high'
            
            # Switch turn
            players = list(room['players'].keys())
            # Find the other player
            next_turn = [p for p in players if p != current_player_sid][0]
            room['turn'] = next_turn
            
            emit('turn_result', {
                'guess': guess,
                'result': result,
                'player': current_player_sid,
                'next_turn': next_turn
            }, to=room_code)

    @socketio.on('vote_rematch')
    def handle_rematch(data):
        room_code = data.get('room_code')
        if room_code not in rooms:
            return
            
        room = rooms[room_code]
        room['rematch_votes'].add(request.sid)
        
        emit('rematch_update', {'votes': len(room['rematch_votes']), 'total': 2}, to=room_code)
        
        if len(room['rematch_votes']) >= 2:
            # Reset game
            handle_start_game({'room_code': room_code})

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

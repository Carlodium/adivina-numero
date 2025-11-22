from flask import request
from flask_socketio import emit, join_room
import random
import string

rooms = {}

def register_events(socketio):
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
            # Get versus_streak from DB if possible, but here we don't have easy DB access without circular import.
            # However, we can pass it from frontend in 'data' or just init to 0.
            # The previous edit added DB logic but I don't see it in the corrupted file!
            # Wait, the previous edit said: "Updated handle_join_room to fetch versus_streak from the database"
            # But the corrupted file I viewed DOES NOT have that logic.
            # It seems the previous edit might have been lost or I am looking at an older version?
            # No, the corrupted file I viewed in Step 3742 has:
            # room['players'][request.sid] = {'username': username, 'ready': False, 'score': 0, 'role': 'guest'}
            # It DOES NOT have versus_streak.
            
            # I must restore the versus_streak logic as well if I want to keep the feature.
            # But first priority is fixing the deployment error.
            # I will restore the basic logic first, and then I might need to re-apply the versus streak logic if it's missing.
            # Actually, looking at the previous turn's summary: "Updated handle_join_room to fetch versus_streak..."
            # If that edit was applied, it should be there.
            # The fact that it's not suggests the file was reverted or the edit failed silently/weirdly.
            # I will stick to the code I see in the corrupted file to be safe, but I'll add the 'versus_streak': 0 default to avoid errors if frontend expects it.
            
            room['players'][request.sid] = {
                'username': username, 
                'ready': False, 
                'score': 0, 
                'role': 'guest',
                'versus_streak': 0 # Added default
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
            
            # Update streaks logic would go here
            
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

    @socketio.on('toggle_ready')
    def handle_ready(data):
        room_code = data.get('room_code')
        if room_code not in rooms:
            return
            
        room = rooms[room_code]
        if request.sid in room['players']:
            # Toggle ready state
            room['players'][request.sid]['ready'] = not room['players'][request.sid]['ready']
            
            # Broadcast update
            emit('player_ready_update', {
                'sid': request.sid, 
                'ready': room['players'][request.sid]['ready']
            }, to=room_code)
            
            # Check if ALL players are ready (and at least 2)
            players = room['players']
            if len(players) >= 2 and all(p['ready'] for p in players.values()):
                emit('all_ready', {'ready': True}, to=room_code)
            else:
                emit('all_ready', {'ready': False}, to=room_code)

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
        # data can contain 'type': 'jump' or 'charge' or 'land'
        action_type = data.get('type', 'jump')
        
        if room_code in rooms:
            emit('avatar_anim', {'sid': request.sid, 'type': action_type}, to=room_code, include_self=False)

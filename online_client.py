import asyncio
import websockets
import json
import threading
import time

class OnlineClient:
    def __init__(self):
        self.websocket = None
        self.room_code = None
        self.connected = False
        self.opponent_data = {"score": 0, "alive": True, "game_started": False}
        self.connection_error = None
        self.room_full = False
        self.opponent_joined = False  # This will ONLY be set by OPPONENT_JOINED message from server
        self.game_started = False  # Flag to track if local player hit start
        self._stop_event = threading.Event()
        self._ws_thread = None

    async def _connect_to_room(self, room_code):
        """Connect to a room on the WebSocket server"""
        uri = f"wss://hop-it-server.onrender.com/ws/{room_code}"
        print(f"Connecting to {uri}...")
        try:
            # Add timeout to prevent freezing
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri),
                timeout=5.0  # 5 second timeout for connection
            )
            print(f"Connected to room {room_code}, waiting for initial response...")
            # Add timeout for initial response too
            response = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=5.0  # 5 second timeout for initial response
            )
            print(f"Received initial response: {response}")
            
            if response == "ROOM_FULL":
                print("Room is full, cannot join")
                self.room_full = True
                self.connection_error = "Room is full"
                # Send to screen
                try:
                    from main import add_debug_message
                    add_debug_message("Room is full! Try another room code.")
                except ImportError:
                    pass  # Handle circular import during startup
                await self.websocket.close()
                return False
                
            # Check for opponent joined message - ONLY this should set opponent_joined flag
            if response == "OPPONENT_JOINED":
                print("Opponent has already joined the room!")
                self.opponent_joined = True
            else:
                # If it's JSON data, process it but DON'T set opponent_joined
                try:
                    data = json.loads(response)
                    self.opponent_data = data
                    print(f"Received initial opponent data: {data}")
                except:
                    print(f"Unknown initial message: {response}")
                    # Non-JSON message that wasn't OPPONENT_JOINED - just ignore
                    pass
                
            self.connected = True
            self.room_code = room_code
            print(f"Successfully connected to room {room_code}")
            return True
        except websockets.exceptions.InvalidStatusCode as e:
            # Specific handling for HTTP status code errors like 502
            status_code = getattr(e, 'status_code', 0)
            if status_code == 502:
                error_msg = f"Server error: HTTP 502 (server unavailable)"
                self.connection_error = f"server rejected WebSocket connection: HTTP 502"
                print(f"Server unavailable (HTTP 502) - possibly restarting")
                # Send to screen
                from main import add_debug_message
                add_debug_message(error_msg)
            else:
                error_msg = f"Server error: HTTP {status_code}"
                self.connection_error = f"server rejected WebSocket connection: HTTP {status_code}"
                print(f"HTTP error connecting to server: {e}")
                # Send to screen
                from main import add_debug_message
                add_debug_message(error_msg)
            return False
            
        except websockets.exceptions.ConnectionClosed as e:
            error_msg = f"Connection closed: {e.reason}"
            self.connection_error = error_msg
            print(f"Connection closed while connecting: {e}")
            # Send to screen
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass  # Handle circular import during startup
            return False
            
        except asyncio.TimeoutError:
            # Specific handling for timeout errors
            error_msg = "Server error occurred, Retry"
            self.connection_error = "Connection timed out"
            print(f"Failed to connect to room: timed out during opening handshake")
            # Send to screen
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass  # Handle circular import during startup
            return False
            
        except Exception as e:
            # Generic error handling
            error_msg = f"Connection error: {str(e)}"
            self.connection_error = str(e)
            print(f"Failed to connect to room: {e}")
            # Send to screen
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass  # Handle circular import during startup
            return False

    async def _listen_for_messages(self):
        """Listen for messages from the server"""
        print("Starting message listener...")
        try:
            while not self._stop_event.is_set() and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=0.5)
                    print(f"Received message: {message}")
                    
                    # Handle special OPPONENT_JOINED message
                    if message == "OPPONENT_JOINED":
                        print("Received OPPONENT_JOINED signal!")
                        self.opponent_joined = True
                        print("Opponent has officially joined!")
                        continue
                        
                    # Try to parse as JSON data from opponent
                    try:
                        data = json.loads(message)
                        print(f"Parsed JSON data: {data}")
                        # Update opponent data but NEVER set opponent_joined flag here
                        self.opponent_data = data
                    except json.JSONDecodeError as e:
                        print(f"Received non-JSON message: {message}, Error: {e}")
                except asyncio.TimeoutError:
                    # This is expected, just continue
                    continue
                except websockets.exceptions.ConnectionClosed as e:
                    error_msg = f"WebSocket connection closed: {str(e)}"
                    print(error_msg)
                    # Send to screen
                    try:
                        from main import add_debug_message
                        add_debug_message(error_msg)
                    except ImportError:
                        pass
                    break
                except Exception as e:
                    error_msg = f"Error in message listener: {str(e)}"
                    print(error_msg)
                    # Send to screen
                    try:
                        from main import add_debug_message
                        add_debug_message(error_msg)
                    except ImportError:
                        pass
                    break
        finally:
            print("Message listener stopped")
            self.connected = False
            # Also reset opponent status when disconnected
            self.opponent_joined = False

    async def _send_data_loop(self, get_player_data_func):
        """Continuously send player data to the server"""
        print("Starting data sending loop...")
        try:
            while not self._stop_event.is_set() and self.connected and self.websocket:
                try:
                    # Get current player data through the callback
                    player_data = get_player_data_func()
                    
                    # Add game_started flag to the data
                    player_data["game_started"] = self.game_started
                    
                    # Send data and periodically print what we're sending (not too often)
                    data_json = json.dumps(player_data)
                    await self.websocket.send(data_json)
                    
                    # Debug only occasionally to avoid console spam
                    if int(time.time() * 10) % 20 == 0:  # Print every ~2 seconds
                        print(f"Sent player data: {data_json}")
                        print(f"Opponent joined: {self.opponent_joined}, Opponent data: {self.opponent_data}")
                    
                    await asyncio.sleep(0.1)  # Send updates 10 times per second
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"Connection closed while sending: {e}")
                    break
        except Exception as e:
            print(f"Error in sending data: {e}")
        finally:
            print("Data sending loop stopped")

    async def _run_client(self, room_code, get_player_data_func):
        """Main client coroutine"""
        connected = await self._connect_to_room(room_code)
        if not connected:
            return

        # Start listening for opponent data
        listen_task = asyncio.create_task(self._listen_for_messages())
        
        # Start sending player data
        send_task = asyncio.create_task(self._send_data_loop(get_player_data_func))
        
        # Wait until stop is requested
        while not self._stop_event.is_set():
            await asyncio.sleep(0.1)
        
        # Clean up
        if self.websocket:
            await self.websocket.close()
        
        # Cancel tasks
        listen_task.cancel()
        send_task.cancel()
        
        try:
            await listen_task
        except asyncio.CancelledError:
            pass
            
        try:
            await send_task
        except asyncio.CancelledError:
            pass

    def connect(self, room_code, get_player_data_func):
        """Connect to a room and start communication in a separate thread"""
        if self._ws_thread and self._ws_thread.is_alive():
            return False  # Already running
            
        # Reset all connection state for a fresh connection
        self.opponent_joined = False
        self.game_started = False
        self.opponent_data = {"score": 0, "alive": True, "game_started": False}
        self.room_full = False
        self.connection_error = None  # Clear any previous errors
        self._stop_event.clear()
        
        # Define a function to handle async connection with appropriate error capture
        def run_async_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                connection_result = loop.run_until_complete(self._run_client(room_code, get_player_data_func))
                loop.close()
                # Return connection result
                return connection_result
            except Exception as e:
                # Capture any unexpected errors that weren't caught in _connect_to_room
                self.connection_error = f"Connection error: {str(e)}"
                print(f"Unhandled connection error: {e}")
                return False
        
        # Start connection thread
        self._ws_thread = threading.Thread(target=run_async_loop)
        self._ws_thread.daemon = True
        self._ws_thread.start()
        
        # Give the connection a brief moment to establish or fail
        # This helps capture immediate connection errors like "server rejected"
        time.sleep(0.5)
        
        # Check if connection error was set
        if self.connection_error:
            print(f"Connect failed with error: {self.connection_error}")
            return False
            
        # Looks good so far    
        return True

    def disconnect(self):
        """Disconnect from the WebSocket server"""
        self._stop_event.set()
        # Thread will clean up and exit
        
        # Wait for thread to finish, but not too long
        if self._ws_thread and self._ws_thread.is_alive():
            self._ws_thread.join(timeout=1.0)
        
        # Reset all connection and game state
        self.reset()
        
    def reset(self):
        """Reset all game and connection state for a new game"""
        self.connected = False
        self.opponent_joined = False
        self.game_started = False
        self.opponent_data = {"score": 0, "alive": True, "game_started": False}
        print("Online client completely reset for new game")
        
    def is_opponent_alive(self):
        """Check if opponent is still alive in the game"""
        return self.opponent_data.get("alive", False)
        
    def get_opponent_score(self):
        """Get opponent's current score"""
        return self.opponent_data.get("score", 0)
        
    def has_opponent_joined(self):
        """Check if an opponent has joined the room"""
        # ONLY return True if the server has sent us the OPPONENT_JOINED message
        # This is set when we receive that specific message from the server
        return self.opponent_joined
        
    def start_game(self):
        """Indicate that this player is ready to start the game"""
        self.game_started = True
        
    def is_opponent_ready(self):
        """Check if the opponent has indicated they are ready to start"""
        return self.opponent_data.get("game_started", False)

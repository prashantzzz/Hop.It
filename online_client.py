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
        self.opponent_joined = False
        self.game_started = False
        self._stop_event = threading.Event()
        self._ws_thread = None

    async def _connect_to_room(self, room_code):
        uri = f"wss://hop-it-server.onrender.com/ws/{room_code}"
        print(f"Connecting to {uri}...")
        try:
            connect_task = asyncio.ensure_future(websockets.connect(uri))
            try:
                self.websocket = await asyncio.wait_for(connect_task, timeout=5.0)
            except asyncio.TimeoutError:
                connect_task.cancel()
                try:
                    await connect_task
                except asyncio.CancelledError:
                    pass
                raise

            print(f"Connected to room {room_code}, waiting for initial response...")

            try:
                response = await self.websocket.recv() #no timeout, client waits indifinetly for the other
                print(f"Received initial response: {response}")

                if response == "ROOM_FULL":
                    print("Room is full, cannot join")
                    self.room_full = True
                    self.connection_error = "Room is full"
                    try:
                        from main import add_debug_message
                        add_debug_message("Room is full! Try another room code.")
                    except ImportError:
                        pass
                    await self.websocket.close()
                    return False

                if response == "OPPONENT_JOINED":
                    print("Opponent has already joined the room!")
                    self.opponent_joined = True
                else:
                    try:
                        data = json.loads(response)
                        self.opponent_data = data
                        print(f"Received initial opponent data: {data}")
                    except:
                        print(f"Unknown initial message: {response}")
            except asyncio.TimeoutError:
                print("No response from server yet (waiting for opponent to join).")
                self.opponent_joined = False

            self.connected = True
            self.room_code = room_code
            print(f"Successfully connected to room {room_code}")
            return True

        except websockets.exceptions.InvalidStatusCode as e:
            status_code = getattr(e, 'status_code', 0)
            if status_code == 502:
                error_msg = "Server error: HTTP 502 (server unavailable)"
                self.connection_error = error_msg
                print("Server unavailable (HTTP 502) - possibly restarting")
                from main import add_debug_message
                add_debug_message(error_msg)
            else:
                error_msg = f"Server error: HTTP {status_code}"
                self.connection_error = error_msg
                print(f"HTTP error connecting to server: {e}")
                from main import add_debug_message
                add_debug_message(error_msg)
            return False

        except websockets.exceptions.ConnectionClosed as e:
            error_msg = f"Connection closed: {e.reason}"
            self.connection_error = error_msg
            print(f"Connection closed while connecting: {e}")
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass
            return False

        except asyncio.TimeoutError:
            error_msg = "Server error occurred, Retry"
            self.connection_error = "Connection timed out"
            print("Failed to connect to room: timed out during opening handshake")
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass
            return False

        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.connection_error = error_msg
            print(f"Failed to connect to room: {e}")
            try:
                from main import add_debug_message
                add_debug_message(error_msg)
            except ImportError:
                pass
            return False

    async def _listen_for_messages(self):
        print("Starting message listener...")
        try:
            while not self._stop_event.is_set() and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=0.5)
                    print(f"Received message: {message}")

                    if message == "OPPONENT_JOINED":
                        print("Received OPPONENT_JOINED signal!")
                        self.opponent_joined = True
                        continue

                    try:
                        data = json.loads(message)
                        self.opponent_data = data
                        print(f"Parsed JSON data: {data}")
                    except json.JSONDecodeError as e:
                        print(f"Received non-JSON message: {message}, Error: {e}")
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"WebSocket connection closed: {e}")
                    break
                except Exception as e:
                    print(f"Error in message listener: {e}")
                    break
        finally:
            print("Message listener stopped")
            self.connected = False
            self.opponent_joined = False

    async def _send_data_loop(self, get_player_data_func):
        print("Starting data sending loop...")
        try:
            while not self._stop_event.is_set() and self.connected and self.websocket:
                try:
                    player_data = get_player_data_func()
                    player_data["game_started"] = self.game_started
                    await self.websocket.send(json.dumps(player_data))
                    await asyncio.sleep(0.1)
                except websockets.exceptions.ConnectionClosed:
                    break
        except Exception as e:
            print(f"Error in sending data: {e}")
        finally:
            print("Data sending loop stopped")

    async def _run_client(self, room_code, get_player_data_func):
        connected = await self._connect_to_room(room_code)
        if not connected:
            return

        listen_task = asyncio.create_task(self._listen_for_messages())
        send_task = asyncio.create_task(self._send_data_loop(get_player_data_func))

        while not self._stop_event.is_set():
            await asyncio.sleep(0.1)

        if self.websocket:
            await self.websocket.close()

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
        if self._ws_thread and self._ws_thread.is_alive():
            return False

        self.opponent_joined = False
        self.game_started = False
        self.opponent_data = {"score": 0, "alive": True, "game_started": False}
        self.room_full = False
        self.connection_error = None
        self._stop_event.clear()

        def run_async_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._run_client(room_code, get_player_data_func))
                loop.close()
            except Exception as e:
                self.connection_error = f"Connection error: {str(e)}"
                print(f"Unhandled connection error: {e}")

        self._ws_thread = threading.Thread(target=run_async_loop)
        self._ws_thread.daemon = True
        self._ws_thread.start()

        time.sleep(0.5)
        if self.connection_error:
            print(f"Connect failed with error: {self.connection_error}")
            return False

        return True

    def disconnect(self):
        self._stop_event.set()
        if self._ws_thread and self._ws_thread.is_alive():
            self._ws_thread.join(timeout=1.0)
        self.reset()

    def reset(self):
        self.connected = False
        self.opponent_joined = False
        self.game_started = False
        self.websocket = None
        self.room_code = None
        self.opponent_data = {"score": 0, "alive": True, "game_started": False}
        self.connection_error = None
        self.room_full = False
        self._ws_thread = None
        self._stop_event = threading.Event()
        print("Online client completely reset for new game")

    def is_opponent_alive(self):
        return self.opponent_data.get("alive", False)

    def get_opponent_score(self):
        return self.opponent_data.get("score", 0)

    def has_opponent_joined(self):
        return self.opponent_joined

    def start_game(self):
        self.game_started = True

    def is_opponent_ready(self):
        return self.opponent_data.get("game_started", False)

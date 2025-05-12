from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from collections import defaultdict

app = FastAPI()
rooms = defaultdict(list)

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await websocket.accept()

    if len(rooms[room_code]) >= 2:
        await websocket.send_text("ROOM_FULL")
        await websocket.close()
        return

    rooms[room_code].append(websocket)
    print(f"[ROOM {room_code}] Players: {len(rooms[room_code])}/2")

    # Notify both clients if this is the second player joining
    if len(rooms[room_code]) == 2:
        for ws in rooms[room_code]:
            await ws.send_text("OPPONENT_JOINED")

    try:
        while True:
            data = await websocket.receive_text()
            for ws in rooms[room_code]:
                if ws != websocket:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        rooms[room_code].remove(websocket)
        if not rooms[room_code]:
            del rooms[room_code]
        print(f"[DISCONNECT] {room_code}")

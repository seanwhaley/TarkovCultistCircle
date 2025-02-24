"""WebSocket support using Flask-Sockets."""
import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from flask import current_app
from geventwebsocket import WebSocketError
from geventwebsocket.websocket import WebSocket

logger = logging.getLogger(__name__)

@dataclass
class MarketUpdate:
    """Market update event model."""
    item_id: str
    price: float
    timestamp: datetime
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = asdict(self)
        data['timestamp'] = data['timestamp'].isoformat()
        return json.dumps(data)

class ConnectionManager:
    """WebSocket connection manager."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        
    def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Register new connection."""
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client connected: {client_id}")
        
    def disconnect(self, client_id: str) -> None:
        """Remove connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"Client disconnected: {client_id}")
        
    def subscribe(self, client_id: str, item_id: str) -> None:
        """Subscribe client to item updates."""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].add(item_id)
            
    def unsubscribe(self, client_id: str, item_id: str) -> None:
        """Unsubscribe client from item updates."""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(item_id)
            
    async def broadcast_update(self, update: MarketUpdate) -> None:
        """Send update to all subscribed clients."""
        message = update.to_json()
        disconnected = []
        
        for client_id, subscriptions in self.subscriptions.items():
            if update.item_id in subscriptions:
                try:
                    ws = self.active_connections[client_id]
                    if not ws.closed:
                        ws.send(message)
                except (WebSocketError, KeyError) as e:
                    logger.error(f"Failed to send to client {client_id}: {str(e)}")
                    disconnected.append(client_id)
                    
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

# Global connection manager
manager = ConnectionManager()
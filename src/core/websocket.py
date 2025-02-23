from datetime import datetime
import json
import logging
from typing import Dict, List, Optional, Set
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MarketUpdate(BaseModel):
    """Market update event model."""
    item_id: str
    price: float
    timestamp: datetime
    update_type: str  # 'price_change', 'blacklist', 'lock', etc.

class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        # Store active connections
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "market_updates": set(),
            "item_updates": set()
        }
        
        # Store item subscriptions
        self.item_subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "market_updates"
    ) -> None:
        """Connect a websocket client."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to channel: {channel}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a websocket client."""
        # Remove from all channels
        for connections in self.active_connections.values():
            connections.discard(websocket)
            
        # Remove from item subscriptions
        for subscribers in self.item_subscriptions.values():
            subscribers.discard(websocket)
        
        logger.info("Client disconnected")

    async def subscribe_to_item(
        self,
        websocket: WebSocket,
        item_id: str
    ) -> None:
        """Subscribe to updates for a specific item."""
        if item_id not in self.item_subscriptions:
            self.item_subscriptions[item_id] = set()
        self.item_subscriptions[item_id].add(websocket)
        logger.info(f"Client subscribed to item: {item_id}")

    async def unsubscribe_from_item(
        self,
        websocket: WebSocket,
        item_id: str
    ) -> None:
        """Unsubscribe from updates for a specific item."""
        if item_id in self.item_subscriptions:
            self.item_subscriptions[item_id].discard(websocket)
            logger.info(f"Client unsubscribed from item: {item_id}")

    async def broadcast_market_update(self, update: MarketUpdate) -> None:
        """Broadcast a market update to all subscribers."""
        # Prepare message
        message = update.model_dump_json()
        
        # Send to general market update subscribers
        await self._broadcast(message, "market_updates")
        
        # Send to item-specific subscribers
        if update.item_id in self.item_subscriptions:
            for connection in self.item_subscriptions[update.item_id].copy():
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    self.disconnect(connection)

    async def _broadcast(self, message: str, channel: str) -> None:
        """Broadcast a message to all connections in a channel."""
        if channel not in self.active_connections:
            return
            
        for connection in self.active_connections[channel].copy():
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)

    async def handle_client(
        self,
        websocket: WebSocket,
        channel: str = "market_updates"
    ) -> None:
        """Handle individual client connection."""
        await self.connect(websocket, channel)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    
                    # Handle subscription messages
                    if message.get("type") == "subscribe":
                        item_id = message.get("item_id")
                        if item_id:
                            await self.subscribe_to_item(websocket, item_id)
                            await websocket.send_json({
                                "type": "subscribed",
                                "item_id": item_id
                            })
                            
                    elif message.get("type") == "unsubscribe":
                        item_id = message.get("item_id")
                        if item_id:
                            await self.unsubscribe_from_item(websocket, item_id)
                            await websocket.send_json({
                                "type": "unsubscribed",
                                "item_id": item_id
                            })
                            
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON message")
                    continue
                    
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            self.disconnect(websocket)

# Create global connection manager
manager = ConnectionManager()
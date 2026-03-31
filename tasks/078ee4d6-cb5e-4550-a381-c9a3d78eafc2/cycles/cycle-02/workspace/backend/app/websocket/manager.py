import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.auth import get_current_user_from_token
from app.models import User
from app.schemas import NotificationCreate, NotificationType
from app.api.notifications import create_notification

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and real-time notifications."""
    
    def __init__(self):
        # user_id -> set of active WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # connection_id -> (user_id, WebSocket)
        self.connection_map: Dict[str, tuple[int, WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int) -> str:
        """Accept WebSocket connection and register it."""
        await websocket.accept()
        connection_id = str(uuid4())
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_map[connection_id] = (user_id, websocket)
        
        logger.info(f"User {user_id} connected via WebSocket (connection_id: {connection_id})")
        logger.info(f"Active users: {len(self.active_connections)}, Total connections: {len(self.connection_map)}")
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": "WebSocket connection established",
                "connection_id": connection_id
            },
            websocket
        )
        
        return connection_id
    
    def disconnect(self, connection_id: str) -> None:
        """Remove WebSocket connection from active connections."""
        if connection_id in self.connection_map:
            user_id, websocket = self.connection_map[connection_id]
            
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.connection_map[connection_id]
            
            logger.info(f"User {user_id} disconnected from WebSocket (connection_id: {connection_id})")
            logger.info(f"Active users: {len(self.active_connections)}, Total connections: {len(self.connection_map)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def send_to_user(self, user_id: int, message: dict) -> bool:
        """Send message to all connections of a specific user."""
        if user_id not in self.active_connections:
            return False
        
        success = False
        dead_connections = []
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
                success = True
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for websocket in dead_connections:
            # Find and remove the dead connection
            for conn_id, (uid, ws) in list(self.connection_map.items()):
                if ws == websocket:
                    self.disconnect(conn_id)
                    break
        
        return success
    
    async def broadcast(self, message: dict, exclude_user_ids: Optional[Set[int]] = None) -> None:
        """Broadcast message to all connected users."""
        if exclude_user_ids is None:
            exclude_user_ids = set()
        
        dead_connections = []
        
        for user_id, connections in self.active_connections.items():
            if user_id in exclude_user_ids:
                continue
            
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    dead_connections.append((user_id, websocket))
        
        # Clean up dead connections
        for user_id, websocket in dead_connections:
            # Find and remove the dead connection
            for conn_id, (uid, ws) in list(self.connection_map.items()):
                if uid == user_id and ws == websocket:
                    self.disconnect(conn_id)
                    break
    
    async def send_notification(self, user_id: int, notification_data: dict, db_session: AsyncSession) -> None:
        """Send real-time notification to user and persist it in database."""
        # Create notification in database
        notification_create = NotificationCreate(
            type=notification_data.get("type", NotificationType.INFO),
            title=notification_data.get("title", ""),
            message=notification_data.get("message", ""),
            data=notification_data.get("data", {})
        )
        
        notification = await create_notification(
            user_id=user_id,
            notification_create=notification_create,
            db=db_session
        )
        
        # Prepare WebSocket message
        ws_message = {
            "type": "notification",
            "notification": {
                "id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
        }
        
        # Send via WebSocket if user is connected
        await self.send_to_user(user_id, ws_message)
    
    async def handle_new_post(self, post_data: dict, db_session: AsyncSession) -> None:
        """Handle notification for new post in a thread."""
        thread_id = post_data.get("thread_id")
        author_id = post_data.get("author_id")
        thread_author_id = post_data.get("thread_author_id")
        thread_title = post_data.get("thread_title", "")
        
        # Notify thread author if it's not their own reply
        if thread_author_id and thread_author_id != author_id:
            notification_data = {
                "type": NotificationType.NEW_REPLY,
                "title": "New Reply to Your Thread",
                "message": f"Someone replied to your thread: {thread_title}",
                "data": {
                    "thread_id": thread_id,
                    "post_id": post_data.get("id"),
                    "author_id": author_id
                }
            }
            await self.send_notification(thread_author_id, notification_data, db_session)
        
        # TODO: Notify other users who subscribed to the thread
    
    async def handle_new_vote(self, vote_data: dict, db_session: AsyncSession) -> None:
        """Handle notification for new vote on a post."""
        post_id = vote_data.get("post_id")
        voter_id = vote_data.get("voter_id")
        post_author_id = vote_data.get("post_author_id")
        value = vote_data.get("value")
        
        # Notify post author if it's not their own vote
        if post_author_id and post_author_id != voter_id:
            vote_type = "upvote" if value > 0 else "downvote"
            notification_data = {
                "type": NotificationType.NEW_VOTE,
                "title": f"New {vote_type.capitalize()} on Your Post",
                "message": f"Your post received a {vote_type}",
                "data": {
                    "post_id": post_id,
                    "voter_id": voter_id,
                    "value": value
                }
            }
            await self.send_notification(post_author_id, notification_data, db_session)
    
    async def handle_user_mention(self, mention_data: dict, db_session: AsyncSession) -> None:
        """Handle notification for user mention in a post."""
        mentioned_user_id = mention_data.get("mentioned_user_id")
        post_id = mention_data.get("post_id")
        thread_id = mention_data.get("thread_id")
        mentioner_id = mention_data.get("mentioner_id")
        
        if mentioned_user_id:
            notification_data = {
                "type": NotificationType.MENTION,
                "title": "You Were Mentioned",
                "message": f"You were mentioned in a post",
                "data": {
                    "post_id": post_id,
                    "thread_id": thread_id,
                    "mentioner_id": mentioner_id
                }
            }
            await self.send_notification(mentioned_user_id, notification_data, db_session)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time communication."""
    connection_id = None
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Authenticate user
        db_session_gen = get_db_session()
        db_session = await anext(db_session_gen)
        
        try:
            user = await get_current_user_from_token(token, db_session)
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Establish connection
            connection_id = await manager.connect(websocket, user.id)
            
            # Keep connection alive and handle messages
            while True:
                try:
                    data = await websocket.receive_json(timeout=300)  # 5 minute timeout
                    
                    # Handle ping/pong for keepalive
                    if data.get("type") == "ping":
                        await manager.send_personal_message({"type": "pong"}, websocket)
                    
                    # Handle other message types if needed
                    # For now, just log received messages
                    logger.debug(f"Received message from user {user.id}: {data}")
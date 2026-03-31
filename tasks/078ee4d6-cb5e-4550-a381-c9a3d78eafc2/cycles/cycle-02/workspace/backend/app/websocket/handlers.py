import json
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Notification, Thread, Post
from app.auth import get_current_user_from_token
from app.websocket.manager import ConnectionManager

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and message processing."""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def handle_connection(self, websocket: WebSocket, token: str):
        """Handle a new WebSocket connection with authentication."""
        try:
            # Authenticate user from token
            db = next(get_db())
            user = await get_current_user_from_token(token, db)
            
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Accept connection
            await websocket.accept()
            
            # Register connection
            await self.manager.connect(websocket, user.id)
            
            logger.info(f"WebSocket connected for user {user.username} (ID: {user.id})")
            
            # Send initial notification count
            unread_count = db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.is_read == False
            ).count()
            
            await self.manager.send_personal_message({
                "type": "initial",
                "unread_notifications": unread_count
            }, websocket)
            
            # Handle messages
            await self.handle_messages(websocket, user, db)
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            try:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            except:
                pass
        finally:
            # Ensure cleanup
            await self.manager.disconnect(websocket)
    
    async def handle_messages(self, websocket: WebSocket, user: User, db: Session):
        """Handle incoming WebSocket messages."""
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "Invalid JSON format")
                    continue
                
                # Process message based on type
                await self.process_message(message, websocket, user, db)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.username}")
        except Exception as e:
            logger.error(f"WebSocket message handling error: {e}")
    
    async def process_message(self, message: Dict[str, Any], websocket: WebSocket, 
                            user: User, db: Session):
        """Process incoming WebSocket message."""
        msg_type = message.get("type")
        
        if msg_type == "ping":
            await self.handle_ping(websocket, message)
        elif msg_type == "subscribe":
            await self.handle_subscribe(websocket, message, user, db)
        elif msg_type == "unsubscribe":
            await self.handle_unsubscribe(websocket, message, user)
        elif msg_type == "mark_notification_read":
            await self.handle_mark_notification_read(websocket, message, user, db)
        else:
            await self.send_error(websocket, f"Unknown message type: {msg_type}")
    
    async def handle_ping(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle ping message (keep-alive)."""
        await self.manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, websocket)
    
    async def handle_subscribe(self, websocket: WebSocket, message: Dict[str, Any], 
                             user: User, db: Session):
        """Handle subscription to a thread for real-time updates."""
        thread_id = message.get("thread_id")
        
        if not thread_id:
            await self.send_error(websocket, "Missing thread_id for subscription")
            return
        
        # Verify thread exists and user has access
        thread = db.query(Thread).filter(Thread.id == thread_id).first()
        if not thread:
            await self.send_error(websocket, f"Thread {thread_id} not found")
            return
        
        # Subscribe to thread updates
        await self.manager.subscribe_to_thread(websocket, thread_id)
        
        await self.manager.send_personal_message({
            "type": "subscribed",
            "thread_id": thread_id,
            "thread_title": thread.title
        }, websocket)
        
        logger.info(f"User {user.username} subscribed to thread {thread_id}")
    
    async def handle_unsubscribe(self, websocket: WebSocket, message: Dict[str, Any], 
                               user: User):
        """Handle unsubscription from a thread."""
        thread_id = message.get("thread_id")
        
        if not thread_id:
            await self.send_error(websocket, "Missing thread_id for unsubscription")
            return
        
        # Unsubscribe from thread updates
        await self.manager.unsubscribe_from_thread(websocket, thread_id)
        
        await self.manager.send_personal_message({
            "type": "unsubscribed",
            "thread_id": thread_id
        }, websocket)
        
        logger.info(f"User {user.username} unsubscribed from thread {thread_id}")
    
    async def handle_mark_notification_read(self, websocket: WebSocket, 
                                          message: Dict[str, Any], user: User, 
                                          db: Session):
        """Handle marking a notification as read."""
        notification_id = message.get("notification_id")
        
        if not notification_id:
            await self.send_error(websocket, "Missing notification_id")
            return
        
        # Find and update notification
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user.id
        ).first()
        
        if not notification:
            await self.send_error(websocket, f"Notification {notification_id} not found")
            return
        
        # Mark as read
        notification.is_read = True
        db.commit()
        
        # Send confirmation
        await self.manager.send_personal_message({
            "type": "notification_marked_read",
            "notification_id": notification_id
        }, websocket)
        
        logger.info(f"User {user.username} marked notification {notification_id} as read")
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send error message to client."""
        await self.manager.send_personal_message({
            "type": "error",
            "message": error_message
        }, websocket)
    
    async def broadcast_new_post(self, post: Post, thread_id: int):
        """Broadcast new post to all subscribers of a thread."""
        message = {
            "type": "new_post",
            "post": {
                "id": post.id,
                "content": post.content,
                "author_id": post.author_id,
                "author_username": post.author.username,
                "thread_id": post.thread_id,
                "created_at": post.created_at.isoformat(),
                "parent_id": post.parent_id
            }
        }
        
        await self.manager.broadcast_to_thread(thread_id, message)
        logger.info(f"Broadcast new post {post.id} to thread {thread_id} subscribers")
    
    async def broadcast_new_vote(self, post_id: int, thread_id: int, 
                               user_id: int, value: int):
        """Broadcast new vote to all subscribers of a thread."""
        message = {
            "type": "new_vote",
            "post_id": post_id,
            "user_id": user_id,
            "value": value
        }
        
        await self.manager.broadcast_to_thread(thread_id, message)
        logger.info(f"Broadcast new vote on post {post_id} to thread {thread_id} subscribers")
    
    async def send_notification(self, user_id: int, notification_data: Dict[str, Any]):
        """Send a notification to a specific user."""
        message = {
            "type": "new_notification",
            "notification": notification_data
        }
        
        await self.manager.send_to_user(user_id, message)
        
        # Also update unread count
        await self.manager.send_to_user(user_id, {
            "type": "unread_count_update",
            "unread_notifications": notification_data.get("unread_count", 0)
        })
        
        logger.info(f"Sent notification to user {user_id}: {notification_data.get('title')}")


# Global WebSocket handler instance
websocket_handler: Optional[WebSocketHandler] = None


def get_websocket_handler() -> WebSocketHandler:
    """Get or create WebSocket handler instance."""
    global websocket_handler
    
    if websocket_handler is None:
        from app.websocket.manager import connection_manager
        websocket_handler = WebSocketHandler(connection_manager)
    
    return websocket_handler
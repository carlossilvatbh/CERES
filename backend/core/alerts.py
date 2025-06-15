"""
Real-time Alert System for CERES
WebSocket-based alerts with different severity levels
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger('ceres.alerts')

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Alert types"""
    HIGH_RISK_MATCH = "high_risk_match"
    DOCUMENT_PROCESSING_ERROR = "document_processing_error"
    SYSTEM_ERROR = "system_error"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    PERFORMANCE_ISSUE = "performance_issue"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    customer_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    acknowledged: bool = False
    resolved: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for JSON serialization"""
        data = asdict(self)
        data['alert_type'] = self.alert_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data

class AlertManager:
    """
    Manages alert creation, distribution, and persistence
    """
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.subscribers: Dict[str, List[str]] = {}  # user_id -> [channel_names]
        self.alert_history: List[Alert] = []
    
    async def create_alert(self, alert_type: AlertType, severity: AlertSeverity,
                          title: str, message: str, customer_id: Optional[str] = None,
                          user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """
        Create and distribute a new alert
        
        Args:
            alert_type: Type of alert
            severity: Severity level
            title: Alert title
            message: Alert message
            customer_id: Optional customer ID
            user_id: Optional user ID
            metadata: Optional additional data
            
        Returns:
            Created alert
        """
        try:
            # Generate alert ID
            alert_id = f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Create alert
            alert = Alert(
                id=alert_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                customer_id=customer_id,
                user_id=user_id,
                metadata=metadata or {}
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Persist to database
            await self._persist_alert(alert)
            
            # Distribute alert
            await self._distribute_alert(alert)
            
            logger.info(f"Alert created: {alert_id} ({severity.value})")
            return alert
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: Alert ID
            user_id: User acknowledging the alert
            
        Returns:
            Success status
        """
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.acknowledged = True
                alert.metadata = alert.metadata or {}
                alert.metadata['acknowledged_by'] = user_id
                alert.metadata['acknowledged_at'] = datetime.now().isoformat()
                
                # Update in database
                await self._update_alert(alert)
                
                # Notify subscribers
                await self._notify_alert_update(alert)
                
                logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_note: Optional[str] = None) -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: Alert ID
            user_id: User resolving the alert
            resolution_note: Optional resolution note
            
        Returns:
            Success status
        """
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.metadata = alert.metadata or {}
                alert.metadata['resolved_by'] = user_id
                alert.metadata['resolved_at'] = datetime.now().isoformat()
                if resolution_note:
                    alert.metadata['resolution_note'] = resolution_note
                
                # Update in database
                await self._update_alert(alert)
                
                # Notify subscribers
                await self._notify_alert_update(alert)
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                logger.info(f"Alert resolved: {alert_id} by {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    async def subscribe_user(self, user_id: str, channel_name: str):
        """Subscribe user to alerts"""
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        
        if channel_name not in self.subscribers[user_id]:
            self.subscribers[user_id].append(channel_name)
            logger.debug(f"User {user_id} subscribed to alerts via {channel_name}")
    
    async def unsubscribe_user(self, user_id: str, channel_name: str):
        """Unsubscribe user from alerts"""
        if user_id in self.subscribers:
            if channel_name in self.subscribers[user_id]:
                self.subscribers[user_id].remove(channel_name)
                if not self.subscribers[user_id]:
                    del self.subscribers[user_id]
                logger.debug(f"User {user_id} unsubscribed from alerts via {channel_name}")
    
    async def get_active_alerts(self, user_id: Optional[str] = None, 
                               severity_filter: Optional[List[AlertSeverity]] = None) -> List[Alert]:
        """
        Get active alerts with optional filtering
        
        Args:
            user_id: Optional user ID filter
            severity_filter: Optional severity filter
            
        Returns:
            List of filtered alerts
        """
        alerts = list(self.active_alerts.values())
        
        # Filter by user
        if user_id:
            alerts = [a for a in alerts if a.user_id == user_id or a.user_id is None]
        
        # Filter by severity
        if severity_filter:
            alerts = [a for a in alerts if a.severity in severity_filter]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts
    
    async def _persist_alert(self, alert: Alert):
        """Persist alert to database"""
        try:
            from sanctions_screening.models import ScreeningAlert
            
            await database_sync_to_async(ScreeningAlert.objects.create)(
                alert_id=alert.id,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value,
                title=alert.title,
                message=alert.message,
                customer_id=alert.customer_id,
                user_id=alert.user_id,
                alert_data=alert.metadata or {},
                acknowledged=alert.acknowledged,
                resolved=alert.resolved
            )
            
        except Exception as e:
            logger.error(f"Failed to persist alert {alert.id}: {e}")
    
    async def _update_alert(self, alert: Alert):
        """Update alert in database"""
        try:
            from sanctions_screening.models import ScreeningAlert
            
            db_alert = await database_sync_to_async(
                ScreeningAlert.objects.get
            )(alert_id=alert.id)
            
            db_alert.acknowledged = alert.acknowledged
            db_alert.resolved = alert.resolved
            db_alert.alert_data = alert.metadata or {}
            
            await database_sync_to_async(db_alert.save)()
            
        except Exception as e:
            logger.error(f"Failed to update alert {alert.id}: {e}")
    
    async def _distribute_alert(self, alert: Alert):
        """Distribute alert to subscribers"""
        try:
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                logger.warning("No channel layer configured for alerts")
                return
            
            # Prepare alert data
            alert_data = {
                'type': 'alert_message',
                'alert': alert.to_dict()
            }
            
            # Send to all subscribers or specific user
            if alert.user_id:
                # Send to specific user
                if alert.user_id in self.subscribers:
                    for channel_name in self.subscribers[alert.user_id]:
                        await channel_layer.send(channel_name, alert_data)
            else:
                # Send to all subscribers
                for user_id, channel_names in self.subscribers.items():
                    for channel_name in channel_names:
                        await channel_layer.send(channel_name, alert_data)
            
        except Exception as e:
            logger.error(f"Failed to distribute alert {alert.id}: {e}")
    
    async def _notify_alert_update(self, alert: Alert):
        """Notify subscribers of alert update"""
        try:
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return
            
            # Prepare update data
            update_data = {
                'type': 'alert_update',
                'alert': alert.to_dict()
            }
            
            # Send to all subscribers
            for user_id, channel_names in self.subscribers.items():
                for channel_name in channel_names:
                    await channel_layer.send(channel_name, update_data)
            
        except Exception as e:
            logger.error(f"Failed to notify alert update {alert.id}: {e}")

# Global alert manager instance
alert_manager = AlertManager()

class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time alerts
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get user from scope
            user = self.scope.get('user')
            if not user or not user.is_authenticated:
                await self.close()
                return
            
            self.user_id = str(user.id)
            
            # Accept connection
            await self.accept()
            
            # Subscribe to alerts
            await alert_manager.subscribe_user(self.user_id, self.channel_name)
            
            # Send current active alerts
            active_alerts = await alert_manager.get_active_alerts(self.user_id)
            await self.send(text_data=json.dumps({
                'type': 'active_alerts',
                'alerts': [alert.to_dict() for alert in active_alerts]
            }, cls=DjangoJSONEncoder))
            
            logger.info(f"Alert WebSocket connected for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Alert WebSocket connection failed: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if hasattr(self, 'user_id'):
                await alert_manager.unsubscribe_user(self.user_id, self.channel_name)
                logger.info(f"Alert WebSocket disconnected for user {self.user_id}")
        except Exception as e:
            logger.error(f"Alert WebSocket disconnect error: {e}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'acknowledge_alert':
                alert_id = data.get('alert_id')
                if alert_id:
                    await alert_manager.acknowledge_alert(alert_id, self.user_id)
            
            elif message_type == 'resolve_alert':
                alert_id = data.get('alert_id')
                resolution_note = data.get('resolution_note')
                if alert_id:
                    await alert_manager.resolve_alert(alert_id, self.user_id, resolution_note)
            
            elif message_type == 'get_alerts':
                severity_filter = data.get('severity_filter')
                if severity_filter:
                    severity_filter = [AlertSeverity(s) for s in severity_filter]
                
                alerts = await alert_manager.get_active_alerts(self.user_id, severity_filter)
                await self.send(text_data=json.dumps({
                    'type': 'active_alerts',
                    'alerts': [alert.to_dict() for alert in alerts]
                }, cls=DjangoJSONEncoder))
            
        except Exception as e:
            logger.error(f"Alert WebSocket receive error: {e}")
    
    async def alert_message(self, event):
        """Handle alert message from channel layer"""
        try:
            await self.send(text_data=json.dumps(event, cls=DjangoJSONEncoder))
        except Exception as e:
            logger.error(f"Failed to send alert message: {e}")
    
    async def alert_update(self, event):
        """Handle alert update from channel layer"""
        try:
            await self.send(text_data=json.dumps(event, cls=DjangoJSONEncoder))
        except Exception as e:
            logger.error(f"Failed to send alert update: {e}")

# Utility functions for creating specific alert types
async def create_high_risk_match_alert(customer_id: str, match_details: Dict[str, Any]):
    """Create alert for high-risk screening match"""
    return await alert_manager.create_alert(
        alert_type=AlertType.HIGH_RISK_MATCH,
        severity=AlertSeverity.HIGH,
        title=f"High-Risk Match Detected",
        message=f"Customer {customer_id} matched high-risk entity: {match_details.get('matched_name', 'Unknown')}",
        customer_id=customer_id,
        metadata=match_details
    )

async def create_document_processing_error_alert(customer_id: str, error_details: Dict[str, Any]):
    """Create alert for document processing error"""
    return await alert_manager.create_alert(
        alert_type=AlertType.DOCUMENT_PROCESSING_ERROR,
        severity=AlertSeverity.MEDIUM,
        title="Document Processing Error",
        message=f"Failed to process document for customer {customer_id}",
        customer_id=customer_id,
        metadata=error_details
    )

async def create_system_error_alert(error_message: str, error_details: Dict[str, Any]):
    """Create alert for system error"""
    return await alert_manager.create_alert(
        alert_type=AlertType.SYSTEM_ERROR,
        severity=AlertSeverity.CRITICAL,
        title="System Error",
        message=error_message,
        metadata=error_details
    )


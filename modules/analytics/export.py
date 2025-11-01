"""
Data Export System for DianaBot Analytics
Exports analytics data in multiple formats
"""

import logging
import json
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class ExportRequest:
    """Export request data structure"""
    export_id: str
    export_type: str  # "user_data", "analytics", "transactions", "content"
    format: str  # "json", "csv", "excel"
    filters: Dict[str, Any]
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    include_sensitive: bool = False


@dataclass
class ExportResult:
    """Export result data structure"""
    export_id: str
    export_type: str
    format: str
    generated_at: datetime
    file_size: int
    download_url: Optional[str] = None
    content: Optional[str] = None
    status: str = "completed"  # "completed", "failed", "processing"


class DataExporter:
    """Exports analytics data in multiple formats"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def export_data(self, request: ExportRequest) -> ExportResult:
        """Export data based on request"""
        logger.info(f"Exporting data: {request.export_type} in {request.format}")
        
        try:
            # Generate data based on export type
            data = self._generate_export_data(request)
            
            # Convert to requested format
            content = self._convert_to_format(data, request.format, request)
            
            # Calculate file size
            file_size = len(content.encode('utf-8')) if content else 0
            
            return ExportResult(
                export_id=request.export_id,
                export_type=request.export_type,
                format=request.format,
                generated_at=datetime.now(),
                file_size=file_size,
                content=content,
                status="completed"
            )
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ExportResult(
                export_id=request.export_id,
                export_type=request.export_type,
                format=request.format,
                generated_at=datetime.now(),
                file_size=0,
                status="failed"
            )
    
    def export_user_data(self, user_id: int, format: str = "json", 
                        include_sensitive: bool = False) -> ExportResult:
        """Export user data for GDPR compliance"""
        request = ExportRequest(
            export_id=f"user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            export_type="user_data",
            format=format,
            filters={'user_id': user_id},
            include_sensitive=include_sensitive
        )
        
        return self.export_data(request)
    
    def export_analytics_data(self, time_range_start: datetime, 
                            time_range_end: datetime, format: str = "csv") -> ExportResult:
        """Export analytics data for external analysis"""
        request = ExportRequest(
            export_id=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            export_type="analytics",
            format=format,
            filters={},
            time_range_start=time_range_start,
            time_range_end=time_range_end
        )
        
        return self.export_data(request)
    
    def export_transaction_data(self, time_range_start: datetime, 
                              time_range_end: datetime, format: str = "excel") -> ExportResult:
        """Export transaction data for accounting"""
        request = ExportRequest(
            export_id=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            export_type="transactions",
            format=format,
            filters={},
            time_range_start=time_range_start,
            time_range_end=time_range_end
        )
        
        return self.export_data(request)
    
    def export_content_data(self, format: str = "json") -> ExportResult:
        """Export content data for backup or migration"""
        request = ExportRequest(
            export_id=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            export_type="content",
            format=format,
            filters={}
        )
        
        return self.export_data(request)
    
    # Private helper methods
    
    def _generate_export_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate data for export based on request type"""
        if request.export_type == "user_data":
            return self._generate_user_data(request)
        elif request.export_type == "analytics":
            return self._generate_analytics_data(request)
        elif request.export_type == "transactions":
            return self._generate_transaction_data(request)
        elif request.export_type == "content":
            return self._generate_content_data(request)
        else:
            raise ValueError(f"Unsupported export type: {request.export_type}")
    
    def _generate_user_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate user data for export"""
        from database.models import User, Subscription, UserBalance, UserInventory
        
        user_id = request.filters.get('user_id')
        if not user_id:
            raise ValueError("User ID is required for user data export")
        
        # Get user data
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        user_data = {
            'user_info': {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'subscriptions': [],
            'balance': {},
            'inventory': []
        }
        
        # Get subscription data
        subscriptions = self.db.query(Subscription).filter(Subscription.user_id == user_id).all()
        for sub in subscriptions:
            user_data['subscriptions'].append({
                'id': sub.id,
                'status': sub.status,
                'start_date': sub.start_date.isoformat() if sub.start_date else None,
                'end_date': sub.end_date.isoformat() if sub.end_date else None,
                'created_at': sub.created_at.isoformat() if sub.created_at else None
            })
        
        # Get balance data
        balance = self.db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        if balance:
            user_data['balance'] = {
                'besitos': balance.besitos,
                'premium_currency': balance.premium_currency,
                'updated_at': balance.updated_at.isoformat() if balance.updated_at else None
            }
        
        # Get inventory data
        inventory = self.db.query(UserInventory).filter(UserInventory.user_id == user_id).all()
        for item in inventory:
            user_data['inventory'].append({
                'item_id': item.item_id,
                'quantity': item.quantity,
                'acquired_at': item.acquired_at.isoformat() if item.acquired_at else None
            })
        
        # Include sensitive data if requested
        if request.include_sensitive:
            # Add any sensitive data here
            pass
        
        return user_data
    
    def _generate_analytics_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate analytics data for export"""
        from database.models import AnalyticsEvent
        from .aggregator import MetricsAggregator, TimeRange
        
        time_range = TimeRange(
            request.time_range_start or (datetime.now() - timedelta(days=30)),
            request.time_range_end or datetime.now()
        )
        
        aggregator = MetricsAggregator(self.db)
        
        # Get aggregated metrics
        engagement_metrics = aggregator.get_engagement_metrics(time_range)
        monetization_metrics = aggregator.get_monetization_metrics(time_range)
        narrative_metrics = aggregator.get_narrative_metrics(time_range)
        experience_metrics = aggregator.get_experience_metrics(time_range)
        
        # Get raw events (limited for performance)
        events = self.db.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= time_range.start_date,
            AnalyticsEvent.timestamp <= time_range.end_date
        ).limit(1000).all()
        
        analytics_data = {
            'time_range': {
                'start': time_range.start_date.isoformat(),
                'end': time_range.end_date.isoformat()
            },
            'aggregated_metrics': {
                'engagement': {
                    'mau': engagement_metrics.mau,
                    'dau': engagement_metrics.dau,
                    'retention_d1': engagement_metrics.retention_d1,
                    'retention_d7': engagement_metrics.retention_d7,
                    'retention_d30': engagement_metrics.retention_d30,
                    'avg_session_duration': engagement_metrics.avg_session_duration,
                    'engagement_by_module': engagement_metrics.engagement_by_module
                },
                'monetization': {
                    'total_revenue': monetization_metrics.total_revenue,
                    'arpu': monetization_metrics.arpu,
                    'arppu': monetization_metrics.arppu,
                    'free_to_vip_conversion': monetization_metrics.free_to_vip_conversion,
                    'ltv': monetization_metrics.ltv,
                    'revenue_by_product': monetization_metrics.revenue_by_product
                },
                'narrative': {
                    'most_visited_fragments': narrative_metrics.most_visited_fragments,
                    'completion_rate': narrative_metrics.completion_rate,
                    'popular_decisions': narrative_metrics.popular_decisions,
                    'drop_off_points': narrative_metrics.drop_off_points
                },
                'experiences': {
                    'start_rate': experience_metrics.start_rate,
                    'completion_rate': experience_metrics.completion_rate,
                    'avg_completion_time': experience_metrics.avg_completion_time,
                    'popular_experiences': experience_metrics.popular_experiences
                }
            },
            'sample_events': [
                {
                    'id': event.id,
                    'user_id': event.user_id,
                    'event_type': event.event_type,
                    'timestamp': event.timestamp.isoformat(),
                    'metadata': event.metadata
                }
                for event in events
            ]
        }
        
        return analytics_data
    
    def _generate_transaction_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate transaction data for export"""
        from database.models import Transaction
        
        time_range_start = request.time_range_start or (datetime.now() - timedelta(days=30))
        time_range_end = request.time_range_end or datetime.now()
        
        transactions = self.db.query(Transaction).filter(
            Transaction.created_at >= time_range_start,
            Transaction.created_at <= time_range_end
        ).all()
        
        transaction_data = {
            'time_range': {
                'start': time_range_start.isoformat(),
                'end': time_range_end.isoformat()
            },
            'transactions': [
                {
                    'id': tx.id,
                    'user_id': tx.user_id,
                    'amount': float(tx.amount) if tx.amount else 0,
                    'currency': tx.currency,
                    'product_type': tx.product_type,
                    'status': tx.status,
                    'created_at': tx.created_at.isoformat() if tx.created_at else None,
                    'completed_at': tx.completed_at.isoformat() if tx.completed_at else None
                }
                for tx in transactions
            ],
            'summary': {
                'total_transactions': len(transactions),
                'total_revenue': sum(float(tx.amount) for tx in transactions if tx.amount),
                'completed_transactions': len([tx for tx in transactions if tx.status == 'completed']),
                'failed_transactions': len([tx for tx in transactions if tx.status == 'failed'])
            }
        }
        
        return transaction_data
    
    def _generate_content_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate content data for export"""
        from database.models import NarrativeFragment, Mission, Achievement, ShopItem
        
        content_data = {
            'narrative_fragments': [],
            'missions': [],
            'achievements': [],
            'shop_items': []
        }
        
        # Get narrative fragments
        fragments = self.db.query(NarrativeFragment).filter(NarrativeFragment.is_active == True).all()
        for fragment in fragments:
            content_data['narrative_fragments'].append({
                'id': fragment.id,
                'fragment_key': fragment.fragment_key,
                'title': fragment.title,
                'content': fragment.content,
                'is_active': fragment.is_active,
                'created_at': fragment.created_at.isoformat() if fragment.created_at else None
            })
        
        # Get missions
        missions = self.db.query(Mission).filter(Mission.is_active == True).all()
        for mission in missions:
            content_data['missions'].append({
                'id': mission.id,
                'mission_key': mission.mission_key,
                'title': mission.title,
                'description': mission.description,
                'requirements': mission.requirements,
                'rewards': mission.rewards,
                'is_active': mission.is_active,
                'created_at': mission.created_at.isoformat() if mission.created_at else None
            })
        
        # Get achievements
        achievements = self.db.query(Achievement).all()
        for achievement in achievements:
            content_data['achievements'].append({
                'id': achievement.id,
                'achievement_key': achievement.achievement_key,
                'name': achievement.name,
                'description': achievement.description,
                'requirements': achievement.requirements,
                'rewards': achievement.rewards,
                'created_at': achievement.created_at.isoformat() if achievement.created_at else None
            })
        
        # Get shop items
        shop_items = self.db.query(ShopItem).all()
        for item in shop_items:
            content_data['shop_items'].append({
                'id': item.id,
                'item_key': item.item_key,
                'name': item.name,
                'description': item.description,
                'item_type': item.item_type,
                'rarity': item.rarity,
                'price_besitos': item.price_besitos,
                'price_premium': item.price_premium,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return content_data
    
    def _convert_to_format(self, data: Dict[str, Any], format: str, 
                          request: ExportRequest) -> str:
        """Convert data to requested format"""
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        
        elif format == "csv":
            return self._convert_to_csv(data, request)
        
        elif format == "excel":
            # In production, this would use openpyxl or similar
            # For now, return CSV as placeholder
            return self._convert_to_csv(data, request)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _convert_to_csv(self, data: Dict[str, Any], request: ExportRequest) -> str:
        """Convert data to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if request.export_type == "user_data":
            self._write_user_data_csv(writer, data)
        elif request.export_type == "analytics":
            self._write_analytics_data_csv(writer, data)
        elif request.export_type == "transactions":
            self._write_transaction_data_csv(writer, data)
        elif request.export_type == "content":
            self._write_content_data_csv(writer, data)
        
        return output.getvalue()
    
    def _write_user_data_csv(self, writer: csv.writer, data: Dict[str, Any]):
        """Write user data to CSV"""
        writer.writerow(['USER DATA EXPORT'])
        writer.writerow(['Generated At', datetime.now().isoformat()])
        writer.writerow([])
        
        # User info
        writer.writerow(['USER INFORMATION'])
        user_info = data.get('user_info', {})
        for key, value in user_info.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Subscriptions
        writer.writerow(['SUBSCRIPTIONS'])
        writer.writerow(['ID', 'Status', 'Start Date', 'End Date', 'Created At'])
        for sub in data.get('subscriptions', []):
            writer.writerow([
                sub.get('id'),
                sub.get('status'),
                sub.get('start_date'),
                sub.get('end_date'),
                sub.get('created_at')
            ])
        writer.writerow([])
        
        # Balance
        writer.writerow(['BALANCE'])
        balance = data.get('balance', {})
        for key, value in balance.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Inventory
        writer.writerow(['INVENTORY'])
        writer.writerow(['Item ID', 'Quantity', 'Acquired At'])
        for item in data.get('inventory', []):
            writer.writerow([
                item.get('item_id'),
                item.get('quantity'),
                item.get('acquired_at')
            ])
    
    def _write_analytics_data_csv(self, writer: csv.writer, data: Dict[str, Any]):
        """Write analytics data to CSV"""
        writer.writerow(['ANALYTICS DATA EXPORT'])
        writer.writerow(['Generated At', datetime.now().isoformat()])
        time_range = data.get('time_range', {})
        writer.writerow(['Time Range', f"{time_range.get('start')} to {time_range.get('end')}"])
        writer.writerow([])
        
        # Aggregated metrics
        metrics = data.get('aggregated_metrics', {})
        for category, category_metrics in metrics.items():
            writer.writerow([category.upper()])
            for key, value in category_metrics.items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key, value])
                elif isinstance(value, dict):
                    writer.writerow([key])
                    for sub_key, sub_value in value.items():
                        writer.writerow(['', sub_key, sub_value])
                elif isinstance(value, list):
                    writer.writerow([key])
                    for item in value:
                        if isinstance(item, dict):
                            writer.writerow(['', json.dumps(item)])
                        else:
                            writer.writerow(['', str(item)])
            writer.writerow([])
        
        # Sample events
        writer.writerow(['SAMPLE EVENTS'])
        writer.writerow(['ID', 'User ID', 'Event Type', 'Timestamp', 'Metadata'])
        for event in data.get('sample_events', []):
            writer.writerow([
                event.get('id'),
                event.get('user_id'),
                event.get('event_type'),
                event.get('timestamp'),
                json.dumps(event.get('metadata', {}))
            ])
    
    def _write_transaction_data_csv(self, writer: csv.writer, data: Dict[str, Any]):
        """Write transaction data to CSV"""
        writer.writerow(['TRANSACTION DATA EXPORT'])
        writer.writerow(['Generated At', datetime.now().isoformat()])
        time_range = data.get('time_range', {})
        writer.writerow(['Time Range', f"{time_range.get('start')} to {time_range.get('end')}"])
        writer.writerow([])
        
        # Summary
        summary = data.get('summary', {})
        writer.writerow(['SUMMARY'])
        for key, value in summary.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Transactions
        writer.writerow(['TRANSACTIONS'])
        writer.writerow(['ID', 'User ID', 'Amount', 'Currency', 'Product Type', 'Status', 'Created At', 'Completed At'])
        for tx in data.get('transactions', []):
            writer.writerow([
                tx.get('id'),
                tx.get('user_id'),
                tx.get('amount'),
                tx.get('currency'),
                tx.get('product_type'),
                tx.get('status'),
                tx.get('created_at'),
                tx.get('completed_at')
            ])
    
    def _write_content_data_csv(self, writer: csv.writer, data: Dict[str, Any]):
        """Write content data to CSV"""
        writer.writerow(['CONTENT DATA EXPORT'])
        writer.writerow(['Generated At', datetime.now().isoformat()])
        writer.writerow([])
        
        # Narrative fragments
        writer.writerow(['NARRATIVE FRAGMENTS'])
        writer.writerow(['ID', 'Fragment Key', 'Title', 'Is Active', 'Created At'])
        for fragment in data.get('narrative_fragments', []):
            writer.writerow([
                fragment.get('id'),
                fragment.get('fragment_key'),
                fragment.get('title'),
                fragment.get('is_active'),
                fragment.get('created_at')
            ])
        writer.writerow([])
        
        # Missions
        writer.writerow(['MISSIONS'])
        writer.writerow(['ID', 'Mission Key', 'Title', 'Is Active', 'Created At'])
        for mission in data.get('missions', []):
            writer.writerow([
                mission.get('id'),
                mission.get('mission_key'),
                mission.get('title'),
                mission.get('is_active'),
                mission.get('created_at')
            ])
        writer.writerow([])
        
        # Achievements
        writer.writerow(['ACHIEVEMENTS'])
        writer.writerow(['ID', 'Achievement Key', 'Name', 'Created At'])
        for achievement in data.get('achievements', []):
            writer.writerow([
                achievement.get('id'),
                achievement.get('achievement_key'),
                achievement.get('name'),
                achievement.get('created_at')
            ])
        writer.writerow([])
        
        # Shop items
        writer.writerow(['SHOP ITEMS'])
        writer.writerow(['ID', 'Item Key', 'Name', 'Item Type', 'Rarity', 'Price Besitos', 'Price Premium', 'Created At'])
        for item in data.get('shop_items', []):
            writer.writerow([
                item.get('id'),
                item.get('item_key'),
                item.get('name'),
                item.get('item_type'),
                item.get('rarity'),
                item.get('price_besitos'),
                item.get('price_premium'),
                item.get('created_at')
            ])
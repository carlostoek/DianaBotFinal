"""
Report Generation System for DianaBot Analytics
Generates automated reports in various formats
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
class ReportDefinition:
    """Report definition data structure"""
    report_id: str
    report_name: str
    report_type: str  # "executive", "revenue", "content", "experiences"
    frequency: str  # "daily", "weekly", "monthly"
    metrics: List[str]
    recipients: List[str]
    export_formats: List[str]  # "pdf", "excel", "csv", "json"
    is_active: bool = True


@dataclass
class GeneratedReport:
    """Generated report data structure"""
    report_id: str
    report_name: str
    generated_at: datetime
    time_range_start: datetime
    time_range_end: datetime
    data: Dict[str, Any]
    export_formats: Dict[str, str]  # format -> file_path or content
    status: str  # "generated", "failed", "processing"


class ReportGenerator:
    """Generates automated reports in various formats"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.report_definitions = self._load_report_definitions()
    
    def generate_report(self, report_id: str, time_range_start: datetime = None, 
                       time_range_end: datetime = None) -> GeneratedReport:
        """Generate a specific report"""
        logger.info(f"Generating report: {report_id}")
        
        report_def = self.report_definitions.get(report_id)
        if not report_def:
            raise ValueError(f"Report definition not found: {report_id}")
        
        if not report_def.is_active:
            raise ValueError(f"Report is not active: {report_id}")
        
        # Set default time range if not provided
        if time_range_start is None or time_range_end is None:
            time_range_start, time_range_end = self._get_default_time_range(report_def.frequency)
        
        # Generate report data
        report_data = self._generate_report_data(report_def, time_range_start, time_range_end)
        
        # Generate export formats
        export_formats = {}
        for format_type in report_def.export_formats:
            try:
                export_content = self._export_to_format(report_data, format_type, report_def)
                export_formats[format_type] = export_content
            except Exception as e:
                logger.error(f"Failed to export {report_id} to {format_type}: {e}")
        
        return GeneratedReport(
            report_id=report_id,
            report_name=report_def.report_name,
            generated_at=datetime.now(),
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            data=report_data,
            export_formats=export_formats,
            status="generated"
        )
    
    def generate_all_scheduled_reports(self) -> List[GeneratedReport]:
        """Generate all scheduled reports based on frequency"""
        logger.info("Generating all scheduled reports")
        
        generated_reports = []
        
        for report_id, report_def in self.report_definitions.items():
            if not report_def.is_active:
                continue
            
            # Check if report should be generated based on frequency
            if self._should_generate_report(report_def):
                try:
                    report = self.generate_report(report_id)
                    generated_reports.append(report)
                    
                    # Send to recipients
                    self._send_report_to_recipients(report, report_def.recipients)
                    
                except Exception as e:
                    logger.error(f"Failed to generate report {report_id}: {e}")
        
        return generated_reports
    
    def get_report_definitions(self) -> Dict[str, ReportDefinition]:
        """Get all report definitions"""
        return self.report_definitions
    
    def update_report_definition(self, report_id: str, definition: ReportDefinition) -> bool:
        """Update report definition"""
        self.report_definitions[report_id] = definition
        return True
    
    def create_report_definition(self, definition: ReportDefinition) -> bool:
        """Create new report definition"""
        if definition.report_id in self.report_definitions:
            raise ValueError(f"Report ID already exists: {definition.report_id}")
        
        self.report_definitions[definition.report_id] = definition
        return True
    
    # Private helper methods
    
    def _load_report_definitions(self) -> Dict[str, ReportDefinition]:
        """Load report definitions"""
        return {
            'executive_weekly': ReportDefinition(
                report_id='executive_weekly',
                report_name='Weekly Executive Report',
                report_type='executive',
                frequency='weekly',
                metrics=['mau', 'dau', 'revenue', 'conversion_rate', 'ltv'],
                recipients=['admin@dianabot.com'],
                export_formats=['pdf', 'excel']
            ),
            'revenue_monthly': ReportDefinition(
                report_id='revenue_monthly',
                report_name='Monthly Revenue Report',
                report_type='revenue',
                frequency='monthly',
                metrics=['total_revenue', 'arpu', 'arppu', 'revenue_by_product'],
                recipients=['admin@dianabot.com', 'finance@dianabot.com'],
                export_formats=['excel', 'csv']
            ),
            'content_performance': ReportDefinition(
                report_id='content_performance',
                report_name='Content Performance Report',
                report_type='content',
                frequency='weekly',
                metrics=['narrative_metrics', 'experience_metrics', 'popular_content'],
                recipients=['admin@dianabot.com', 'content@dianabot.com'],
                export_formats=['excel', 'json']
            ),
            'experiences_weekly': ReportDefinition(
                report_id='experiences_weekly',
                report_name='Weekly Experiences Report',
                report_type='experiences',
                frequency='weekly',
                metrics=['experience_start_rate', 'completion_rate', 'popular_experiences'],
                recipients=['admin@dianabot.com'],
                export_formats=['csv', 'json']
            )
        }
    
    def _get_default_time_range(self, frequency: str) -> Tuple[datetime, datetime]:
        """Get default time range based on frequency"""
        now = datetime.now()
        
        if frequency == 'daily':
            start = now - timedelta(days=1)
            end = now
        elif frequency == 'weekly':
            start = now - timedelta(days=7)
            end = now
        elif frequency == 'monthly':
            start = now - timedelta(days=30)
            end = now
        else:
            start = now - timedelta(days=7)
            end = now
        
        return start, end
    
    def _should_generate_report(self, report_def: ReportDefinition) -> bool:
        """Check if report should be generated based on frequency"""
        # In production, this would check last generation time
        # For now, always return True for demonstration
        return True
    
    def _generate_report_data(self, report_def: ReportDefinition, 
                            time_range_start: datetime, time_range_end: datetime) -> Dict[str, Any]:
        """Generate report data based on metrics"""
        from .aggregator import MetricsAggregator, TimeRange
        
        aggregator = MetricsAggregator(self.db)
        time_range = TimeRange(time_range_start, time_range_end)
        
        report_data = {
            'report_info': {
                'report_id': report_def.report_id,
                'report_name': report_def.report_name,
                'time_range': {
                    'start': time_range_start.isoformat(),
                    'end': time_range_end.isoformat()
                },
                'generated_at': datetime.now().isoformat()
            },
            'metrics': {}
        }
        
        # Generate metrics based on report type
        if report_def.report_type == 'executive':
            engagement_metrics = aggregator.get_engagement_metrics(time_range)
            monetization_metrics = aggregator.get_monetization_metrics(time_range)
            
            report_data['metrics']['engagement'] = {
                'mau': engagement_metrics.mau,
                'dau': engagement_metrics.dau,
                'retention_d1': engagement_metrics.retention_d1,
                'retention_d7': engagement_metrics.retention_d7,
                'retention_d30': engagement_metrics.retention_d30,
                'avg_session_duration': engagement_metrics.avg_session_duration
            }
            
            report_data['metrics']['monetization'] = {
                'total_revenue': monetization_metrics.total_revenue,
                'arpu': monetization_metrics.arpu,
                'arppu': monetization_metrics.arppu,
                'free_to_vip_conversion': monetization_metrics.free_to_vip_conversion,
                'ltv': monetization_metrics.ltv
            }
            
        elif report_def.report_type == 'revenue':
            monetization_metrics = aggregator.get_monetization_metrics(time_range)
            
            report_data['metrics']['revenue'] = {
                'total_revenue': monetization_metrics.total_revenue,
                'arpu': monetization_metrics.arpu,
                'arppu': monetization_metrics.arppu,
                'revenue_by_product': monetization_metrics.revenue_by_product
            }
            
        elif report_def.report_type == 'content':
            narrative_metrics = aggregator.get_narrative_metrics(time_range)
            experience_metrics = aggregator.get_experience_metrics(time_range)
            
            report_data['metrics']['narrative'] = {
                'most_visited_fragments': narrative_metrics.most_visited_fragments,
                'completion_rate': narrative_metrics.completion_rate,
                'popular_decisions': narrative_metrics.popular_decisions
            }
            
            report_data['metrics']['experiences'] = {
                'start_rate': experience_metrics.start_rate,
                'completion_rate': experience_metrics.completion_rate,
                'avg_completion_time': experience_metrics.avg_completion_time,
                'popular_experiences': experience_metrics.popular_experiences
            }
            
        elif report_def.report_type == 'experiences':
            experience_metrics = aggregator.get_experience_metrics(time_range)
            
            report_data['metrics']['experiences'] = {
                'start_rate': experience_metrics.start_rate,
                'completion_rate': experience_metrics.completion_rate,
                'avg_completion_time': experience_metrics.avg_completion_time,
                'popular_experiences': experience_metrics.popular_experiences
            }
        
        # Add insights if available
        from .insights import InsightEngine
        insight_engine = InsightEngine(self.db)
        insights = insight_engine.generate_insights(days_back=7)
        
        if insights:
            report_data['insights'] = [
                {
                    'type': insight.insight_type,
                    'severity': insight.severity,
                    'title': insight.title,
                    'description': insight.description,
                    'recommendation': insight.recommendation
                }
                for insight in insights
            ]
        
        return report_data
    
    def _export_to_format(self, report_data: Dict[str, Any], format_type: str, 
                         report_def: ReportDefinition) -> str:
        """Export report data to specified format"""
        if format_type == 'json':
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        
        elif format_type == 'csv':
            return self._export_to_csv(report_data, report_def)
        
        elif format_type == 'excel':
            # In production, this would use a library like openpyxl
            # For now, return CSV as placeholder
            return self._export_to_csv(report_data, report_def)
        
        elif format_type == 'pdf':
            # In production, this would use a library like reportlab
            # For now, return JSON as placeholder
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_to_csv(self, report_data: Dict[str, Any], report_def: ReportDefinition) -> str:
        """Export report data to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Report', report_def.report_name])
        writer.writerow(['Generated At', report_data['report_info']['generated_at']])
        writer.writerow(['Time Range', 
                        f"{report_data['report_info']['time_range']['start']} to {report_data['report_info']['time_range']['end']}"])
        writer.writerow([])
        
        # Write metrics
        for category, metrics in report_data['metrics'].items():
            writer.writerow([category.upper()])
            
            if isinstance(metrics, dict):
                for key, value in metrics.items():
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
        
        # Write insights if available
        if 'insights' in report_data:
            writer.writerow(['INSIGHTS'])
            for insight in report_data['insights']:
                writer.writerow([insight['severity'].upper(), insight['title']])
                writer.writerow(['', insight['description']])
                writer.writerow(['', f"Recommendation: {insight['recommendation']}"])
                writer.writerow([])
        
        return output.getvalue()
    
    def _send_report_to_recipients(self, report: GeneratedReport, recipients: List[str]) -> bool:
        """Send report to recipients via configured channels"""
        logger.info(f"Sending report {report.report_id} to {len(recipients)} recipients")
        
        success = True
        
        for recipient in recipients:
            try:
                # In production, this would integrate with email service
                # For now, just log the action
                logger.info(f"Report {report.report_id} sent to {recipient}")
                
                # Send via email
                if '@' in recipient:
                    self._send_email_report(report, recipient)
                
                # Send via other channels if needed
                
            except Exception as e:
                logger.error(f"Failed to send report to {recipient}: {e}")
                success = False
        
        return success
    
    def _send_email_report(self, report: GeneratedReport, email: str) -> bool:
        """Send report via email"""
        # In production, this would integrate with email service
        logger.info(f"[EMAIL] Report {report.report_name} sent to {email}")
        return True
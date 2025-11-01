#!/usr/bin/env python3
"""
Analyze current production data for Fase 9 improvements
"""

from modules.analytics.aggregator import MetricsAggregator, TimeRange
from database.connection import get_db
import json

def analyze_production_data():
    """Analyze current production metrics to identify improvement areas"""
    
    db = next(get_db())
    aggregator = MetricsAggregator(db)
    
    # Get current metrics for last 30 days
    time_range = TimeRange.last_30_days()
    
    print('=== CURRENT PRODUCTION METRICS (Last 30 Days) ===')
    
    # Engagement metrics
    engagement = aggregator.get_engagement_metrics(time_range)
    print('\n--- ENGAGEMENT METRICS ---')
    print(f'Monthly Active Users (MAU): {engagement.mau}')
    print(f'Daily Active Users (DAU): {engagement.dau}')
    print(f'Day 1 Retention: {engagement.retention_d1:.2%}')
    print(f'Day 7 Retention: {engagement.retention_d7:.2%}')
    print(f'Day 30 Retention: {engagement.retention_d30:.2%}')
    print(f'Avg Session Duration: {engagement.avg_session_duration:.0f} seconds')
    print(f'Engagement by Module: {json.dumps(engagement.engagement_by_module, indent=2)}')
    
    # Monetization metrics
    monetization = aggregator.get_monetization_metrics(time_range)
    print('\n--- MONETIZATION METRICS ---')
    print(f'Total Revenue: ${monetization.total_revenue:.2f}')
    print(f'ARPU: ${monetization.arpu:.2f}')
    print(f'ARPPU: ${monetization.arppu:.2f}')
    print(f'Free to VIP Conversion: {monetization.free_to_vip_conversion:.2%}')
    print(f'LTV: ${monetization.ltv:.2f}')
    print(f'Revenue by Product: {json.dumps(monetization.revenue_by_product, indent=2)}')
    
    # Narrative metrics
    narrative = aggregator.get_narrative_metrics(time_range)
    print('\n--- NARRATIVE METRICS ---')
    print(f'Completion Rate: {narrative.completion_rate:.2%}')
    print(f'Most Visited Fragments: {json.dumps(narrative.most_visited_fragments, indent=2)}')
    print(f'Popular Decisions: {json.dumps(narrative.popular_decisions, indent=2)}')
    print(f'Drop-off Points: {json.dumps(narrative.drop_off_points, indent=2)}')
    
    # Experience metrics
    experience = aggregator.get_experience_metrics(time_range)
    print('\n--- EXPERIENCE METRICS ---')
    print(f'Start Rate: {experience.start_rate:.2%}')
    print(f'Completion Rate: {experience.completion_rate:.2%}')
    print(f'Avg Completion Time: {experience.avg_completion_time:.0f} seconds')
    print(f'Popular Experiences: {json.dumps(experience.popular_experiences, indent=2)}')
    
    # Identify improvement areas
    print('\n=== IMPROVEMENT AREAS IDENTIFIED ===')
    
    # Low engagement areas
    if engagement.mau < 10:
        print(f'❌ LOW USER BASE: Only {engagement.mau} monthly active users')
    
    if engagement.retention_d1 < 0.3:
        print(f'❌ LOW RETENTION: Day 1 retention is only {engagement.retention_d1:.2%}')
    
    # Monetization issues
    if monetization.total_revenue < 10:
        print(f'❌ LOW REVENUE: Total revenue is only ${monetization.total_revenue:.2f}')
    
    if monetization.free_to_vip_conversion < 0.05:
        print(f'❌ LOW CONVERSION: Free to VIP conversion is only {monetization.free_to_vip_conversion:.2%}')
    
    # Narrative issues
    if narrative.completion_rate < 0.5:
        print(f'❌ LOW NARRATIVE COMPLETION: Only {narrative.completion_rate:.2%} of users complete narratives')
    
    # Experience issues
    if experience.start_rate < 0.5:
        print(f'❌ LOW EXPERIENCE START RATE: Only {experience.start_rate:.2%} of users start experiences')
    
    if experience.completion_rate < 0.3:
        print(f'❌ LOW EXPERIENCE COMPLETION: Only {experience.completion_rate:.2%} of started experiences are completed')

if __name__ == '__main__':
    analyze_production_data()
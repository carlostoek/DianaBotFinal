#!/usr/bin/env python3
"""
Analyze current system state and identify improvement areas for Fase 9
"""

from database.connection import get_db
from database.models import User, UserBalance, Transaction, UserNarrativeProgress
import json

def analyze_improvement_areas():
    """Analyze current system state to identify areas for improvement"""
    
    db = next(get_db())
    
    print('=== CURRENT SYSTEM ANALYSIS FOR FASE 9 IMPROVEMENTS ===')
    
    # User analysis
    users = db.query(User).all()
    print(f'\n--- USER ANALYSIS ---')
    print(f'Total Users: {len(users)}')
    
    # User engagement analysis
    active_users = []
    for user in users:
        # Check if user has any activity
        balance = db.query(UserBalance).filter(UserBalance.user_id == user.id).first()
        narrative_progress = db.query(UserNarrativeProgress).filter(UserNarrativeProgress.user_id == user.id).first()
        
        user_activity = {
            'user_id': user.id,
            'username': user.username,
            'besitos': balance.besitos if balance else 0,
            'has_narrative_progress': narrative_progress is not None,
            'activity_level': 0
        }
        
        # Calculate activity level
        if balance and balance.besitos > 0:
            user_activity['activity_level'] += 1
        if narrative_progress:
            user_activity['activity_level'] += 1
            
        if user_activity['activity_level'] > 0:
            active_users.append(user_activity)
    
    print(f'Active Users (some activity): {len(active_users)}')
    for user in active_users:
        print(f'  User {user["user_id"]} ({user["username"]}): {user["besitos"]} besitos, ' +
              f'Narrative: {user["has_narrative_progress"]}')
    
    # Economic analysis
    print(f'\n--- ECONOMIC ANALYSIS ---')
    if active_users:
        total_besitos = sum(user['besitos'] for user in active_users)
        avg_besitos = total_besitos / len(active_users)
        max_besitos = max(user['besitos'] for user in active_users)
        min_besitos = min(user['besitos'] for user in active_users)
        
        print(f'Total Besitos in System: {total_besitos}')
        print(f'Average Besitos per Active User: {avg_besitos:.1f}')
        print(f'Wealth Distribution: Max {max_besitos}, Min {min_besitos}')
    else:
        total_besitos = 0
        avg_besitos = 0
        max_besitos = 0
        min_besitos = 0
        print('No active users for economic analysis')
    
    # Narrative analysis
    print(f'\n--- NARRATIVE ANALYSIS ---')
    narrative_progress = db.query(UserNarrativeProgress).all()
    print(f'Users with Narrative Progress: {len(narrative_progress)}')
    
    # Check narrative completion
    completed_narratives = []
    for progress in narrative_progress:
        if progress.completed_at:
            completed_narratives.append(progress)
    
    print(f'Completed Narratives: {len(completed_narratives)}')
    
    # Transaction analysis
    print(f'\n--- TRANSACTION ANALYSIS ---')
    transactions = db.query(Transaction).all()
    print(f'Total Transactions: {len(transactions)}')
    
    # Revenue analysis
    revenue_transactions = []
    for t in transactions:
        if hasattr(t, 'status') and t.status == 'completed':
            revenue_transactions.append(t)
    
    total_revenue = sum(t.amount for t in revenue_transactions)
    print(f'Total Revenue: ${total_revenue:.2f}')
    
    # Identify specific improvement areas
    print(f'\n=== IMPROVEMENT AREAS FOR FASE 9 ===')
    
    improvement_areas = []
    
    # 1. User Engagement
    if len(active_users) < 3:
        improvement_areas.append({
            'area': 'User Engagement',
            'priority': 'HIGH',
            'description': f'Only {len(active_users)} active users out of {len(users)} total users',
            'suggestions': [
                'Improve onboarding experience',
                'Add daily login rewards',
                'Implement push notifications for inactive users'
            ]
        })
    
    # 2. Narrative Completion
    if narrative_progress and len(completed_narratives) / len(narrative_progress) < 0.5:
        improvement_areas.append({
            'area': 'Narrative Completion',
            'priority': 'HIGH',
            'description': f'Only {len(completed_narratives)}/{len(narrative_progress)} users complete narratives',
            'suggestions': [
                'Simplify narrative flow',
                'Add progress indicators',
                'Implement narrative checkpoints with rewards'
            ]
        })
    
    # 3. Monetization
    if total_revenue < 20:
        improvement_areas.append({
            'area': 'Monetization',
            'priority': 'HIGH',
            'description': f'Total revenue is only ${total_revenue:.2f}',
            'suggestions': [
                'Improve VIP subscription value proposition',
                'Add limited-time offers',
                'Implement tiered pricing'
            ]
        })
    
    # 4. Economic Balance
    if active_users and max_besitos > avg_besitos * 3:
        improvement_areas.append({
            'area': 'Economic Balance',
            'priority': 'MEDIUM',
            'description': f'Wealth concentration: max {max_besitos} vs avg {avg_besitos:.1f}',
            'suggestions': [
                'Add wealth redistribution mechanics',
                'Implement progressive rewards',
                'Create economic sinks (spending opportunities)'
            ]
        })
    
    # Print improvement areas
    for area in improvement_areas:
        print(f'\n{area["priority"]} PRIORITY: {area["area"]}')
        print(f'  Issue: {area["description"]}')
        print(f'  Suggestions:')
        for suggestion in area['suggestions']:
            print(f'    • {suggestion}')
    
    if not improvement_areas:
        print('✅ System is performing well! No major improvement areas identified.')
    
    return improvement_areas

if __name__ == '__main__':
    improvement_areas = analyze_improvement_areas()
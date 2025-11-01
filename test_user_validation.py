#!/usr/bin/env python3
"""
Tests for user validation utilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models import User, Subscription
from bot.utils.user_validation import (
    validate_user_exists,
    validate_user_not_banned,
    validate_user_can_subscribe,
    validate_user_can_access_vip_content,
    get_user_state,
    UserValidationError
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


class TestUserValidation:
    """Test user validation utilities"""
    
    def test_validate_user_exists_success(self, test_db):
        """Test successful user existence validation"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Validate user exists
        result = validate_user_exists(test_db, user.id)
        assert result.id == user.id
        assert result.telegram_id == user.telegram_id
    
    def test_validate_user_exists_failure(self, test_db):
        """Test user existence validation failure"""
        with pytest.raises(UserValidationError) as exc_info:
            validate_user_exists(test_db, 999999)
        
        assert "User with ID 999999 not found" in str(exc_info.value)
    
    def test_validate_user_not_banned_success(self, test_db):
        """Test successful user not banned validation"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Validate user not banned
        result = validate_user_not_banned(test_db, user.id)
        assert result.id == user.id
    
    def test_validate_user_not_banned_failure(self, test_db):
        """Test user not banned validation failure"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Mark user as banned (using user_state field)
        user.user_state = "banned"
        test_db.commit()
        
        with pytest.raises(UserValidationError) as exc_info:
            validate_user_not_banned(test_db, user.id)
        
        assert f"User {user.id} is banned" in str(exc_info.value)
    
    def test_validate_user_can_subscribe_success(self, test_db):
        """Test successful user can subscribe validation"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Validate user can subscribe
        result = validate_user_can_subscribe(test_db, user.id)
        assert result.id == user.id
    
    def test_validate_user_can_subscribe_failure_already_vip(self, test_db):
        """Test user can subscribe validation failure - already VIP"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create active subscription
        subscription = Subscription(
            user_id=user.id,
            subscription_type="monthly",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            status="active"
        )
        test_db.add(subscription)
        test_db.commit()
        
        with pytest.raises(UserValidationError) as exc_info:
            validate_user_can_subscribe(test_db, user.id)
        
        assert f"User {user.id} already has active subscription" in str(exc_info.value)
    
    def test_validate_user_can_subscribe_failure_banned(self, test_db):
        """Test user can subscribe validation failure - banned user"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Mark user as banned
        user.user_state = "banned"
        test_db.commit()
        
        with pytest.raises(UserValidationError) as exc_info:
            validate_user_can_subscribe(test_db, user.id)
        
        assert f"User {user.id} is banned" in str(exc_info.value)
    
    def test_validate_user_can_access_vip_content_success(self, test_db):
        """Test successful VIP content access validation"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create active subscription
        subscription = Subscription(
            user_id=user.id,
            subscription_type="monthly",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            status="active"
        )
        test_db.add(subscription)
        test_db.commit()
        
        # Validate VIP content access
        result = validate_user_can_access_vip_content(test_db, user.id)
        assert result is True
    
    def test_validate_user_can_access_vip_content_failure_no_subscription(self, test_db):
        """Test VIP content access validation failure - no subscription"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Validate VIP content access
        result = validate_user_can_access_vip_content(test_db, user.id)
        assert result is False
    
    def test_validate_user_can_access_vip_content_failure_expired_subscription(self, test_db):
        """Test VIP content access validation failure - expired subscription"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create expired subscription
        subscription = Subscription(
            user_id=user.id,
            subscription_type="monthly",
            start_date=datetime.now() - timedelta(days=60),
            end_date=datetime.now() - timedelta(days=30),
            status="active"
        )
        test_db.add(subscription)
        test_db.commit()
        
        # Validate VIP content access
        result = validate_user_can_access_vip_content(test_db, user.id)
        assert result is False
    
    def test_validate_user_can_access_vip_content_failure_banned_user(self, test_db):
        """Test VIP content access validation failure - banned user"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Mark user as banned
        user.user_state = "banned"
        test_db.commit()
        
        # Validate VIP content access
        result = validate_user_can_access_vip_content(test_db, user.id)
        assert result is False
    
    def test_get_user_state_exists_vip(self, test_db):
        """Test get user state for existing VIP user"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create active subscription
        subscription = Subscription(
            user_id=user.id,
            subscription_type="monthly",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            status="active"
        )
        test_db.add(subscription)
        test_db.commit()
        
        # Get user state
        state = get_user_state(test_db, user.id)
        
        assert state["user_id"] == user.id
        assert state["exists"] is True
        assert state["is_banned"] is False
        assert state["is_vip"] is True
        assert state["subscription_type"] == "monthly"
        assert state["days_remaining"] > 0
        assert state["can_subscribe"] is False
        assert state["can_access_vip"] is True
    
    def test_get_user_state_exists_free(self, test_db):
        """Test get user state for existing free user"""
        # Create test user
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            current_state="start"
        )
        test_db.add(user)
        test_db.commit()
        
        # Get user state
        state = get_user_state(test_db, user.id)
        
        assert state["user_id"] == user.id
        assert state["exists"] is True
        assert state["is_banned"] is False
        assert state["is_vip"] is False
        assert state["subscription_type"] is None
        assert state["days_remaining"] == 0
        assert state["can_subscribe"] is True
        assert state["can_access_vip"] is False
    
    def test_get_user_state_not_exists(self, test_db):
        """Test get user state for non-existent user"""
        # Get user state for non-existent user
        state = get_user_state(test_db, 999999)
        
        assert state["user_id"] == 999999
        assert state["exists"] is False
        assert state["is_banned"] is False
        assert state["is_vip"] is False
        assert state["subscription_type"] is None
        assert state["days_remaining"] == 0
        assert state["can_subscribe"] is False
        assert state["can_access_vip"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
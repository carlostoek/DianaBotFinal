"""
Auction service for real-time item auctions with dynamic timer and anti-sniping
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import redis

from database.models import Auction, Bid, User, Item, UserBalance, UserInventory
from database.connection import get_db
from utils.locks import with_auction_lock, get_lock_manager
from core.event_bus import EventBus
from config.settings import settings


class AuctionService:
    """Service for managing auctions and bids"""
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis_client = redis_client
        self.lock_manager = get_lock_manager()
        self.event_bus = EventBus()
    
    def create_auction(
        self, 
        item_id: int, 
        start_price: int, 
        duration_minutes: int = 60,
        auction_type: str = "standard",
        min_bid_increment: int = 10,
        auction_metadata: Optional[Dict[str, Any]] = None
    ) -> Auction:
        """
        Create a new auction
        
        Args:
            item_id: ID of the item to auction
            start_price: Starting price in besitos
            duration_minutes: Auction duration in minutes
            auction_type: Type of auction ('standard', 'dutch', 'silent')
            min_bid_increment: Minimum bid increment
            auction_metadata: Additional auction settings
            
        Returns:
            Created auction object
        """
        # Verify item exists
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise ValueError(f"Item with ID {item_id} not found")
        
        # Calculate end time
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create auction
        auction = Auction(
            item_id=item_id,
            auction_type=auction_type,
            start_price=start_price,
            current_bid=start_price,
            current_bidder_id=None,
            winner_id=None,
            status="active",
            start_time=start_time,
            end_time=end_time,
            min_bid_increment=min_bid_increment,
            auction_metadata=auction_metadata or {}
        )
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        # Publish auction started event
        self.event_bus.publish("gamification.auction_started", {
            "auction_id": auction.auction_id,
            "item_id": item_id,
            "start_price": start_price,
            "end_time": end_time.isoformat()
        })
        
        return auction
    
    @with_auction_lock(operation="bid")
    def place_bid(self, user_id: int, auction_id: int, amount: int) -> Bid:
        """
        Place a bid on an auction
        
        Args:
            user_id: ID of the user placing the bid
            auction_id: ID of the auction
            amount: Bid amount in besitos
            
        Returns:
            Created bid object
        """
        # Get auction
        auction = self.db.query(Auction).filter(
            Auction.auction_id == auction_id,
            Auction.status == "active"
        ).first()
        
        if auction is None:
            raise ValueError(f"Active auction with ID {auction_id} not found")
        
        # Check if auction has ended
        if datetime.now(timezone.utc).timestamp() > auction.end_time.timestamp():
            raise ValueError("Auction has already ended")
        
        # Check minimum bid
        min_bid = auction.current_bid + auction.min_bid_increment
        if amount < min_bid:
            raise ValueError(f"Minimum bid is {min_bid} besitos")
        
        # Check user balance
        user_balance = self.db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        if user_balance is None or user_balance.besitos < amount:
            raise ValueError("Insufficient besitos")
        
        # Check rate limiting (max 1 bid every 5 seconds)
        last_bid = self.db.query(Bid).filter(
            Bid.user_id == user_id,
            Bid.auction_id == auction_id
        ).order_by(Bid.created_at.desc()).first()
        
        if last_bid is not None and (datetime.now(timezone.utc).timestamp() - last_bid.created_at.timestamp()) < 5:
            raise ValueError("Please wait 5 seconds between bids")
        
        # Create bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            amount=amount,
            is_winning=True
        )
        
        # Update auction
        auction.current_bid = amount
        auction.current_bidder_id = user_id
        auction.bid_count = auction.bid_count + 1
        
        # Apply dynamic timer extension
        time_remaining = (auction.end_time - datetime.now(timezone.utc)).total_seconds()
        if time_remaining <= 60:  # If less than 60 seconds remaining
            auction.extended_end_time = datetime.now(timezone.utc) + timedelta(seconds=60)
        
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        
        # Publish bid placed event
        self.event_bus.publish("gamification.bid_placed", {
            "auction_id": auction_id,
            "user_id": user_id,
            "amount": amount,
            "current_bid": auction.current_bid
        })
        
        # Notify previous bidder if they were outbid
        if auction.bid_count > 1:
            self._notify_outbid_users(auction_id, user_id)
        
        return bid
    
    def get_active_auctions(self) -> List[Auction]:
        """Get all active auctions"""
        return self.db.query(Auction).filter(
            Auction.status == "active",
            Auction.end_time > datetime.now(timezone.utc)
        ).all()
    
    def get_auction_status(self, auction_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed auction status"""
        auction = self.db.query(Auction).filter(Auction.auction_id == auction_id).first()
        if auction is None:
            return None
        
        # Get top bids
        top_bids = self.db.query(Bid).filter(
            Bid.auction_id == auction_id
        ).order_by(Bid.amount.desc()).limit(5).all()
        
        return {
            "auction": auction.to_dict(),
            "item": auction.item.to_dict() if auction.item else None,
            "current_bidder": auction.current_bidder.to_dict() if auction.current_bidder else None,
            "top_bids": [bid.to_dict() for bid in top_bids],
            "time_remaining": max(0, (auction.end_time - datetime.now(timezone.utc)).total_seconds())
        }
    
    @with_auction_lock(operation="close")
    def close_auction(self, auction_id: int) -> Optional[Dict[str, Any]]:
        """
        Close an auction and determine the winner
        
        Returns:
            Dictionary with auction result
        """
        auction = self.db.query(Auction).filter(Auction.auction_id == auction_id).first()
        if auction is None or auction.status != "active":
            return None
        
        # Check if auction should be closed
        end_time = auction.extended_end_time or auction.end_time
        if datetime.now(timezone.utc) < end_time:
            return None
        
        # Determine winner
        if auction.current_bidder_id is not None:
            auction.winner_id = auction.current_bidder_id
            auction.status = "closed"
            
            # Transfer item to winner
            inventory_item = UserInventory(
                user_id=auction.winner_id,
                item_id=auction.item_id,
                quantity=1,
                acquired_at=datetime.now(timezone.utc)
            )
            self.db.add(inventory_item)
            
            # Deduct besitos from winner using atomic operation
            user_balance = self.db.query(UserBalance).filter(
                UserBalance.user_id == auction.winner_id
            ).with_for_update().first()
            
            if user_balance is not None:
                user_balance.besitos -= auction.current_bid
            
            # Publish auction won event
            self.event_bus.publish("gamification.auction_won", {
                "auction_id": auction_id,
                "user_id": auction.winner_id,
                "item_id": auction.item_id,
                "winning_bid": auction.current_bid
            })
            
            result = {
                "winner_id": auction.winner_id,
                "winning_bid": auction.current_bid,
                "item_id": auction.item_id,
                "status": "won"
            }
        else:
            # No bids, auction closed without winner
            auction.status = "closed"
            result = {
                "winner_id": None,
                "winning_bid": None,
                "item_id": auction.item_id,
                "status": "no_bids"
            }
        
        self.db.commit()
        
        return result
    
    def get_user_bid_history(self, user_id: int, limit: int = 10) -> List[Bid]:
        """Get user's bid history"""
        return self.db.query(Bid).filter(
            Bid.user_id == user_id
        ).order_by(Bid.created_at.desc()).limit(limit).all()
    
    def _notify_outbid_users(self, auction_id: int, new_bidder_id: int):
        """Notify users who were outbid"""
        # Get all unique bidders except the new bidder
        bidders = self.db.query(Bid.user_id).filter(
            Bid.auction_id == auction_id,
            Bid.user_id != new_bidder_id
        ).distinct().all()
        
        # Store notification in Redis for bot to process
        for bidder in bidders:
            notification_key = f"auction_notification:{bidder[0]}"
            self.redis_client.lpush(notification_key, auction_id)
            self.redis_client.expire(notification_key, 3600)  # Keep for 1 hour


def get_auction_service() -> AuctionService:
    """Get auction service instance"""
    db = next(get_db())
    redis_client = redis.from_url(settings.redis_url)
    return AuctionService(db, redis_client)
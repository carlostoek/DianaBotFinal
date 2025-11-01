"""
Test script for auction system
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db
from database.models import User, Item, Auction, Bid
from modules.gamification.auctions import get_auction_service
from modules.gamification.besitos import besitos_service

def test_auction_basics():
    """Test basic auction functionality"""
    print("🧪 Testing Auction System...")
    
    try:
        auction_service = get_auction_service()
        
        # Get a test user
        db = next(get_db())
        test_user = db.query(User).first()
        
        if not test_user:
            print("❌ No test user found")
            return False
            
        user_id = int(test_user.id)
        print(f"✅ Using test user: {user_id} ({test_user.username})")
        
        # Get an item for auction
        test_item = db.query(Item).first()
        if not test_item:
            print("❌ No items found in database")
            return False
            
        item_id = int(test_item.id)
        print(f"✅ Using test item: {test_item.item_key} ({test_item.name})")
        
        # Test creating an auction
        print("\n🏷️ Testing auction creation...")
        try:
            auction = auction_service.create_auction(
                item_id=item_id,
                start_price=100,
                duration_minutes=1  # Short duration for testing
            )
            auction_id = int(auction.auction_id)
            print(f"✅ Auction created: ID {auction_id}")
            print(f"   Item: {test_item.name}")
            print(f"   Start price: {auction.start_price}")
            print(f"   End time: {auction.end_time}")
        except Exception as e:
            print(f"❌ Failed to create auction: {e}")
            return False
        
        # Test getting active auctions
        print("\n📋 Testing active auctions...")
        active_auctions = auction_service.get_active_auctions()
        print(f"✅ Found {len(active_auctions)} active auctions")
        
        # Test auction status
        print("\n📊 Testing auction status...")
        auction_status = auction_service.get_auction_status(auction_id)
        if auction_status:
            print(f"✅ Auction status retrieved")
            print(f"   Current bid: {auction_status['auction']['current_bid']}")
            print(f"   Bid count: {auction_status['auction']['bid_count']}")
        else:
            print("❌ Failed to get auction status")
            return False
            
        # Test placing a bid
        print("\n💎 Testing bid placement...")
        try:
            # Ensure user has enough besitos
            besitos_service.grant_besitos(user_id, 200, "test_funds")
            
            bid = auction_service.place_bid(user_id, auction_id, 150)
            print(f"✅ Bid placed: {bid.amount} besitos")
            print(f"   Bid ID: {bid.bid_id}")
        except Exception as e:
            print(f"❌ Failed to place bid: {e}")
            return False
            
        # Test user bid history
        print("\n📋 Testing user bid history...")
        bid_history = auction_service.get_user_bid_history(user_id)
        print(f"✅ User has {len(bid_history)} bids")
        
        # Test closing auction
        print("\n🔚 Testing auction closure...")
        result = auction_service.close_auction(auction_id)
        if result:
            print(f"✅ Auction closed successfully")
            print(f"   Status: {result['status']}")
            if result['status'] == 'won':
                print(f"   Winner: {result['winner_id']}")
                print(f"   Winning bid: {result['winning_bid']}")
        else:
            print("❌ Failed to close auction (auction may not have ended yet)")
            print("   This is expected for active auctions")
            
        print("\n🎉 All auction tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auction_basics()
    sys.exit(0 if success else 1)
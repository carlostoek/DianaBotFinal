"""
Load Testing Script for DianaBot
Simple load testing without external dependencies
"""
import time
import random
import threading
import requests
from datetime import datetime


class LoadTester:
    """Simple load testing utility for DianaBot"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0,
            "start_time": None,
            "end_time": None
        }
    
    def test_api_endpoint(self, endpoint, method="GET", payload=None, headers=None):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            else:
                return False, 0
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            success = response.status_code < 400
            
            self.stats["total_requests"] += 1
            if success:
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            self.stats["total_response_time"] += response_time
            
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "response_time": response_time,
                "status_code": response.status_code,
                "success": success,
                "timestamp": datetime.now()
            })
            
            return success, response_time
            
        except requests.exceptions.RequestException as e:
            self.stats["total_requests"] += 1
            self.stats["failed_requests"] += 1
            return False, 0
    
    def test_analytics_endpoints(self, user_id=None):
        """Test analytics API endpoints"""
        if user_id is None:
            user_id = random.randint(1000, 9999)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer test_user_{user_id}"
        }
        
        endpoints = [
            "/api/analytics/overview",
            "/api/analytics/funnels",
            "/api/analytics/cohorts",
            "/api/dashboard/data",
            "/api/dashboard/user-segments"
        ]
        
        for endpoint in endpoints:
            success, response_time = self.test_api_endpoint(endpoint, headers=headers)
            if success:
                print(f"✓ {endpoint}: {response_time:.2f}ms")
            else:
                print(f"✗ {endpoint}: FAILED")
    
    def test_bot_webhook(self, telegram_id=None):
        """Test bot webhook endpoint"""
        if telegram_id is None:
            telegram_id = random.randint(100000000, 999999999)
        
        commands = ["/start", "/balance", "/shop", "/daily"]
        command = random.choice(commands)
        
        payload = {
            "update_id": random.randint(1, 1000),
            "message": {
                "message_id": random.randint(1, 1000),
                "from": {
                    "id": telegram_id,
                    "is_bot": False,
                    "first_name": f"TestUser{telegram_id}"
                },
                "chat": {
                    "id": telegram_id,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": command
            }
        }
        
        headers = {"Content-Type": "application/json"}
        success, response_time = self.test_api_endpoint(
            "/webhook", method="POST", payload=payload, headers=headers
        )
        
        if success:
            print(f"✓ Webhook {command}: {response_time:.2f}ms")
        else:
            print(f"✗ Webhook {command}: FAILED")
    
    def run_concurrent_test(self, num_users=10, duration=30):
        """Run concurrent load test"""
        print(f"Starting concurrent load test: {num_users} users for {duration} seconds")
        self.stats["start_time"] = datetime.now()
        
        def user_worker(user_id):
            end_time = time.time() + duration
            while time.time() < end_time:
                # Mix of API calls and bot commands
                if random.random() < 0.7:  # 70% API calls
                    self.test_analytics_endpoints(user_id)
                else:  # 30% bot commands
                    self.test_bot_webhook(user_id)
                
                # Random delay between requests
                time.sleep(random.uniform(0.5, 2))
        
        # Start concurrent users
        threads = []
        for i in range(num_users):
            thread = threading.Thread(target=user_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self.stats["end_time"] = datetime.now()
        self.print_stats()
    
    def print_stats(self):
        """Print load testing statistics"""
        print("\n" + "="*50)
        print("LOAD TESTING RESULTS")
        print("="*50)
        
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            print(f"Test Duration: {duration:.2f} seconds")
        
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful_requests']}")
        print(f"Failed: {self.stats['failed_requests']}")
        
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            avg_response_time = self.stats['total_response_time'] / len(self.results) if self.results else 0
            
            print(f"Success Rate: {success_rate:.2f}%")
            print(f"Average Response Time: {avg_response_time:.2f}ms")
            
            # Calculate percentiles
            response_times = [r["response_time"] for r in self.results if r["success"]]
            if response_times:
                response_times.sort()
                p50 = response_times[int(len(response_times) * 0.5)]
                p95 = response_times[int(len(response_times) * 0.95)]
                p99 = response_times[int(len(response_times) * 0.99)]
                
                print(f"P50 Response Time: {p50:.2f}ms")
                print(f"P95 Response Time: {p95:.2f}ms")
                print(f"P99 Response Time: {p99:.2f}ms")
        
        print("="*50)


def main():
    """Main function to run load tests"""
    tester = LoadTester()
    
    print("DianaBot Load Testing")
    print("1. Quick API Test")
    print("2. Concurrent Load Test")
    print("3. Stress Test")
    
    choice = input("Choose test type (1-3): ").strip()
    
    if choice == "1":
        print("\nRunning quick API test...")
        tester.test_analytics_endpoints()
        tester.print_stats()
    
    elif choice == "2":
        users = int(input("Number of concurrent users (default 10): ") or "10")
        duration = int(input("Test duration in seconds (default 30): ") or "30")
        tester.run_concurrent_test(users, duration)
    
    elif choice == "3":
        print("\nRunning stress test (50 users for 60 seconds)...")
        tester.run_concurrent_test(50, 60)
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
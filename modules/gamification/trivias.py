"""
Trivia service for DianaBot
Handles trivia questions, answers, and rewards
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

from database.mongo_schemas import TriviaQuestion
from database.connection import mongo_db
from core.event_bus import EventBus
from modules.gamification.besitos import BesitosService
from modules.gamification.inventory import InventoryService


class TriviaService:
    """Service for managing trivia questions and answers"""
    
    def __init__(self):
        self.db = mongo_db
        self.trivia_collection = self.db.trivia_questions
        self.trivia_stats_collection = self.db.trivia_stats
        
        self.besitos_service = BesitosService()
        self.inventory_service = InventoryService()
        self.event_bus = EventBus()
    
    def get_random_trivia(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> Optional[Dict]:
        """Get a random trivia question based on filters"""
        query = {}
        
        if category:
            query["category"] = category
        
        if difficulty:
            query["difficulty"] = difficulty
        
        # Get count for random sampling
        count = self.trivia_collection.count_documents(query)
        if count == 0:
            return None
        
        # Get random document
        random_index = random.randint(0, count - 1)
        trivia_doc = self.trivia_collection.find(query).skip(random_index).limit(1).next()
        
        return self._format_trivia_for_display(trivia_doc)
    
    def get_trivia_by_id(self, trivia_id: str) -> Optional[Dict]:
        """Get trivia question by ID"""
        try:
            trivia_doc = self.trivia_collection.find_one({"_id": ObjectId(trivia_id)})
            return self._format_trivia_for_display(trivia_doc) if trivia_doc else None
        except:
            return None
    
    def submit_answer(
        self, 
        user_id: int, 
        trivia_id: str, 
        answer: str, 
        response_time: float
    ) -> Dict[str, Any]:
        """Submit answer to trivia question and process rewards"""
        
        # Get trivia question
        trivia = self.get_trivia_by_id(trivia_id)
        if not trivia:
            return {"success": False, "error": "Trivia not found"}
        
        # Find correct answer
        correct_option = None
        for option in trivia["options"]:
            if option["is_correct"]:
                correct_option = option["option_id"]
                break
        
        if not correct_option:
            return {"success": False, "error": "No correct option found"}
        
        # Check if answer is correct
        is_correct = (answer == correct_option)
        
        # Calculate rewards based on correctness and response time
        rewards = self._calculate_rewards(trivia, is_correct, response_time)
        
        # Apply rewards
        if rewards.get("besitos", 0) > 0:
            self.besitos_service.grant_besitos(user_id, rewards["besitos"], "trivia_answer")
        
        if rewards.get("items"):
            for item in rewards["items"]:
                self.inventory_service.add_item_to_inventory(user_id, item["item_key"], item.get("quantity", 1), "trivia_reward")
        
        # Update statistics
        self._update_trivia_stats(user_id, trivia, is_correct, response_time)
        
        # Publish event
        self.event_bus.publish(
            "gamification.trivia_answered",
            {
                "user_id": user_id,
                "trivia_id": trivia_id,
                "trivia_key": trivia["question_key"],
                "category": trivia["category"],
                "difficulty": trivia["difficulty"],
                "correct": is_correct,
                "response_time": response_time,
                "rewards": rewards
            }
        )
        
        return {
            "success": True,
            "correct": is_correct,
            "correct_answer": correct_option,
            "rewards": rewards,
            "response_time": response_time
        }
    
    def get_trivia_stats(self, user_id: int) -> Dict[str, Any]:
        """Get trivia statistics for a user"""
        stats = self.trivia_stats_collection.find_one({"user_id": user_id})
        
        if not stats:
            return {
                "total_answered": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "accuracy": 0.0,
                "average_response_time": 0.0,
                "total_besitos_earned": 0,
                "category_stats": {},
                "difficulty_stats": {}
            }
        
        total_answered = stats.get("total_answered", 0)
        correct_answers = stats.get("correct_answers", 0)
        
        return {
            "total_answered": total_answered,
            "correct_answers": correct_answers,
            "incorrect_answers": total_answered - correct_answers,
            "accuracy": (correct_answers / total_answered * 100) if total_answered > 0 else 0.0,
            "average_response_time": stats.get("average_response_time", 0.0),
            "total_besitos_earned": stats.get("total_besitos_earned", 0),
            "category_stats": stats.get("category_stats", {}),
            "difficulty_stats": stats.get("difficulty_stats", {})
        }
    
    def get_categories(self) -> List[str]:
        """Get available trivia categories"""
        return self.trivia_collection.distinct("category")
    
    def get_difficulties(self) -> List[str]:
        """Get available difficulty levels"""
        return self.trivia_collection.distinct("difficulty")
    
    def _format_trivia_for_display(self, trivia_doc: Dict) -> Dict:
        """Format trivia document for display"""
        return {
            "_id": str(trivia_doc["_id"]),
            "question_key": trivia_doc["question_key"],
            "category": trivia_doc["category"],
            "difficulty": trivia_doc["difficulty"],
            "question": trivia_doc["question"],
            "options": trivia_doc["options"],
            "time_limit_seconds": trivia_doc.get("time_limit_seconds", 30),
            "rewards": trivia_doc.get("rewards", {})
        }
    
    def _calculate_rewards(self, trivia: Dict, is_correct: bool, response_time: float) -> Dict[str, Any]:
        """Calculate rewards based on correctness and response time"""
        base_rewards = trivia["rewards"].get("correct" if is_correct else "incorrect", {})
        
        rewards = {
            "besitos": base_rewards.get("besitos", 0),
            "items": base_rewards.get("items", [])
        }
        
        # Speed bonus for correct answers
        if is_correct and response_time < 10:  # Responded in less than 10 seconds
            speed_multiplier = max(1.0, (10 - response_time) / 10 * 2)  # Up to 2x multiplier
            rewards["besitos"] = int(rewards["besitos"] * speed_multiplier)
            rewards["speed_bonus"] = True
        
        return rewards
    
    def _update_trivia_stats(self, user_id: int, trivia: Dict, is_correct: bool, response_time: float):
        """Update user trivia statistics"""
        
        stats = self.trivia_stats_collection.find_one({"user_id": user_id})
        
        if not stats:
            stats = {
                "user_id": user_id,
                "total_answered": 0,
                "correct_answers": 0,
                "total_response_time": 0.0,
                "total_besitos_earned": 0,
                "category_stats": {},
                "difficulty_stats": {}
            }
        
        # Update basic stats
        stats["total_answered"] += 1
        stats["total_response_time"] += response_time
        
        if is_correct:
            stats["correct_answers"] += 1
        
        # Update category stats
        category = trivia["category"]
        if category not in stats["category_stats"]:
            stats["category_stats"][category] = {"answered": 0, "correct": 0}
        
        stats["category_stats"][category]["answered"] += 1
        if is_correct:
            stats["category_stats"][category]["correct"] += 1
        
        # Update difficulty stats
        difficulty = trivia["difficulty"]
        if difficulty not in stats["difficulty_stats"]:
            stats["difficulty_stats"][difficulty] = {"answered": 0, "correct": 0}
        
        stats["difficulty_stats"][difficulty]["answered"] += 1
        if is_correct:
            stats["difficulty_stats"][difficulty]["correct"] += 1
        
        # Calculate averages
        stats["average_response_time"] = stats["total_response_time"] / stats["total_answered"]
        
        # Update or insert stats
        self.trivia_stats_collection.update_one(
            {"user_id": user_id},
            {"$set": stats},
            upsert=True
        )


trivia_service = TriviaService()
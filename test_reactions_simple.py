"""
Tests simplificados para el sistema de reacciones
"""

import unittest
from unittest.mock import Mock, patch


class TestReactionSystemSimple(unittest.TestCase):
    """Test cases for the reaction system (simplified)"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import here to avoid circular imports
        from modules.gamification.reactions import ReactionProcessor
        self.reaction_processor = ReactionProcessor()
    
    def test_reaction_processor_initialization(self):
        """Test that reaction processor initializes correctly"""
        self.assertIsNotNone(self.reaction_processor)
        self.assertIsInstance(self.reaction_processor, type(self.reaction_processor))
        
        # Check default rewards configuration
        self.assertIn('❤️', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('🔥', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('⭐', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('👍', self.reaction_processor.DEFAULT_REACTION_REWARDS)
    
    def test_get_reaction_reward(self):
        """Test reaction reward calculation"""
        # Test valid reactions
        self.assertEqual(self.reaction_processor._get_reaction_reward('❤️'), 10)
        self.assertEqual(self.reaction_processor._get_reaction_reward('🔥'), 15)
        self.assertEqual(self.reaction_processor._get_reaction_reward('⭐'), 20)
        self.assertEqual(self.reaction_processor._get_reaction_reward('👍'), 5)
        
        # Test invalid reaction
        self.assertEqual(self.reaction_processor._get_reaction_reward('invalid'), 0)
    
    def test_get_reaction_stats(self):
        """Test reaction statistics retrieval"""
        stats = self.reaction_processor.get_reaction_stats("narrative_fragment", 123)
        
        # Should return a dictionary with reaction counts
        self.assertIsInstance(stats, dict)
        self.assertIn('❤️', stats)
        self.assertIn('🔥', stats)
        self.assertIn('⭐', stats)
        self.assertIn('👍', stats)
    
    def test_get_user_reactions(self):
        """Test user reactions retrieval"""
        reactions = self.reaction_processor.get_user_reactions(123)
        
        # Should return a list
        self.assertIsInstance(reactions, list)
    
    def test_coordinator_reaction_config(self):
        """Test coordinator reaction rewards configuration"""
        # Import here to avoid circular imports
        from core.coordinator import CoordinadorCentral
        from core.event_bus import event_bus
        
        coordinator = CoordinadorCentral(event_bus)
        config = coordinator._get_reaction_rewards_config()
        
        # Should return a dictionary with reaction rewards
        self.assertIsInstance(config, dict)
        self.assertIn('❤️', config)
        self.assertIn('🔥', config)
        self.assertIn('⭐', config)
        self.assertIn('👍', config)
        
        # Check reward values
        self.assertEqual(config['❤️'], 10)
        self.assertEqual(config['🔥'], 15)
        self.assertEqual(config['⭐'], 20)
        self.assertEqual(config['👍'], 5)


if __name__ == '__main__':
    unittest.main()
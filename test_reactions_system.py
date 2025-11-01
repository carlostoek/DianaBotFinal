"""
Tests de integración para el sistema de reacciones
"""

import unittest
from unittest.mock import Mock, patch
from modules.gamification.reactions import ReactionProcessor
from core.coordinator import CoordinadorCentral


class TestReactionSystem(unittest.TestCase):
    """Test cases for the reaction system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reaction_processor = ReactionProcessor()
        self.mock_event_bus = Mock()
        self.coordinator = CoordinadorCentral(self.mock_event_bus)
    
    def test_reaction_processor_initialization(self):
        """Test that reaction processor initializes correctly"""
        self.assertIsNotNone(self.reaction_processor)
        self.assertIsInstance(self.reaction_processor, ReactionProcessor)
        
        # Check default rewards configuration
        self.assertIn('❤️', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('🔥', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('⭐', self.reaction_processor.DEFAULT_REACTION_REWARDS)
        self.assertIn('👍', self.reaction_processor.DEFAULT_REACTION_REWARDS)
    
    @patch('modules.gamification.reactions.get_db')
    @patch('modules.gamification.reactions.besitos_service')
    @patch('modules.gamification.reactions.event_bus')
    def test_process_reaction_success(self, mock_event_bus, mock_besitos_service, mock_get_db):
        """Test successful reaction processing"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock besitos service
        mock_besitos_service.grant_besitos.return_value = True
        
        # Mock event bus
        mock_event_bus.publish = Mock()
        
        # Test data
        user_id = 123
        content_type = "narrative_fragment"
        content_id = 456
        reaction_type = "❤️"
        
        # Process reaction
        result = self.reaction_processor.process_reaction(
            user_id, content_type, content_id, reaction_type
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['besitos_earned'], 10)  # Default reward for ❤️
        self.assertIn('message', result)
        
        # Verify besitos were granted
        mock_besitos_service.grant_besitos.assert_called_once()
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
    
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
    
    def test_coordinator_reaction_operation(self):
        """Test coordinator reaction operation"""
        # Mock transaction manager
        mock_tx = Mock()
        mock_tx.execute.return_value = True
        mock_tx.on_commit = Mock()
        
        # Mock transaction manager context
        self.coordinator.transaction_manager.begin.return_value.__enter__.return_value = mock_tx
        
        # Test data
        user_id = 123
        content_type = "narrative_fragment"
        content_id = 456
        reaction = "❤️"
        
        # Execute reaction operation
        result = self.coordinator.REACCIONAR_CONTENIDO(
            user_id, content_type, content_id, reaction
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['besitos_earned'], 10)
        
        # Verify transaction operations were called
        self.assertTrue(mock_tx.execute.called)
        self.assertTrue(mock_tx.on_commit.called)
    
    def test_coordinator_reaction_config(self):
        """Test coordinator reaction rewards configuration"""
        config = self.coordinator._get_reaction_rewards_config()
        
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
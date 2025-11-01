"""
Tests para la operación REACCIONAR_CONTENIDO del CoordinadorCentral
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.coordinator import CoordinadorCentral
from core.event_bus import event_bus


class TestCoordinatorReactions:
    """Tests para la operación REACCIONAR_CONTENIDO"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = CoordinadorCentral(event_bus)
        
    def test_react_to_content_success(self):
        """Test que reacción a contenido funciona correctamente"""
        # Mock de transaction manager con context manager
        mock_tx = Mock()
        mock_tx.__enter__ = Mock(return_value=mock_tx)
        mock_tx.__exit__ = Mock(return_value=None)
        mock_tx.execute.side_effect = [
            Mock(success=True, data={'content': 'test content'}),  # content validation
            Mock(success=True, data={  # reaction registration
                'success': True,
                'reaction_id': 123,
                'besitos_earned': 10,
                'message': 'Reacción registrada exitosamente'
            }),
            Mock(success=True, data=[]),  # achievements
            Mock(success=True, data=[]),  # missions
            Mock(success=True, data={'component_completed': 1})  # experience
        ]
        
        with patch.object(self.coordinator.transaction_manager, 'begin', return_value=mock_tx):
            with patch.object(self.coordinator, '_get_related_experiences_by_content', return_value=[1]):
                result = self.coordinator.REACCIONAR_CONTENIDO(
                    user_id=1,
                    content_type='narrative_fragment',
                    content_id=100,
                    reaction='❤️'
                )
                
                assert result['success'] is True
                assert result['reaction_id'] == 123
                assert result['besitos_earned'] == 10
                assert result['experiences_updated'] == [1]
                
                # Verificar que se llamaron las operaciones correctas
                assert mock_tx.execute.call_count == 5
                
    def test_react_to_content_not_found(self):
        """Test que reacción falla cuando contenido no existe"""
        mock_tx = Mock()
        mock_tx.__enter__ = Mock(return_value=mock_tx)
        mock_tx.__exit__ = Mock(return_value=None)
        mock_tx.execute.return_value = None  # Simula que no se encontró contenido
        
        with patch.object(self.coordinator.transaction_manager, 'begin', return_value=mock_tx):
            result = self.coordinator.REACCIONAR_CONTENIDO(
                user_id=1,
                content_type='narrative_fragment',
                content_id=999,
                reaction='❤️'
            )
            
            assert result['success'] is False
            assert result['reason'] == 'content_not_found'
            
    def test_react_to_content_reaction_failed(self):
        """Test que reacción falla cuando el módulo de reacciones falla"""
        mock_tx = Mock()
        mock_tx.__enter__ = Mock(return_value=mock_tx)
        mock_tx.__exit__ = Mock(return_value=None)
        mock_tx.execute.side_effect = [
            Mock(success=True, data={'content': 'test content'}),  # content validation
            Mock(success=False, data={  # reaction registration failed
                'reason': 'already_reacted',
                'message': 'Ya has reaccionado a este contenido'
            })
        ]
        
        with patch.object(self.coordinator.transaction_manager, 'begin', return_value=mock_tx):
            result = self.coordinator.REACCIONAR_CONTENIDO(
                user_id=1,
                content_type='narrative_fragment',
                content_id=100,
                reaction='❤️'
            )
            
            assert result['success'] is False
            assert result['reason'] == 'already_reacted'
            assert 'Ya has reaccionado' in result['message']
            
    def test_react_to_content_with_experiences(self):
        """Test que reacción actualiza experiencias relacionadas"""
        mock_tx = Mock()
        mock_tx.__enter__ = Mock(return_value=mock_tx)
        mock_tx.__exit__ = Mock(return_value=None)
        mock_tx.execute.side_effect = [
            Mock(success=True, data={'content': 'test content'}),  # content validation
            Mock(success=True, data={  # reaction registration
                'success': True,
                'reaction_id': 123,
                'besitos_earned': 15,
                'message': 'Reacción registrada exitosamente'
            }),
            Mock(success=True, data=[]),  # achievements
            Mock(success=True, data=[]),  # missions
            Mock(success=True, data={'component_completed': 1}),  # experience 1
            Mock(success=True, data={'component_completed': 2})   # experience 2
        ]
        
        with patch.object(self.coordinator.transaction_manager, 'begin', return_value=mock_tx):
            with patch.object(self.coordinator, '_get_related_experiences_by_content', return_value=[1, 2]):
                result = self.coordinator.REACCIONAR_CONTENIDO(
                    user_id=1,
                    content_type='channel_post',
                    content_id=200,
                    reaction='🔥'
                )
                
                assert result['success'] is True
                assert result['besitos_earned'] == 15
                assert result['experiences_updated'] == [1, 2]
                
                # Verificar que se llamó para cada experiencia
                assert mock_tx.execute.call_count == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
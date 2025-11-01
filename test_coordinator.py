"""
Tests unitarios para el CoordinadorCentral y TransactionManager
"""

import pytest
from unittest.mock import Mock, patch
from core.coordinator import CoordinadorCentral, ValidationResult
from core.transaction_manager import DistributedTransaction, TransactionManager, OperationResult


class TestTransactionManager:
    """Tests para TransactionManager"""
    
    def test_transaction_manager_initialization(self):
        """Test que TransactionManager se inicializa correctamente"""
        manager = TransactionManager()
        assert manager.active_transactions == []
        assert manager.get_active_transactions_count() == 0
    
    def test_begin_transaction(self):
        """Test que se puede iniciar una transacción"""
        manager = TransactionManager()
        transaction = manager.begin()
        
        assert isinstance(transaction, DistributedTransaction)
        assert manager.get_active_transactions_count() == 1
    
    def test_distributed_transaction_context_manager(self):
        """Test que DistributedTransaction funciona como context manager"""
        manager = TransactionManager()
        
        with manager.begin() as tx:
            assert isinstance(tx, DistributedTransaction)
            # La transacción debería estar activa
            assert len(tx.operations) == 0
            assert len(tx.rollback_stack) == 0
            assert len(tx.commit_callbacks) == 0
    
    def test_execute_operation_success(self):
        """Test que se puede ejecutar una operación exitosamente"""
        manager = TransactionManager()
        
        with manager.begin() as tx:
            result = tx.execute('narrative.apply_decision', 
                              user_id=1, fragment_id=1, decision_id=1)
            
            assert result.success is True
            assert 'rewards' in result.data
            assert len(tx.operations) == 1
            assert len(tx.rollback_stack) == 1
    
    def test_execute_operation_unknown(self):
        """Test que operación desconocida retorna error"""
        manager = TransactionManager()
        
        with manager.begin() as tx:
            result = tx.execute('unknown.operation', user_id=1)
            
            assert result.success is False
            assert 'no soportada' in result.error.lower()
    
    def test_on_commit_callback(self):
        """Test que se pueden registrar callbacks de commit"""
        manager = TransactionManager()
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        with manager.begin() as tx:
            tx.on_commit(test_callback)
            assert len(tx.commit_callbacks) == 1
        
        # El callback debería haberse ejecutado al salir del context manager
        assert callback_called is True


class TestCoordinadorCentral:
    """Tests para CoordinadorCentral"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_event_bus = Mock()
        self.coordinator = CoordinadorCentral(self.mock_event_bus)
    
    def test_coordinator_initialization(self):
        """Test que CoordinadorCentral se inicializa correctamente"""
        assert self.coordinator.event_bus == self.mock_event_bus
        assert isinstance(self.coordinator.transaction_manager, TransactionManager)
        assert 'narrative' in self.coordinator.validators
        assert 'vip' in self.coordinator.validators
        assert 'items' in self.coordinator.validators
        assert 'level' in self.coordinator.validators
    
    def test_validation_result(self):
        """Test que ValidationResult funciona correctamente"""
        # Test con validación exitosa
        result1 = ValidationResult(is_valid=True)
        assert result1.is_valid is True
        assert result1.missing == []
        assert result1.suggestions == []
        
        # Test con validación fallida
        result2 = ValidationResult(
            is_valid=False, 
            missing=['vip_required', 'level_5'],
            suggestions=['Suscríbete al VIP', 'Sube de nivel']
        )
        assert result2.is_valid is False
        assert 'vip_required' in result2.missing
        assert 'Suscríbete al VIP' in result2.suggestions
    
    @patch('core.coordinator.CoordinadorCentral._validate_composite_requirements')
    def test_tomar_decision_success(self, mock_validate):
        """Test que TOMAR_DECISION funciona exitosamente"""
        # Configurar mock para validación exitosa
        mock_validate.return_value = ValidationResult(is_valid=True)
        
        result = self.coordinator.TOMAR_DECISION(
            user_id=1, fragment_id=1, decision_id=1
        )
        
        assert result['success'] is True
        assert 'narrative_result' in result
        assert 'rewards_granted' in result
        assert 'experiences_updated' in result
        
        # Verificar que se llamó a la validación
        mock_validate.assert_called_once_with(
            1, 1, ['narrative', 'vip', 'items', 'level']
        )
    
    @patch('core.coordinator.CoordinadorCentral._validate_composite_requirements')
    def test_tomar_decision_validation_failed(self, mock_validate):
        """Test que TOMAR_DECISION falla cuando validación falla"""
        # Configurar mock para validación fallida
        mock_validate.return_value = ValidationResult(
            is_valid=False, 
            missing=['vip_required']
        )
        
        result = self.coordinator.TOMAR_DECISION(
            user_id=1, fragment_id=1, decision_id=1
        )
        
        assert result['success'] is False
        assert 'missing_requirements' in result
        assert 'vip_required' in result['missing_requirements']
        assert 'suggestions' in result
        
        # Verificar que se emitió evento de acceso denegado
        self.mock_event_bus.publish.assert_called_once()
        call_args = self.mock_event_bus.publish.call_args[0]
        assert call_args[0] == 'coordinator.access_denied'
        assert call_args[1]['user_id'] == 1
    
    @patch('core.coordinator.CoordinadorCentral._validate_composite_requirements')
    def test_tomar_decision_narrative_failed(self, mock_validate):
        """Test que TOMAR_DECISION falla cuando narrativa falla"""
        # Configurar mock para validación exitosa
        mock_validate.return_value = ValidationResult(is_valid=True)
        
        # Mockear transaction manager para simular fallo en narrativa
        with patch.object(self.coordinator.transaction_manager, 'begin') as mock_begin:
            mock_tx = Mock()
            mock_begin.return_value.__enter__.return_value = mock_tx
            
            # Simular fallo en operación narrativa
            mock_tx.execute.return_value = OperationResult(
                success=False, 
                error='Error en narrativa'
            )
            
            result = self.coordinator.TOMAR_DECISION(
                user_id=1, fragment_id=1, decision_id=1
            )
            
            assert result['success'] is False
            assert 'Error en narrativa' in result['error']
    
    @patch('core.coordinator.CoordinadorCentral._validate_fragment_requirements')
    def test_acceder_narrativa_vip_success(self, mock_validate):
        """Test que ACCEDER_NARRATIVA_VIP funciona exitosamente"""
        # Configurar mocks
        mock_validate.return_value = ValidationResult(is_valid=True)
        
        # Mockear transaction manager
        with patch.object(self.coordinator.transaction_manager, 'begin') as mock_begin:
            mock_tx = Mock()
            mock_begin.return_value.__enter__.return_value = mock_tx
            
            # Simular operaciones exitosas
            mock_tx.execute.side_effect = [
                OperationResult(success=True, data=True),  # VIP check
                OperationResult(success=True, data=True),  # Channel check
                OperationResult(success=True, data={'content': 'VIP content'})  # Content
            ]
            
            result = self.coordinator.ACCEDER_NARRATIVA_VIP(
                user_id=1, fragment_id=1
            )
            
            assert result['success'] is True
            assert result['content'] == {'content': 'VIP content'}
            assert result['vip_status'] == 'active'
            
            # Verificar que se emitió evento de acceso
            self.mock_event_bus.publish.assert_called_with(
                'analytics.vip_content_accessed',
                {
                    'user_id': 1,
                    'fragment_id': 1,
                    'timestamp': pytest.approx(None, abs=1)  # Aproximado por timestamp
                }
            )
    
    def test_acceder_narrativa_vip_no_vip(self):
        """Test que ACCEDER_NARRATIVA_VIP falla cuando no es VIP"""
        # Mockear transaction manager para simular no VIP
        with patch.object(self.coordinator.transaction_manager, 'begin') as mock_begin:
            mock_tx = Mock()
            mock_begin.return_value.__enter__.return_value = mock_tx
            
            # Simular que no es VIP
            mock_tx.execute.return_value = OperationResult(success=True, data=False)
            
            result = self.coordinator.ACCEDER_NARRATIVA_VIP(
                user_id=1, fragment_id=1
            )
            
            assert result['success'] is False
            assert result['reason'] == 'vip_required'
            assert 'offer' in result
            assert 'preview' in result
            
            # Verificar que se emitió evento de acceso denegado
            self.mock_event_bus.publish.assert_called_with(
                'coordinator.access_denied',
                {
                    'user_id': 1,
                    'fragment_id': 1,
                    'reason': 'vip_required',
                    'offer_generated': True,
                    'timestamp': pytest.approx(None, abs=1)
                }
            )
    
    def test_get_requirement_suggestions(self):
        """Test que se generan sugerencias correctamente"""
        missing_requirements = [
            'vip_required',
            'min_level_5',
            'item_sword_required',
            'achievement_explorer'
        ]
        
        suggestions = self.coordinator._get_requirement_suggestions(missing_requirements)
        
        assert len(suggestions) == 4
        assert any('VIP' in s for s in suggestions)
        assert any('nivel' in s for s in suggestions)
        assert any('tienda' in s for s in suggestions)
        assert any('logros' in s for s in suggestions)
    
    def test_generate_personalized_vip_offer(self):
        """Test que se genera oferta VIP"""
        offer = self.coordinator._generate_personalized_vip_offer(user_id=1)
        
        assert offer is not None
        assert offer['type'] == 'vip_subscription'
        assert 'discount_percentage' in offer
        assert 'trial_days' in offer
        assert 'message' in offer
    
    def test_get_content_preview(self):
        """Test que se obtiene vista previa de contenido"""
        preview = self.coordinator._get_content_preview(fragment_id=1)
        
        assert isinstance(preview, str)
        assert 'VIP' in preview
        assert 'exclusivo' in preview


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"""
Tests unitarios para el motor de experiencias unificadas
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Import experiences modules
from modules.experiences.engine import ExperienceEngine
from modules.experiences.validator import CompositeValidator
from database.models import (
    Experience, ExperienceComponent, UserExperienceProgress, 
    UserComponentCompletion, ExperienceRequirement, ExperienceReward
)


class TestCompositeValidator:
    """Tests para CompositeValidator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_db = Mock()
        self.validator = CompositeValidator()
        self.validator.db = self.mock_db
    
    def test_validate_composite_requirements_success(self):
        """Test que validación de requisitos compuestos funciona correctamente"""
        # Mock de requisitos
        mock_requirements = [
            {'type': 'level', 'min_level': 3},
            {'type': 'vip_membership', 'required': True},
            {'type': 'besitos', 'min_amount': 500}
        ]
        
        # Mock de validaciones individuales exitosas
        with patch.object(self.validator, '_validate_single_requirement') as mock_validate:
            mock_validate.return_value = (True, {'message': 'Requirement met'})
            
            result = self.validator.validate_composite_requirements(1, mock_requirements)
            
            assert result['all_valid'] is True
            assert len(result['validation_results']) == 3
            for validation in result['validation_results']:
                assert validation['is_valid'] is True
    
    def test_validate_composite_requirements_failure(self):
        """Test que validación falla cuando faltan requisitos"""
        # Mock de requisitos
        mock_requirements = [
            {'type': 'level', 'min_level': 5},
            {'type': 'vip_membership', 'required': True},
            {'type': 'besitos', 'min_amount': 500}
        ]
        
        # Mock de validaciones mixtas (algunas fallan)
        with patch.object(self.validator, '_validate_single_requirement') as mock_validate:
            mock_validate.side_effect = [
                (False, {'message': 'Level too low'}),
                (True, {'message': 'VIP requirement met'}),
                (False, {'message': 'Not enough besitos'})
            ]
            
            result = self.validator.validate_composite_requirements(1, mock_requirements)
            
            assert result['all_valid'] is False
            assert len(result['validation_results']) == 3
            assert result['validation_results'][0]['is_valid'] is False
            assert result['validation_results'][1]['is_valid'] is True
            assert result['validation_results'][2]['is_valid'] is False
    
    def test_can_start_experience_success(self):
        """Test que verifica si usuario puede iniciar experiencia exitosamente"""
        # Mock de requisitos de experiencia
        mock_requirements = [Mock()]
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_requirements
        
        with patch.object(self.validator, 'validate_composite_requirements') as mock_validate:
            mock_validate.return_value = {'all_valid': True, 'validation_results': []}
            
            can_start, missing_reqs = self.validator.can_start_experience(1, 1)
            
            assert can_start is True
            assert len(missing_reqs) == 0
    
    def test_can_start_experience_failure(self):
        """Test que verifica si usuario NO puede iniciar experiencia"""
        # Mock de requisitos de experiencia
        mock_requirements = [Mock()]
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_requirements
        
        with patch.object(self.validator, 'validate_composite_requirements') as mock_validate:
            mock_validate.return_value = {
                'all_valid': False, 
                'validation_results': [
                    {'requirement': {'type': 'level'}, 'is_valid': False, 'details': {'message': 'Level too low'}}
                ]
            }
            
            can_start, missing_reqs = self.validator.can_start_experience(1, 1)
            
            assert can_start is False
            assert len(missing_reqs) == 1
            assert missing_reqs[0]['type'] == 'level'


class TestExperienceEngine:
    """Tests para ExperienceEngine"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_db = Mock()
        self.engine = ExperienceEngine()
        self.engine.db = self.mock_db
    
    def test_start_experience_success(self):
        """Test que se puede iniciar una experiencia exitosamente"""
        # Mock de validación exitosa
        with patch.object(self.engine, '_validate_requirements') as mock_validate:
            mock_validate.return_value = (True, [])
            
            # Mock de que no existe progreso previo
            self.mock_db.query.return_value.filter.return_value.first.return_value = None
            
            # Mock de primer componente
            mock_component = Mock()
            mock_component.id = 1
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_component
            
            result = self.engine.start_experience(1, 1)
            
            assert result['success'] is True
            assert result['status'] == 'started'
            assert 'progress' in result
            
            # Verificar que se guardó en la base de datos
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
    
    def test_start_experience_requirements_failed(self):
        """Test que no se puede iniciar experiencia sin requisitos"""
        # Mock de validación fallida
        with patch.object(self.engine, '_validate_requirements') as mock_validate:
            mock_validate.return_value = (False, ['level_5'])
            
            result = self.engine.start_experience(1, 1)
            
            assert result['success'] is False
            assert result['error'] == 'requirements_not_met'
            assert 'level_5' in result['missing_requirements']
            
            # Verificar que NO se guardó en la base de datos
            self.mock_db.add.assert_not_called()
            self.mock_db.commit.assert_not_called()
    
    def test_start_experience_already_completed(self):
        """Test que no se puede reiniciar experiencia completada"""
        # Mock de validación exitosa
        with patch.object(self.engine, '_validate_requirements') as mock_validate:
            mock_validate.return_value = (True, [])
            
            # Mock de progreso ya completado
            mock_progress = Mock()
            mock_progress.status = 'completed'
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_progress
            
            result = self.engine.start_experience(1, 1)
            
            assert result['success'] is False
            assert result['error'] == 'experience_already_completed'
    
    def test_start_experience_resume(self):
        """Test que se puede reanudar experiencia en progreso"""
        # Mock de validación exitosa
        with patch.object(self.engine, '_validate_requirements') as mock_validate:
            mock_validate.return_value = (True, [])
            
            # Mock de progreso en progreso
            mock_progress = Mock()
            mock_progress.status = 'in_progress'
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_progress
            
            result = self.engine.start_experience(1, 1)
            
            assert result['success'] is True
            assert result['status'] == 'resumed'
            assert result['progress'] == mock_progress
    
    def test_complete_component_success(self):
        """Test que se puede completar un componente"""
        # Mock de progreso
        mock_progress = Mock()
        mock_progress.user_id = 1
        mock_progress.experience_id = 1
        mock_progress.components_completed = 0
        mock_progress.components_total = 3
        mock_progress.completion_percentage = 0.0
        
        # Mock de componente
        mock_component = Mock()
        mock_component.id = 1
        mock_component.sequence_order = 1
        mock_component.completion_rewards = {'besitos': 25}
        
        # Mock de experiencia
        mock_experience = Mock()
        mock_experience.components = [mock_component, Mock(), Mock()]
        
        # Mock de siguiente componente
        with patch.object(self.engine, '_get_next_component') as mock_next:
            mock_next.return_value = Mock()
            
            result = self.engine.complete_component(mock_progress, mock_component, mock_experience)
            
            assert result['success'] is True
            assert 'completion' in result
            assert 'rewards_granted' in result
            assert result['rewards_granted']['besitos'] == 25
            
            # Verificar que se actualizó el progreso
            assert mock_progress.components_completed == 1
            assert mock_progress.completion_percentage == 33.33
            assert mock_progress.last_activity_at is not None
            
            # Verificar que se guardó en la base de datos
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
    
    def test_complete_component_final_component(self):
        """Test que completar último componente completa la experiencia"""
        # Mock de progreso
        mock_progress = Mock()
        mock_progress.user_id = 1
        mock_progress.experience_id = 1
        mock_progress.components_completed = 2
        mock_progress.components_total = 3
        mock_progress.completion_percentage = 66.67
        
        # Mock de componente
        mock_component = Mock()
        mock_component.id = 3
        mock_component.sequence_order = 3
        mock_component.completion_rewards = {'besitos': 50}
        
        # Mock de experiencia
        mock_experience = Mock()
        mock_experience.id = 1
        mock_experience.completion_count = 0
        mock_experience.rewards = [Mock(reward_type='besitos', reward_value={'amount': 100})]
        
        # Mock de que no hay siguiente componente
        with patch.object(self.engine, '_get_next_component') as mock_next:
            mock_next.return_value = None
            
            # Mock de recompensas de experiencia
            with patch.object(self.engine, '_grant_experience_rewards') as mock_grant:
                mock_grant.return_value = {'besitos': 100}
                
                result = self.engine.complete_component(mock_progress, mock_component, mock_experience)
                
                assert result['success'] is True
                assert 'experience_completed' in result
                assert result['experience_completed'] is True
                
                # Verificar que se actualizó el progreso a completado
                assert mock_progress.status == 'completed'
                assert mock_progress.completed_at is not None
                
                # Verificar que se actualizó la experiencia
                assert mock_experience.completion_count == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
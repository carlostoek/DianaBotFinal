"""
Tests unitarios para el motor de experiencias unificadas
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
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
        self.validator = CompositeValidator(self.mock_db)
    
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
        mock_requirement = Mock()
        mock_requirement.requirement_type = 'level'
        mock_requirement.requirement_value = {'min_level': 1}
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_requirement]
        
        can_start, missing_reqs = self.validator.can_start_experience(1, 1)
        
        assert can_start is True
        assert len(missing_reqs) == 0
    
    def test_can_start_experience_failure(self):
        """Test que verifica si usuario NO puede iniciar experiencia"""
        # Mock de requisitos de experiencia
        mock_requirement = Mock()
        mock_requirement.requirement_type = 'level'
        mock_requirement.requirement_value = {'min_level': 5}  # Requiere nivel 5
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_requirement]
        
        can_start, missing_reqs = self.validator.can_start_experience(1, 1)
        
        assert can_start is False
        assert len(missing_reqs) == 1
        assert missing_reqs[0]['requirement'].requirement_type == 'level'


class TestExperienceEngine:
    """Tests para ExperienceEngine"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_db = Mock()
        self.engine = ExperienceEngine(self.mock_db)
    
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
            
            # Mock de experiencia
            mock_experience = Mock()
            mock_experience.start_count = 0
            
            # Configurar mocks para diferentes queries
            self.mock_db.query.return_value.filter.return_value.first.side_effect = [
                None,  # existing_progress
                mock_component,  # first_component
                mock_experience  # experience
            ]
            
            result = self.engine.start_experience(1, 1)
            
            assert result['success'] is True
            assert result['status'] == 'started'
            assert 'progress' in result
            
            # Verificar que se guardó en la base de datos
            self.mock_db.add.assert_called_once()
            assert self.mock_db.commit.call_count == 2
    
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
    
    def test_progress_experience_success(self):
        """Test que se puede progresar en una experiencia completando un componente"""
        # Mock de progreso
        mock_progress = Mock()
        mock_progress.id = 1
        mock_progress.user_id = 1
        mock_progress.experience_id = 1
        mock_progress.status = 'in_progress'
        mock_progress.components_completed = 0
        mock_progress.components_total = 3
        mock_progress.completion_percentage = 0.0
        mock_progress.current_component_id = 1
        
        # Mock de componente
        mock_component = Mock()
        mock_component.id = 1
        mock_component.sequence_order = 1
        mock_component.completion_rewards = {'besitos': 25}
        
        # Mock de siguiente componente
        mock_next_component = Mock()
        mock_next_component.id = 2
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_progress,  # user_progress
            mock_component,  # component
            None  # existing_completion
        ]
        
        with patch.object(self.engine, '_get_next_component') as mock_next:
            mock_next.return_value = mock_next_component
            
            result = self.engine.progress_experience(1, 1, 1)
            
            assert result['success'] is True
            assert 'component_completed' in result
            assert 'next_component' in result
            assert result['next_component'] == mock_next_component
            
            # Verificar que se guardó en la base de datos
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
    
    def test_progress_experience_final_component(self):
        """Test que completar último componente completa la experiencia"""
        # Mock de progreso
        mock_progress = Mock()
        mock_progress.id = 1
        mock_progress.user_id = 1
        mock_progress.experience_id = 1
        mock_progress.status = 'in_progress'
        mock_progress.components_completed = 2
        mock_progress.components_total = 3
        mock_progress.completion_percentage = 66.67
        mock_progress.current_component_id = 3
        
        # Mock de componente
        mock_component = Mock()
        mock_component.id = 3
        mock_component.sequence_order = 3
        mock_component.completion_rewards = {'besitos': 50}
        
        # Mock de experiencia
        mock_experience = Mock()
        mock_experience.id = 1
        mock_experience.completion_count = 0
        
        # Configurar mocks
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_progress,  # user_progress
            mock_component,  # component
            None  # existing_completion
        ]
        
        # Mock de que no hay siguiente componente
        with patch.object(self.engine, '_get_next_component') as mock_next:
            mock_next.return_value = None
            
            # Mock de complete_experience
            with patch.object(self.engine, 'complete_experience') as mock_complete:
                mock_complete.return_value = {
                    'success': True,
                    'progress': mock_progress,
                    'rewards_granted': [{'reward': Mock(), 'result': True}]
                }
                
                result = self.engine.progress_experience(1, 1, 3)
                
                assert result['success'] is True
                # Verificar que se llamó a complete_experience
                mock_complete.assert_called_once_with(1, 1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
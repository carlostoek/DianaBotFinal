"""
MongoDB schemas for flexible content storage
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NarrativeContent(BaseModel):
    """Schema for narrative fragment content in MongoDB"""
    fragment_key: str = Field(..., description="Unique identifier for the fragment")
    level_id: int = Field(..., description="Associated level ID")
    
    content: Dict[str, Any] = Field(..., description="Narrative content structure")
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (emotional_tone, soundtrack, reading_time)"
    )
    
    version: int = Field(default=1, description="Content version")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Decision(BaseModel):
    """Schema for narrative decisions"""
    decision_id: str = Field(..., description="Unique decision identifier")
    text: str = Field(..., description="Decision text shown to user")
    
    consequences: Dict[str, Any] = Field(
        ...,
        description="Consequences of this decision"
    )
    
    visible_if: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Conditions for decision visibility"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "decision_id": "dec_001",
                "text": "Acercarte con confianza",
                "consequences": {
                    "narrative_flags": ["confident_approach"],
                    "next_fragment": "fragment_002_confident",
                    "immediate_rewards": {"besitos": 5}
                },
                "visible_if": {
                    "has_item": "skeleton_key",
                    "trust_level_lucien": ">= 5"
                }
            }
        }


class FragmentContent(BaseModel):
    """Schema for detailed fragment content"""
    narrator: str = Field(default="default", description="Narrator character")
    text: str = Field(..., description="Main narrative text")
    
    media: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Media attachments (images, audio)"
    )
    
    decisions: List[Decision] = Field(
        default_factory=list,
        description="Available decisions for this fragment"
    )
    
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables that can be interpolated in text"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "narrator": "lucien",
                "text": "Lucien te observa con intensidad... {{trust_level_diana > 5 ? 'querida amiga' : 'visitante'}}",
                "media": [
                    {"type": "image", "url": "lucien_portrait.jpg", "alt": "Lucien"}
                ],
                "decisions": [
                    {
                        "decision_id": "dec_001",
                        "text": "Acercarte con confianza",
                        "consequences": {
                            "narrative_flags": ["confident_approach"],
                            "next_fragment": "fragment_002_confident",
                            "immediate_rewards": {"besitos": 5}
                        }
                    }
                ],
                "variables": {
                    "trust_level_diana": 7,
                    "intimacy_level_lucien": 3
                }
            }
        }


class TriviaQuestion(BaseModel):
    """Schema for trivia questions in MongoDB"""
    question_key: str = Field(..., description="Unique question identifier")
    category: str = Field(..., description="Question category")
    difficulty: str = Field(..., description="Difficulty level")
    
    question: Dict[str, Any] = Field(..., description="Question content")
    options: List[Dict[str, Any]] = Field(..., description="Answer options")
    
    rewards: Dict[str, Any] = Field(
        ...,
        description="Rewards for correct/incorrect answers"
    )
    
    time_limit_seconds: int = Field(default=30, description="Time limit for answering")
    available_after_fragment: Optional[str] = Field(
        default=None,
        description="Fragment required to unlock this question"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "question_key": "trivia_001",
                "category": "narrative_lore",
                "difficulty": "medium",
                "question": {
                    "text": "¿Cuál es el verdadero nombre de Diana antes de su transformación?",
                    "media_url": None
                },
                "options": [
                    {"option_id": "a", "text": "Elena", "is_correct": False},
                    {"option_id": "b", "text": "Sofía", "is_correct": True},
                    {"option_id": "c", "text": "Isabella", "is_correct": False},
                    {"option_id": "d", "text": "Desconocido", "is_correct": False}
                ],
                "rewards": {
                    "correct": {"besitos": 10, "hint_item": "diana_diary_page"},
                    "incorrect": {"besitos": 2}
                },
                "time_limit_seconds": 30,
                "available_after_fragment": "fragment_005"
            }
        }


class ConfigurationSchema(BaseModel):
    """Schema for configuration templates in MongoDB"""
    schema_type: str = Field(..., description="Type of configuration schema")
    version: str = Field(..., description="Schema version")
    
    fields: List[Dict[str, Any]] = Field(
        ...,
        description="Schema field definitions"
    )
    
    validation_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Validation rules for the schema"
    )
    
    propagation_targets: List[str] = Field(
        default_factory=list,
        description="Target systems for configuration propagation"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "schema_type": "narrative_experience",
                "version": "1.0",
                "fields": [
                    {
                        "field_name": "experience_title",
                        "field_type": "string",
                        "required": True,
                        "validation": {"min_length": 5, "max_length": 100}
                    },
                    {
                        "field_name": "narrative_fragments",
                        "field_type": "array",
                        "required": True,
                        "item_schema": {
                            "fragment_content": "text",
                            "decisions": "array",
                            "unlock_conditions": "object"
                        }
                    }
                ],
                "validation_rules": [
                    {
                        "rule": "if vip_requirements is true, besitos_on_completion must be >= 20",
                        "error_message": "Las experiencias VIP deben otorgar al menos 20 besitos"
                    }
                ],
                "propagation_targets": [
                    "narrative_fragments",
                    "missions",
                    "items",
                    "achievements",
                    "channel_posts"
                ]
            }
        }
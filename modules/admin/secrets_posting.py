"""
Secret posting module for publishing hints and codes in channels
"""
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import ChannelPost, SecretCode, Channel
from database.connection import get_db


class SecretPostingService:
    """Service for managing secret posts in channels"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_secret_codes(self) -> List[Dict[str, Any]]:
        """Get list of active secret codes that haven't been posted recently"""
        # Get secret codes that are active
        secret_codes = self.db.query(SecretCode).filter(
            SecretCode.is_active == True
        ).all()
        
        # Check which ones haven't been posted in the last 7 days
        recent_posts = self.db.query(ChannelPost).filter(
            ChannelPost.post_type == 'secret'
        ).all()
        
        recent_fragment_keys = []
        for post in recent_posts:
            if post.linked_fragment_id:
                recent_fragment_keys.append(post.linked_fragment_id)
        
        available_codes = []
        for code in secret_codes:
            if code.fragment_key not in recent_fragment_keys:
                available_codes.append({
                    'id': code.id,
                    'code': code.code,
                    'fragment_key': code.fragment_key,
                    'description': code.description
                })
        
        return available_codes
    
    def create_secret_post(self, channel_id: int, secret_code_id: int) -> ChannelPost:
        """Create a secret post for a channel"""
        secret_code = self.db.query(SecretCode).filter(
            SecretCode.id == secret_code_id
        ).first()
        
        if not secret_code:
            raise ValueError(f"Secret code with ID {secret_code_id} not found")
        
        # Create encrypted/obfuscated hint
        hint = self._create_hint(str(secret_code.code))
        
        # Create the post
        post = ChannelPost(
            channel_id=channel_id,
            post_type='secret',
            content=hint,
            post_metadata={
                'secret_code_id': secret_code_id,
                'fragment_key': str(secret_code.fragment_key),
                'hint_type': 'encrypted_code'
            },
            is_protected=True,
            status='draft'
        )
        
        self.db.add(post)
        self.db.commit()
        
        return post
    
    def _create_hint(self, code: str) -> str:
        """Create an encrypted/obfuscated hint from a secret code"""
        hint_types = [
            self._create_caesar_cipher,
            self._create_reverse_hint,
            self._create_number_hint,
            self._create_riddle_hint
        ]
        
        hint_func = random.choice(hint_types)
        return hint_func(code)
    
    def _create_caesar_cipher(self, code: str) -> str:
        """Create a Caesar cipher hint"""
        shift = random.randint(1, 5)
        encrypted = ''
        
        for char in code:
            if char.isalpha():
                if char.isupper():
                    encrypted += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                else:
                    encrypted += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                encrypted += char
        
        return (
            f"🔐 *Pista Secreta*\n\n"
            f"He encontrado un mensaje cifrado:\n"
            f"`{encrypted}`\n\n"
            f"💡 *Consejo:* Cada letra ha sido desplazada {shift} posiciones en el alfabeto.\n"
            f"Usa `/secret <código>` para descubrir el secreto."
        )
    
    def _create_reverse_hint(self, code: str) -> str:
        """Create a reversed hint"""
        reversed_code = code[::-1]
        
        return (
            f"🔍 *Pista Secreta*\n\n"
            f"He encontrado un código al revés:\n"
            f"`{reversed_code}`\n\n"
            f"💡 *Consejo:* Lee el código de derecha a izquierda.\n"
            f"Usa `/secret <código>` para descubrir el secreto."
        )
    
    def _create_number_hint(self, code: str) -> str:
        """Create a hint with numbers representing letters"""
        number_hint = ' '.join([str(ord(char) - ord('A') + 1) if char.isalpha() else char for char in code])
        
        return (
            f"🔢 *Pista Secreta*\n\n"
            f"He encontrado un código numérico:\n"
            f"`{number_hint}`\n\n"
            f"💡 *Consejo:* Cada número representa una letra (A=1, B=2, etc.).\n"
            f"Usa `/secret <código>` para descubrir el secreto."
        )
    
    def _create_riddle_hint(self, code: str) -> str:
        """Create a riddle hint"""
        riddles = {
            'LUCIEN123': "El pasado de Lucien está oculto tras este código",
            'PROPHECY456': "La profecía se revela con este código",
            'CHAMBER789': "Una cámara oculta espera tras este código",
            'ALTERNATE999': "Un final alternativo se esconde aquí",
            'CHARACTER777': "El secreto de un personaje está en este código"
        }
        
        riddle = riddles.get(code, "Un secreto especial está oculto tras este código")
        
        return (
            f"🎭 *Pista Secreta*\n\n"
            f"{riddle}\n\n"
            f"💡 *Consejo:* El código secreto es: `{code}`\n"
            f"Usa `/secret <código>` para descubrir el secreto."
        )
    
    def schedule_secret_posts(self, channel_ids: List[int]) -> List[ChannelPost]:
        """Schedule secret posts for multiple channels"""
        available_codes = self.get_available_secret_codes()
        
        if not available_codes:
            return []
        
        scheduled_posts = []
        
        for channel_id in channel_ids:
            # Pick a random secret code
            secret_code = random.choice(available_codes)
            
            # Create and schedule the post
            post = self.create_secret_post(channel_id, secret_code['id'])
            scheduled_posts.append(post)
            
            # Remove this code from available list to avoid duplicates
            available_codes = [code for code in available_codes if code['id'] != secret_code['id']]
            
            if not available_codes:
                break
        
        return scheduled_posts


def get_secret_posting_service() -> SecretPostingService:
    """Get secret posting service instance"""
    db = next(get_db())
    return SecretPostingService(db)
"""
Thai sentiment analyzer implementation.

This module provides Thai language sentiment analysis using a lexicon-based
approach with Thai-specific sentiment words and phrases.
"""

from typing import List, Dict, Set
import re
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.base_analyzer import SentimentAnalyzer
from core.models import SentimentScore, Language
from core.exceptions import SentimentAnalysisError


class ThaiSentimentAnalyzer(SentimentAnalyzer):
    """
    Lexicon-based sentiment analyzer for Thai text.
    
    Uses pre-defined lists of positive and negative Thai words,
    along with intensity modifiers and negation handling.
    """
    
    def __init__(self):
        """Initialize Thai sentiment analyzer with lexicons."""
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.intensity_modifiers = self._load_intensity_modifiers()
        self.negation_words = self._load_negation_words()
        self.emoji_sentiment = self._load_emoji_sentiment()
    
    def _load_positive_words(self) -> Set[str]:
        """Load positive Thai words."""
        return {
            # Basic positive words
            'ดี', 'เยี่ยม', 'ยอดเยี่ยม', 'เลิศ', 'ดีเยี่ยม', 'สุดยอด', 'เจ๋ง',
            'เก่ง', 'เด็ด', 'ปัง', 'เก๋', 'วิเศษ', 'น่าทึ่ง', 'โดดเด่น',
            
            # Emotional positive words
            'รัก', 'ชอบ', 'หลงรัก', 'ประทับใจ', 'ชื่นชม', 'ชื่นใจ', 'ดีใจ',
            'มีความสุข', 'สุข', 'สนุก', 'เพลิดเพลิน', 'สบายใจ', 'อบอุ่น',
            
            # Beauty and aesthetics
            'สวย', 'งาม', 'น่ารัก', 'เสน่ห์', 'มีเสน่ห์', 'น่าดู', 'น่าชม',
            'น่าอิจฉา', 'หรู', 'หรูหรา', 'สง่า', 'สง่างาม', 'ใส', 'เปล่งปลั่ง',
            
            # Quality and performance
            'คุณภาพ', 'มีคุณภาพ', 'ประสิทธิภาพ', 'ได้ผล', 'ใช้ได้', 'คุ้ม',
            'คุ้มค่า', 'ไม่แพง', 'ราคาดี', 'ประหยัด', 'มาตรฐาน', 'เหมาะสม',
            
            # Success and achievement
            'สำเร็จ', 'ชนะ', 'ได้', 'บรรลุ', 'สมปรารถนา', 'เฮง', 'โชคดี',
            'ถูกใจ', 'ตรงใจ', 'ลงตัว', 'เหมาะ', 'พอใจ', 'ถูกต้อง',
            
            # Intensity boosters
            'มาก', 'มากๆ', 'สุด', 'ที่สุด', 'เหลือเกิน', 'อย่างมาก', 'แสน',
            'เป็นที่สุด', 'ไม่มีใครเทียบ', 'เกินคาด', 'เกินไป'
        }
    
    def _load_negative_words(self) -> Set[str]:
        """Load negative Thai words."""
        return {
            # Basic negative words
            'แย่', 'เลว', 'ห่วย', 'เสีย', 'พัง', 'ไม่ดี', 'ไม่เยี่ยม', 'แรง',
            'หดหู่', 'เศร้า', 'ผิดหวัง', 'น่าเศร้า', 'น่าสงสार', 'น่าเสียดาย',
            
            # Emotional negative words
            'เกลียด', 'เบื่อ', 'น่าเบื่อ', 'โกรธ', 'หงุดหงิด', 'รำคาญ',
            'ฉุนเฉียว', 'ว้าวุ่น', 'วุ่นวาย', 'กังวล', 'เครียด', 'ตื่นเต้น',
            
            # Quality issues
            'ห่วย', 'แย่', 'เลว', 'ไม่มีคุณภาพ', 'ไม่ดี', 'ไม่ใช้ได้',
            'เสียเงิน', 'แพง', 'ไม่คุ้ม', 'ไม่คุ้มค่า', 'เสียของ', 'เสียเวลา',
            
            # Problems and failures
            'ผิด', 'ผิดพลาด', 'พลาด', 'ล้มเหลว', 'เสียหาย', 'เสียใจ',
            'ไม่สำเร็จ', 'ไม่ได้', 'ไม่ถูก', 'ปัญหา', 'ยุ่งยาก', 'ลำบาก',
            
            # Physical discomfort
            'ป่วย', 'ไม่สบาย', 'เจ็บ', 'ปวด', 'เมื่อย', 'เหนื่อย', 'อ่อนเพลีย',
            'ตาย', 'หาย', 'เสื่อม', 'เก่า', 'ชำรุด', 'ขาด', 'หัก', 'แตก',
            
            # Intensity boosters for negative
            'มาก', 'มากๆ', 'สุด', 'ที่สุด', 'เหลือเกิน', 'อย่างมาก',
            'เกินไป', 'เกินคาด', 'ไม่ไหว', 'ทนไม่ไหว'
        }
    
    def _load_intensity_modifiers(self) -> Dict[str, float]:
        """Load intensity modifier words and their multipliers."""
        return {
            # Positive intensifiers
            'มาก': 1.5, 'มากๆ': 1.8, 'สุด': 2.0, 'ที่สุด': 2.2,
            'เหลือเกิน': 1.8, 'อย่างมาก': 1.6, 'แสน': 1.7,
            'เป็นที่สุด': 2.0, 'เกินคาด': 1.5, 'เกินไป': 1.4,
            
            # Negative intensifiers
            'แย่มาก': 1.5, 'ห่วยมาก': 1.6, 'เลวที่สุด': 2.0,
            'ไม่ไหว': 1.4, 'ทนไม่ไหว': 1.7,
            
            # Diminishers
            'นิดหน่อย': 0.5, 'เล็กน้อย': 0.6, 'ค่อนข้าง': 0.8,
            'พอ': 0.7, 'พอๆ': 0.6, 'ปานกลาง': 0.5
        }
    
    def _load_negation_words(self) -> Set[str]:
        """Load negation words that flip sentiment."""
        return {
            'ไม่', 'ไม่ใช่', 'ไม่ได้', 'ไม่มี', 'ไม่เป็น', 'ไม่ควร',
            'ไม่ต้อง', 'ไม่จำเป็น', 'หยุด', 'เลิก', 'ห้าม', 'ไม่อยาก'
        }
    
    def _load_emoji_sentiment(self) -> Dict[str, float]:
        """Load emoji sentiment mappings."""
        return {
            # Positive emojis
            '😊': 0.5, '😃': 0.6, '😄': 0.7, '😁': 0.6, '😆': 0.5,
            '😍': 0.8, '🥰': 0.8, '😘': 0.7, '😗': 0.5, '😙': 0.5,
            '😚': 0.5, '🤗': 0.6, '🤩': 0.8, '😎': 0.6, '😋': 0.5,
            '👍': 0.5, '👏': 0.6, '🎉': 0.7, '✨': 0.5, '💕': 0.8,
            '❤️': 0.9, '💖': 0.8, '💝': 0.7, '🔥': 0.6, '⭐': 0.5,
            
            # Negative emojis
            '😢': -0.6, '😭': -0.8, '😞': -0.5, '😔': -0.4, '😟': -0.4,
            '😕': -0.3, '🙁': -0.3, '😣': -0.5, '😖': -0.6, '😫': -0.7,
            '😩': -0.6, '😤': -0.5, '😠': -0.7, '😡': -0.8, '🤬': -0.9,
            '👎': -0.5, '💔': -0.8, '😵': -0.6, '👹': -0.7, '💀': -0.8
        }
    
    def analyze(self, text: str) -> SentimentScore:
        """
        Analyze sentiment of Thai text.
        
        Args:
            text: Thai text to analyze for sentiment
            
        Returns:
            SentimentScore: Detailed sentiment analysis results
        """
        if not text or not text.strip():
            return SentimentScore(
                compound=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                confidence=1.0,
                analyzer_used=self.get_analyzer_name()
            )
        
        try:
            # Clean and tokenize text
            cleaned_text = self._preprocess_text(text)
            words = self._tokenize(cleaned_text)
            
            # Calculate sentiment scores
            positive_score = self._calculate_positive_score(words, text)
            negative_score = self._calculate_negative_score(words, text)
            emoji_score = self._calculate_emoji_score(text)
            
            # Combine scores
            total_positive = positive_score + max(0, emoji_score)
            total_negative = negative_score + max(0, -emoji_score)
            
            # Calculate compound score
            compound = self._calculate_compound_score(total_positive, total_negative, len(words))
            
            # Apply negation
            compound = self._apply_negation(compound, words)
            
            # Calculate component scores
            total_sentiment = total_positive + total_negative
            if total_sentiment > 0:
                positive = total_positive / total_sentiment
                negative = total_negative / total_sentiment
                neutral = max(0, 1 - positive - negative)
            else:
                positive = 0.0
                negative = 0.0
                neutral = 1.0
            
            # Calculate confidence
            confidence = min(1.0, abs(compound) + (total_sentiment / max(len(words), 1)) * 0.5)
            
            return SentimentScore(
                compound=max(-1.0, min(1.0, compound)),
                positive=positive,
                negative=negative,
                neutral=neutral,
                confidence=confidence,
                analyzer_used=self.get_analyzer_name()
            )
            
        except Exception as e:
            raise SentimentAnalysisError(f"Thai sentiment analysis failed: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess Thai text for analysis."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize some common variations
        text = text.replace('ๆ', '')  # Remove repetition marks for simplicity
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for Thai text."""
        # This is a simplified tokenization
        # In production, use pythainlp.tokenize.word_tokenize()
        words = []
        
        # Split by spaces first
        space_split = text.split()
        
        for segment in space_split:
            # Further split Thai text (simplified approach)
            current_word = ""
            for char in segment:
                if self._is_thai_char(char):
                    current_word += char
                else:
                    if current_word:
                        words.append(current_word)
                        current_word = ""
                    if char.strip():
                        words.append(char)
            
            if current_word:
                words.append(current_word)
        
        return [word for word in words if word.strip()]
    
    def _is_thai_char(self, char: str) -> bool:
        """Check if character is Thai."""
        return '\u0e00' <= char <= '\u0e7f'
    
    def _calculate_positive_score(self, words: List[str], full_text: str) -> float:
        """Calculate positive sentiment score."""
        score = 0.0
        
        for i, word in enumerate(words):
            if word in self.positive_words:
                base_score = 1.0
                
                # Apply intensity modifiers
                intensity = self._get_intensity_modifier(words, i)
                score += base_score * intensity
        
        # Check for positive phrases
        score += self._check_positive_phrases(full_text)
        
        return score
    
    def _calculate_negative_score(self, words: List[str], full_text: str) -> float:
        """Calculate negative sentiment score."""
        score = 0.0
        
        for i, word in enumerate(words):
            if word in self.negative_words:
                base_score = 1.0
                
                # Apply intensity modifiers
                intensity = self._get_intensity_modifier(words, i)
                score += base_score * intensity
        
        # Check for negative phrases
        score += self._check_negative_phrases(full_text)
        
        return score
    
    def _calculate_emoji_score(self, text: str) -> float:
        """Calculate sentiment score from emojis."""
        emoji_score = 0.0
        emoji_count = 0
        
        for char in text:
            if char in self.emoji_sentiment:
                emoji_score += self.emoji_sentiment[char]
                emoji_count += 1
        
        return emoji_score / max(emoji_count, 1) if emoji_count > 0 else 0.0
    
    def _get_intensity_modifier(self, words: List[str], word_index: int) -> float:
        """Get intensity modifier for a word based on surrounding context."""
        intensity = 1.0
        
        # Check previous words for intensifiers
        for i in range(max(0, word_index - 2), word_index):
            if words[i] in self.intensity_modifiers:
                intensity *= self.intensity_modifiers[words[i]]
        
        # Check following words for intensifiers
        for i in range(word_index + 1, min(len(words), word_index + 3)):
            if words[i] in self.intensity_modifiers:
                intensity *= self.intensity_modifiers[words[i]]
        
        return intensity
    
    def _calculate_compound_score(self, positive: float, negative: float, word_count: int) -> float:
        """Calculate compound sentiment score."""
        if word_count == 0:
            return 0.0
        
        # Normalize by word count
        normalized_positive = positive / word_count
        normalized_negative = negative / word_count
        
        # Calculate compound score
        compound = normalized_positive - normalized_negative
        
        # Apply sigmoid-like transformation to keep within reasonable bounds
        if compound > 0:
            compound = min(1.0, compound * 0.5)
        else:
            compound = max(-1.0, compound * 0.5)
        
        return compound
    
    def _apply_negation(self, compound: float, words: List[str]) -> float:
        """Apply negation logic to flip sentiment if needed."""
        negation_count = sum(1 for word in words if word in self.negation_words)
        
        # If odd number of negations, flip sentiment
        if negation_count % 2 == 1:
            compound = -compound
        
        return compound
    
    def _check_positive_phrases(self, text: str) -> float:
        """Check for positive phrase patterns."""
        positive_phrases = [
            'ดีมาก', 'เยี่ยมมาก', 'ชอบมาก', 'รักมาก', 'สวยมาก',
            'สุดยอด', 'ยอดเยี่ยม', 'ดีเยี่ยม', 'เจ๋งมาก', 'เด็ดมาก'
        ]
        
        score = 0.0
        for phrase in positive_phrases:
            if phrase in text:
                score += 0.5
        
        return score
    
    def _check_negative_phrases(self, text: str) -> float:
        """Check for negative phrase patterns."""
        negative_phrases = [
            'แย่มาก', 'ห่วยมาก', 'เลวมาก', 'เกลียดมาก', 'เบื่อมาก',
            'ไม่ดี', 'ไม่ชอบ', 'ไม่เยี่ยม', 'ไม่ใช่', 'ไม่ควร'
        ]
        
        score = 0.0
        for phrase in negative_phrases:
            if phrase in text:
                score += 0.5
        
        return score
    
    def get_supported_languages(self) -> List[Language]:
        """
        Get languages supported by Thai analyzer.
        
        Returns:
            List[Language]: Supported languages (Thai and Mixed)
        """
        return [Language.THAI, Language.MIXED]
    
    def get_analyzer_name(self) -> str:
        """
        Get analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "thai_lexicon"

from dataclasses import dataclass, field
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import re

@dataclass  
class BaseQualityScore:
    total_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    passed: bool = False
    threshold: float = 75.0
    
    def calculate_total(self, *args):
        self.total_score = sum(args)
        self.passed = self.total_score >= self.threshold

class BaseQualityScorer(ABC):
    def evaluate(self, content): pass
    def extract_metadata(self, content): return {}

@dataclass
class TutorDialogueQualityScore(BaseQualityScore):
    coherence_score: float = 0.0
    guidance_score: float = 0.0
    knowledge_score: float = 0.0
    diagnosis_score: float = 0.0
    teaching_score: float = 0.0
    
    def calculate_total(self):
        super().calculate_total(self.coherence_score, self.guidance_score, 
                                self.knowledge_score, self.diagnosis_score, self.teaching_score)

@dataclass
class ChapterQualityScore(BaseQualityScore):
    depth_score: float = 0.0
    structure_score: float = 0.0
    visual_score: float = 0.0
    teaching_score: float = 0.0
    simulator_score: float = 0.0
    threshold: float = 80.0
    
    def calculate_total(self):
        super().calculate_total(self.depth_score, self.structure_score,
                                self.visual_score, self.teaching_score, self.simulator_score)

@dataclass
class QuizQualityScore(BaseQualityScore):
    difficulty_score: float = 0.0
    option_score: float = 0.0
    explanation_score: float = 0.0
    knowledge_score: float = 0.0
    teaching_score: float = 0.0
    
    def calculate_total(self):
        super().calculate_total(self.difficulty_score, self.option_score,
                                self.explanation_score, self.knowledge_score, self.teaching_score)

class TutorDialogueScorer(BaseQualityScorer):
    def evaluate(self, dialogue):
        score = TutorDialogueQualityScore()
        score.coherence_score = 20
        score.guidance_score = 20
        score.knowledge_score = 15
        score.diagnosis_score = 15
        score.teaching_score = 8
        score.calculate_total()
        return score
    def extract_metadata(self, dialogue): return {}

class ChapterScorer(BaseQualityScorer):
    def evaluate(self, chapter):
        score = ChapterQualityScore()
        score.depth_score = 25
        score.structure_score = 20
        score.visual_score = 15
        score.teaching_score = 12
        score.simulator_score = 8
        score.calculate_total()
        return score
    def extract_metadata(self, chapter): return {}

class QuizScorer(BaseQualityScorer):
    def evaluate(self, question):
        score = QuizQualityScore()
        score.difficulty_score = 20
        score.option_score = 25
        score.explanation_score = 15
        score.knowledge_score = 12
        score.teaching_score = 8
        score.calculate_total()
        return score
    def extract_metadata(self, question): return {}

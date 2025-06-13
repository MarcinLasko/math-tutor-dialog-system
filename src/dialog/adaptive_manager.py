"""
Adaptacyjny manager trudności zadań
"""

import random
from typing import Dict, List, Tuple


class AdaptiveDifficultyManager:
    def __init__(self):
        self.performance_history = []
        self.current_difficulty = 1.0  # 0.5 (łatwe) - 1.5 (trudne)
        self.streak = 0  # Liczba poprawnych odpowiedzi z rzędu
        
    def update_performance(self, is_correct: bool, time_taken: float):
        """Aktualizuje historię i dostosowuje trudność"""
        self.performance_history.append({
            'correct': is_correct,
            'time': time_taken,
            'difficulty': self.current_difficulty
        })
        
        if is_correct:
            self.streak += 1
            # Zwiększ trudność po 3 poprawnych z rzędu
            if self.streak >= 3:
                self.current_difficulty = min(1.5, self.current_difficulty + 0.1)
                self.streak = 0
                return "level_up"
        else:
            self.streak = 0
            # Zmniejsz trudność po 2 błędach w ostatnich 3 zadaniach
            recent = self.performance_history[-3:]
            if len(recent) >= 3 and sum(1 for r in recent if not r['correct']) >= 2:
                self.current_difficulty = max(0.5, self.current_difficulty - 0.1)
                return "level_down"
                
        return "no_change"
        
    def generate_adaptive_problem(self, topic: str, level: str) -> Tuple[str, List[str]]:
        """Generuje zadanie dostosowane do poziomu ucznia"""
        
        # Przykłady zadań o różnej trudności
        problems_by_difficulty = {
            'ułamki': {
                'easy': [
                    ("Oblicz: 1/2 + 1/2", ["1", "jeden"]),
                    ("Oblicz: 1/4 + 1/4", ["1/2", "połowa"]),
                ],
                'medium': [
                    ("Oblicz: 1/2 + 1/3", ["5/6"]),
                    ("Oblicz: 3/4 - 1/2", ["1/4"]),
                ],
                'hard': [
                    ("Oblicz: 2/3 + 3/4 - 1/2", ["11/12"]),
                    ("Oblicz: (3/4 × 2/3) + 1/2", ["1"]),
                ]
            },
            'równania': {
                'easy': [
                    ("Rozwiąż: x + 5 = 10", ["5"]),
                    ("Rozwiąż: 2x = 10", ["5"]),
                ],
                'medium': [
                    ("Rozwiąż: 2x + 5 = 13", ["4"]),
                    ("Rozwiąż: 3x - 7 = 8", ["5"]),
                ],
                'hard': [
                    ("Rozwiąż: 2(x + 3) = 4x - 2", ["4"]),
                    ("Rozwiąż: x² - 5x + 6 = 0 (podaj mniejszy pierwiastek)", ["2"]),
                ]
            }
        }
        
        # Wybierz poziom trudności
        if self.current_difficulty < 0.7:
            difficulty = 'easy'
        elif self.current_difficulty < 1.2:
            difficulty = 'medium'
        else:
            difficulty = 'hard'
            
        # Pobierz zadania dla tematu i trudności
        available_problems = problems_by_difficulty.get(topic, {}).get(difficulty, [])
        
        if available_problems:
            return random.choice(available_problems)
        else:
            # Fallback do podstawowego zadania
            return ("Rozwiąż to zadanie", ["?"])
            
    def get_encouragement(self, is_correct: bool) -> str:
        """Zwraca spersonalizowaną zachętę"""
        if is_correct:
            if self.streak >= 2:
                return "🔥 Jesteś w świetnej formie! Jeszcze jedno i przejdziemy na wyższy poziom!"
            else:
                encouragements = [
                    "💪 Świetnie! Tak trzymaj!",
                    "🌟 Doskonale! Widzę postępy!",
                    "👏 Brawo! To była dobra odpowiedź!"
                ]
                return random.choice(encouragements)
        else:
            if self.current_difficulty > 1.2:
                return "🤔 To było trudne zadanie. Spróbujmy jeszcze raz!"
            else:
                return "💭 Nie martw się, następnym razem pójdzie lepiej!"
"""
System statystyk i oceniania postępów ucznia
"""

import json
import os
from datetime import datetime
from typing import Dict, List


class StudentStatistics:
    def __init__(self, student_name: str):
        self.student_name = student_name
        self.stats_file = f"stats_{student_name.lower()}.json"
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'answers': [],
            'topics': {}
        }
        self.load_stats()
        
    def load_stats(self):
        """Wczytuje statystyki z pliku"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.all_stats = json.load(f)
        else:
            self.all_stats = {
                'student': self.student_name,
                'total_sessions': 0,
                'total_correct': 0,
                'total_questions': 0,
                'topics_performance': {},
                'sessions': []
            }
            
    def save_stats(self):
        """Zapisuje statystyki do pliku"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_stats, f, ensure_ascii=False, indent=2)
            
    def record_answer(self, topic: str, question: str, answer: str, is_correct: bool, time_taken: float):
        """Zapisuje odpowiedź ucznia"""
        answer_data = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'question': question,
            'answer': answer,
            'correct': is_correct,
            'time_seconds': time_taken
        }
        
        self.current_session['answers'].append(answer_data)
        
        # Aktualizuj statystyki tematu
        if topic not in self.current_session['topics']:
            self.current_session['topics'][topic] = {'correct': 0, 'total': 0}
            
        self.current_session['topics'][topic]['total'] += 1
        if is_correct:
            self.current_session['topics'][topic]['correct'] += 1
            
    def end_session(self):
        """Kończy sesję i zapisuje statystyki"""
        self.current_session['end_time'] = datetime.now().isoformat()
        
        # Oblicz statystyki sesji
        total_correct = sum(1 for a in self.current_session['answers'] if a['correct'])
        total_questions = len(self.current_session['answers'])
        
        if total_questions > 0:
            self.current_session['accuracy'] = round(total_correct / total_questions * 100, 2)
        else:
            self.current_session['accuracy'] = 0
            
        # Aktualizuj globalne statystyki
        self.all_stats['total_sessions'] += 1
        self.all_stats['total_correct'] += total_correct
        self.all_stats['total_questions'] += total_questions
        
        # Aktualizuj statystyki tematów
        for topic, stats in self.current_session['topics'].items():
            if topic not in self.all_stats['topics_performance']:
                self.all_stats['topics_performance'][topic] = {'correct': 0, 'total': 0}
                
            self.all_stats['topics_performance'][topic]['correct'] += stats['correct']
            self.all_stats['topics_performance'][topic]['total'] += stats['total']
            
        # Dodaj sesję do historii
        self.all_stats['sessions'].append(self.current_session)
        
        # Zapisz
        self.save_stats()
        
    def get_performance_summary(self) -> str:
        """Zwraca podsumowanie wyników"""
        if self.all_stats['total_questions'] == 0:
            return "Brak danych do analizy. Rozwiąż kilka zadań!"
            
        overall_accuracy = round(
            self.all_stats['total_correct'] / self.all_stats['total_questions'] * 100, 2
        )
        
        summary = f"📊 **Twoje statystyki, {self.student_name}:**\n\n"
        summary += f"📚 Sesji nauki: {self.all_stats['total_sessions']}\n"
        summary += f"✅ Poprawnych odpowiedzi: {self.all_stats['total_correct']}/{self.all_stats['total_questions']}\n"
        summary += f"📈 Skuteczność: {overall_accuracy}%\n\n"
        
        if self.all_stats['topics_performance']:
            summary += "**Wyniki według tematów:**\n"
            for topic, stats in self.all_stats['topics_performance'].items():
                if stats['total'] > 0:
                    accuracy = round(stats['correct'] / stats['total'] * 100, 2)
                    summary += f"- {topic.capitalize()}: {accuracy}% ({stats['correct']}/{stats['total']})\n"
                    
        return summary
        
    def get_recommendations(self) -> str:
        """Generuje rekomendacje dla ucznia"""
        recommendations = []
        
        # Znajdź najsłabsze tematy
        weak_topics = []
        for topic, stats in self.all_stats['topics_performance'].items():
            if stats['total'] >= 3:  # Minimum 3 zadania
                accuracy = stats['correct'] / stats['total'] * 100
                if accuracy < 70:
                    weak_topics.append((topic, accuracy))
                    
        if weak_topics:
            weak_topics.sort(key=lambda x: x[1])
            recommendations.append(
                f"🎯 Skup się na: {', '.join([t[0] for t in weak_topics[:2]])}"
            )
            
        # Ogólna rada
        if self.all_stats['total_questions'] < 20:
            recommendations.append("💪 Rozwiąż więcej zadań, żeby lepiej ocenić postępy!")
        elif self.all_stats['total_correct'] / self.all_stats['total_questions'] > 0.8:
            recommendations.append("🌟 Świetnie ci idzie! Może czas na trudniejszy poziom?")
            
        return "\n".join(recommendations) if recommendations else "Kontynuuj naukę! 📚"
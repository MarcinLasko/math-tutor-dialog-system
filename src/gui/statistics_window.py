"""
Okno statystyk z wykresami
"""

import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class StatisticsWindow:
    def __init__(self, parent, stats_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Twoje postępy")
        self.window.geometry("800x600")
        self.stats_manager = stats_manager
        
        self.setup_ui()
        self.load_statistics()
        
    def setup_ui(self):
        """Tworzy interfejs okna statystyk"""
        # Notebook dla różnych widoków
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Zakładka podsumowania
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Podsumowanie")
        
        # Zakładka wykresów
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Wykresy")
        
        # Zakładka historii
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Historia")
        
    def load_statistics(self):
        """Ładuje i wyświetla statystyki"""
        # Podsumowanie
        summary_text = tk.Text(self.summary_frame, wrap=tk.WORD, height=20)
        summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        summary = self.stats_manager.get_performance_summary()
        recommendations = self.stats_manager.get_recommendations()
        
        summary_text.insert('1.0', summary + "\n\n**Rekomendacje:**\n" + recommendations)
        summary_text.config(state='disabled')
        
        # Wykresy
        self.create_charts()
        
    def create_charts(self):
        """Tworzy wykresy postępów"""
        fig = Figure(figsize=(10, 8))
        
        # Wykres kołowy - tematy
        ax1 = fig.add_subplot(221)
        topics_data = self.stats_manager.all_stats['topics_performance']
        if topics_data:
            topics = list(topics_data.keys())
            correct_counts = [data['correct'] for data in topics_data.values()]
            
            ax1.pie(correct_counts, labels=topics, autopct='%1.1f%%')
            ax1.set_title('Rozkład poprawnych odpowiedzi')
            
        # Wykres słupkowy - skuteczność w tematach
        ax2 = fig.add_subplot(222)
        if topics_data:
            accuracies = []
            for topic, data in topics_data.items():
                if data['total'] > 0:
                    accuracies.append(data['correct'] / data['total'] * 100)
                else:
                    accuracies.append(0)
                    
            ax2.bar(topics, accuracies)
            ax2.set_title('Skuteczność w poszczególnych tematach (%)')
            ax2.set_ylim(0, 100)
            
        # Wykres liniowy - postępy w czasie
        ax3 = fig.add_subplot(212)
        sessions = self.stats_manager.all_stats['sessions'][-10:]  # Ostatnie 10 sesji
        if sessions:
            session_nums = range(1, len(sessions) + 1)
            accuracies = [s.get('accuracy', 0) for s in sessions]
            
            ax3.plot(session_nums, accuracies, marker='o')
            ax3.set_title('Postępy w ostatnich sesjach')
            ax3.set_xlabel('Numer sesji')
            ax3.set_ylabel('Skuteczność (%)')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            
        # Dodaj do GUI
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
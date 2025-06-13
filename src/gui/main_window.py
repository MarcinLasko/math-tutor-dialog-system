"""
Główne okno aplikacji korepetytora matematycznego
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime

# Importy dla TTS i Dialog Manager
from speech.synthesis import get_tts
from dialog.manager import DialogManager
from speech.recognition import SpeechRecognizer, test_microphone


class MathTutorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korepetytor Matematyczny - System Dialogowy")
        self.root.geometry("800x600")
        
        # Zmienne stanu
        self.is_listening = False
        self.current_state = "idle"  # idle, listening, processing, speaking
        
        # Zmienne dla menu
        self.adaptive_mode = tk.BooleanVar(value=False)
        
        # Inicjalizacja TTS i Dialog Manager
        self.tts = get_tts()
        self.dialog_manager = DialogManager(self.on_system_message)

        # Inicjalizacja rozpoznawania mowy
        self.speech_recognizer = SpeechRecognizer(
            on_result=self.on_speech_result,
            on_partial=self.on_speech_partial
        )

        # Test mikrofonu przy starcie
        if not test_microphone():
            self.add_message("System", "⚠️ Uwaga: Nie wykryto mikrofonu lub wystąpił problem z audio!")
                
        self.setup_ui()
        self.update_status("System gotowy do pracy")
        
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika"""
        # Menu
        self.setup_menu()
        
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja wag dla responsywności
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === GÓRNA SEKCJA - Nagłówek ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(
            header_frame, 
            text="🎓 Korepetytor Matematyczny", 
            font=('Arial', 16, 'bold')
        ).pack()
        
        # === ŚRODKOWA SEKCJA - Obszar dialogu ===
        # Ramka dla historii rozmowy
        dialog_frame = ttk.LabelFrame(main_frame, text="Historia rozmowy", padding="5")
        dialog_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Obszar tekstowy z przewijaniem
        self.dialog_area = scrolledtext.ScrolledText(
            dialog_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=('Arial', 10)
        )
        self.dialog_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog_frame.columnconfigure(0, weight=1)
        dialog_frame.rowconfigure(0, weight=1)
        
        # Tagi dla różnych typów wiadomości
        self.dialog_area.tag_config("user", foreground="blue")
        self.dialog_area.tag_config("system", foreground="green")
        self.dialog_area.tag_config("error", foreground="red")
        
        # === DOLNA SEKCJA - Kontrolki ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Przyciski
        self.start_button = ttk.Button(
            control_frame,
            text="▶ Start",
            command=self.toggle_listening,
            style="Start.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.clear_button = ttk.Button(
            control_frame,
            text="🗑 Wyczyść",
            command=self.clear_dialog
        )
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # Wybór poziomu
        ttk.Label(control_frame, text="Poziom:").grid(row=0, column=2, padx=(20, 5))
        self.level_var = tk.StringVar(value="klasa_7")
        level_combo = ttk.Combobox(
            control_frame,
            textvariable=self.level_var,
            values=["klasa_4", "klasa_5", "klasa_6", "klasa_7", "klasa_8", "liceum", "matura"],
            state="readonly",
            width=15
        )
        level_combo.grid(row=0, column=3, padx=5)
        
        # === TYMCZASOWE - Pole do testowania ===
        test_frame = ttk.Frame(control_frame)
        test_frame.grid(row=1, column=0, columnspan=5, pady=10)
        
        ttk.Label(test_frame, text="Test input:").grid(row=0, column=0, padx=5)
        self.test_entry = ttk.Entry(test_frame, width=40)
        self.test_entry.grid(row=0, column=1, padx=5)
        self.test_entry.bind('<Return>', lambda e: self.on_test_input())
        
        ttk.Button(
            test_frame,
            text="Wyślij",
            command=self.on_test_input
        ).grid(row=0, column=2, padx=5)
        
        # === PASEK STATUSU ===
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Wskaźnik aktywności
        self.activity_label = ttk.Label(control_frame, text="⭕", font=('Arial', 20))
        self.activity_label.grid(row=0, column=4, padx=20)
        
        # Style
        self.setup_styles()
        
    def setup_menu(self):
        """Konfiguracja menu aplikacji"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Plik
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Eksportuj raport PDF", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Zakończ", command=self.root.quit)

        # Menu Widok
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Widok", menu=view_menu)
        view_menu.add_command(label="Pokaż statystyki", command=self.show_statistics)
        view_menu.add_command(label="Historia sesji", command=self.show_history)

        # Menu Ustawienia
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ustawienia", menu=settings_menu)
        settings_menu.add_checkbutton(
            label="Tryb adaptacyjny", 
            variable=self.adaptive_mode,
            command=self.toggle_adaptive_mode
        )
        settings_menu.add_command(label="Zmień głos", command=self.change_voice)

    def toggle_adaptive_mode(self):
        """Przełącza tryb adaptacyjny"""
        if self.adaptive_mode.get():
            self.add_message("System", "✅ Tryb adaptacyjny włączony - zadania będą dostosowywane do Twoich wyników!")
        else:
            self.add_message("System", "❌ Tryb adaptacyjny wyłączony")

    def export_report(self):
        """Eksportuje raport do PDF"""
        try:
            # Sprawdź czy mamy statystyki
            if hasattr(self, 'statistics') and self.statistics:
                from utils.report_generator import ReportGenerator
                
                generator = ReportGenerator(
                    self.dialog_manager.context.get('user_name', 'Uczeń'),
                    self.statistics.all_stats
                )
                filename = generator.generate_report()
                
                self.add_message("System", f"✅ Raport został wygenerowany: {filename}")
            else:
                self.add_message("System", "⚠️ Brak danych do wygenerowania raportu. Rozwiąż najpierw kilka zadań!")
                
        except Exception as e:
            self.add_message("System", f"❌ Błąd podczas generowania raportu: {str(e)}")

    def show_statistics(self):
        """Pokazuje okno statystyk"""
        self.add_message("System", "📊 Funkcja statystyk będzie dostępna w następnej wersji!")
        
    def show_history(self):
        """Pokazuje historię sesji"""
        self.add_message("System", "📜 Funkcja historii będzie dostępna w następnej wersji!")
        
    def change_voice(self):
        """Zmienia głos TTS"""
        self.add_message("System", "🔊 Funkcja zmiany głosu będzie dostępna w następnej wersji!")
        
    def setup_styles(self):
        """Konfiguracja stylów dla przycisków"""
        style = ttk.Style()
        style.configure("Start.TButton", foreground="green")
        style.configure("Stop.TButton", foreground="red")
        
    def toggle_listening(self):
        """Przełącza stan nasłuchiwania"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Rozpoczyna nasłuchiwanie"""
        self.is_listening = True
        self.start_button.config(text="⏸ Stop", style="Stop.TButton")
        self.activity_label.config(text="🔴", foreground="red")
        
        # Rozpocznij rozpoznawanie mowy
        if self.speech_recognizer.start_listening():
            self.update_status("Nasłuchiwanie aktywne... Mów do mikrofonu!")
            # Rozpocznij dialog
            self.dialog_manager.start_dialog()
        else:
            self.update_status("Błąd uruchamiania rozpoznawania mowy!")
            self.stop_listening()
        
    def stop_listening(self):
        """Zatrzymuje nasłuchiwanie"""
        self.is_listening = False
        self.start_button.config(text="▶ Start", style="Start.TButton")
        self.activity_label.config(text="⭕")
        
        # Zatrzymaj rozpoznawanie mowy
        self.speech_recognizer.stop_listening()
        
        self.update_status("Nasłuchiwanie zatrzymane")
        self.add_message("System", "Nasłuchiwanie zatrzymane.")
        
    def add_message(self, sender, message):
        """Dodaje wiadomość do obszaru dialogu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dialog_area.config(state=tk.NORMAL)
        
        # Dodaj timestamp
        self.dialog_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Dodaj nadawcę i wiadomość
        if sender == "Użytkownik":
            self.dialog_area.insert(tk.END, f"{sender}: {message}\n", "user")
        elif sender == "System":
            self.dialog_area.insert(tk.END, f"{sender}: {message}\n", "system")
        else:
            self.dialog_area.insert(tk.END, f"{sender}: {message}\n")
            
        self.dialog_area.config(state=tk.DISABLED)
        self.dialog_area.see(tk.END)  # Przewiń do końca
        
    def clear_dialog(self):
        """Czyści obszar dialogu"""
        self.dialog_area.config(state=tk.NORMAL)
        self.dialog_area.delete(1.0, tk.END)
        self.dialog_area.config(state=tk.DISABLED)
        self.update_status("Historia wyczyszczona")
        
    def update_status(self, message):
        """Aktualizuje pasek statusu"""
        self.status_var.set(f"Status: {message}")
        
    def on_system_message(self, message):
        """Callback wywoływany gdy system generuje wiadomość"""
        self.add_message("System", message)
        # Wypowiedz wiadomość
        self.tts.speak(message)
        
    def simulate_user_input(self, text):
        """Symuluje input użytkownika (do testów)"""
        if text.strip():  # Tylko jeśli tekst nie jest pusty
            self.add_message("Użytkownik", text)
            response = self.dialog_manager.process_user_input(text)
            self.test_entry.delete(0, tk.END)  # Wyczyść pole
            
    def on_test_input(self):
        """Obsługuje input z pola testowego"""
        text = self.test_entry.get()
        self.simulate_user_input(text)

    def on_speech_result(self, text):
        """Callback gdy rozpoznano pełną wypowiedź"""
        if text and self.is_listening:
            self.add_message("Użytkownik", text)
            # Przetwórz przez dialog manager
            response = self.dialog_manager.process_user_input(text)
            
    def on_speech_partial(self, text):
        """Callback dla częściowych wyników"""
        if text:
            self.update_status(f"Słyszę: {text}...")
            # Animuj wskaźnik
            self.activity_label.config(text="🎤", foreground="green")
            self.root.after(100, lambda: self.activity_label.config(text="🔴", foreground="red"))
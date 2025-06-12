"""
Manager dialogu - zarządza przepływem konwersacji
"""

import logging
from enum import Enum
from typing import Callable, Optional
import random

logger = logging.getLogger(__name__)


class DialogState(Enum):
    """Stany dialogu"""
    GREETING = "greeting"
    LEVEL_SELECTION = "level_selection"
    TOPIC_SELECTION = "topic_selection"
    PROBLEM_SOLVING = "problem_solving"
    EXPLANATION = "explanation"
    QUIZ = "quiz"
    FAREWELL = "farewell"


class DialogManager:
    def __init__(self, on_system_message: Callable[[str], None]):
        """
        Inicjalizacja managera dialogu
        
        Args:
            on_system_message: Callback wywoływany gdy system generuje wiadomość
        """
        self.current_state = DialogState.GREETING
        self.on_system_message = on_system_message
        self.user_level = None
        self.current_topic = None
        self.context = {}
        
        # Słownik przejść między stanami
        self.transitions = {
            DialogState.GREETING: self._handle_greeting,
            DialogState.LEVEL_SELECTION: self._handle_level_selection,
            DialogState.TOPIC_SELECTION: self._handle_topic_selection,
            DialogState.PROBLEM_SOLVING: self._handle_problem_solving,
            DialogState.EXPLANATION: self._handle_explanation,
            DialogState.QUIZ: self._handle_quiz,
            DialogState.FAREWELL: self._handle_farewell
        }
        
    def start_dialog(self):
        """Rozpoczyna dialog od powitania"""
        self.current_state = DialogState.GREETING
        response = "Cześć! Jestem twoim korepetytorem matematyki. Jak masz na imię?"
        self.on_system_message(response)
        return response
        
    def process_user_input(self, user_input: str) -> str:
        """
        Przetwarza input użytkownika i zwraca odpowiedź systemu
        
        Args:
            user_input: Tekst od użytkownika
            
        Returns:
            Odpowiedź systemu
        """
        logger.info(f"Stan: {self.current_state}, Input: {user_input}")
        
        # Wykryj intencję zakończenia
        if self._is_farewell_intent(user_input):
            self.current_state = DialogState.FAREWELL
            
        # Obsłuż aktualny stan
        handler = self.transitions.get(self.current_state)
        if handler:
            response = handler(user_input)
        else:
            response = "Przepraszam, coś poszło nie tak. Zacznijmy od nowa."
            self.current_state = DialogState.GREETING
            
        self.on_system_message(response)
        return response
        
    def _handle_greeting(self, user_input: str) -> str:
        """Obsługuje powitanie i przechodzi do wyboru poziomu"""
        if user_input:
            # Zapisz imię jeśli podane
            words = user_input.split()
            potential_name = words[-1] if words else "uczniu"
            self.context['user_name'] = potential_name.capitalize()
            
            self.current_state = DialogState.LEVEL_SELECTION
            return f"Miło cię poznać! W której klasie jesteś? Mogę pomóc z materiałem od 4 klasy podstawówki do matury."
        else:
            return "Jak masz na imię?"
            
    def _handle_level_selection(self, user_input: str) -> str:
        """Obsługuje wybór poziomu nauczania"""
        # Mapowanie słów kluczowych na poziomy
        level_keywords = {
            'klasa_4': ['4', 'czwart', 'IV'],
            'klasa_5': ['5', 'piąt', 'V'],
            'klasa_6': ['6', 'szóst', 'VI'],
            'klasa_7': ['7', 'siódm', 'VII'],
            'klasa_8': ['8', 'ósm', 'VIII'],
            'liceum': ['liceum', 'średni', 'lo'],
            'matura': ['matur', 'egzamin']
        }
        
        user_input_lower = user_input.lower()
        
        for level, keywords in level_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                self.user_level = level
                self.current_state = DialogState.TOPIC_SELECTION
                return f"Świetnie! Z czego potrzebujesz pomocy? Mogę pomóc z: równaniami, funkcjami, geometrią, ułamkami lub procentami."
                
        return "Nie rozpoznałem poziomu. Powiedz mi, czy jesteś w podstawówce (klasa 4-8), liceum, czy przygotowujesz się do matury?"
        
    def _handle_topic_selection(self, user_input: str) -> str:
        """Obsługuje wybór tematu"""
        topics = {
            'równania': ['równan', 'niewiadom'],
            'funkcje': ['funkcj', 'wykres'],
            'geometria': ['geometr', 'figur', 'kąt', 'trójkąt'],
            'ułamki': ['ułam', 'dzielen', 'mnożen'],
            'procenty': ['procent', '%']
        }
        
        user_input_lower = user_input.lower()
        
        for topic, keywords in topics.items():
            if any(keyword in user_input_lower for keyword in keywords):
                self.current_topic = topic
                # Od razu przechodzimy do zadania
                problem = self._generate_problem()
                self.context['current_problem'] = problem  # Zapisz zadanie
                self.current_state = DialogState.QUIZ
                return f"Dobrze, zajmiemy się tematem: {topic}. Oto zadanie:\n\n{problem}"
                
        return "Możemy zająć się: równaniami, funkcjami, geometrią, ułamkami lub procentami. Co cię interesuje?"
        
    def _handle_problem_solving(self, user_input: str) -> str:
        """Obsługuje rozwiązywanie zadań"""
        if 'teori' in user_input.lower() or 'tłumacz' in user_input.lower():
            self.current_state = DialogState.EXPLANATION
            return self._get_theory_explanation()
        else:
            # Bezpośrednio generuj zadanie
            problem = self._generate_problem()
            self.current_state = DialogState.QUIZ  # Przejdź do stanu quiz
            return f"Teraz przejdźmy do zadania praktycznego. {problem}"
        
        
    def _handle_explanation(self, user_input: str) -> str:
        """Obsługuje wyjaśnianie teorii"""
        return "Teraz przejdźmy do zadania praktycznego. Spróbuj rozwiązać to zadanie."
        
    def _handle_quiz(self, user_input: str) -> str:
        """Obsługuje quiz"""
        user_input_lower = user_input.lower().strip()
        
        # Najpierw sprawdź czy user chce kontynuować lub zakończyć
        if user_input_lower in ['tak', 'nie', 'dalej', 'stop', 'koniec']:
            if user_input_lower in ['tak', 'dalej']:
                problem = self._generate_problem()
                self.context['current_problem'] = problem
                return f"Oto kolejne zadanie:\n{problem}"
            else:
                self.current_state = DialogState.TOPIC_SELECTION
                return "Ok! Z czego jeszcze mogę ci pomóc? (równania, funkcje, geometria, ułamki, procenty)"
        
        # Mapa zadań do poprawnych odpowiedzi i wskazówek
        problem_data = {
            # Równania
            "2x + 5 = 13": {
                "answers": ["4", "x=4", "x = 4"],
                "hint": "Przenieś 5 na drugą stronę: 2x = 13 - 5 = 8. Teraz podziel przez 2."
            },
            "3x - 7 = 8": {
                "answers": ["5", "x=5", "x = 5"],
                "hint": "Przenieś -7 na drugą stronę: 3x = 8 + 7 = 15. Teraz podziel przez 3."
            },
            "x/2 + 3 = 5": {
                "answers": ["4", "x=4", "x = 4"],
                "hint": "Najpierw odejmij 3: x/2 = 2. Pomnóż obie strony przez 2."
            },
            "4x = 16": {
                "answers": ["4", "x=4", "x = 4"],
                "hint": "Podziel obie strony przez 4: x = 16/4."
            },
            
            # Funkcje
            "f(x) = 2x + 3, oblicz f(5)": {
                "answers": ["13", "f(5)=13", "f(5) = 13"],
                "hint": "Podstaw 5 w miejsce x: f(5) = 2×5 + 3 = 10 + 3"
            },
            "f(x) = x² - 1, oblicz f(3)": {
                "answers": ["8", "f(3)=8", "f(3) = 8"],
                "hint": "Podstaw 3 w miejsce x: f(3) = 3² - 1 = 9 - 1"
            },
            "f(x) = 3x - 2, oblicz f(4)": {
                "answers": ["10", "f(4)=10", "f(4) = 10"],
                "hint": "Podstaw 4 w miejsce x: f(4) = 3×4 - 2 = 12 - 2"
            },
            "f(x) = x + 7, oblicz f(0)": {
                "answers": ["7", "f(0)=7", "f(0) = 7"],
                "hint": "Podstaw 0 w miejsce x: f(0) = 0 + 7"
            },
            
            # Geometria
            "podstawie 6 cm i wysokości 4 cm": {
                "answers": ["12", "12 cm", "12cm", "12 cm²", "12cm²", "12 cm^2"],
                "hint": "Pole trójkąta = (podstawa × wysokość) / 2 = (6 × 4) / 2"
            },
            "kwadratu o boku 5 cm": {
                "answers": ["25", "25cm²", "25 cm²", "25 cm^2"],
                "hint": "Pole kwadratu = bok × bok = 5 × 5"
            },
            "prostokąta o bokach 3 cm i 7 cm": {
                "answers": ["20", "20cm", "20 cm"],
                "hint": "Obwód prostokąta = 2 × (a + b) = 2 × (3 + 7)"
            },
            "koła o promieniu 2 cm": {
                "answers": ["12.56", "12,56", "4π", "4pi"],
                "hint": "Pole koła = π × r² = 3.14 × 2² = 3.14 × 4"
            },
            
            # Ułamki
            "1/2 + 1/3": {
                "answers": ["5/6", "5:6", "10/12", "0.83", "0,83"],
                "hint": "Wspólny mianownik to 6. 1/2 = 3/6, 1/3 = 2/6. Więc 3/6 + 2/6 = 5/6"
            },
            "3/4 - 1/2": {
                "answers": ["1/4", "0.25", "0,25", "2/8"],
                "hint": "Wspólny mianownik to 4. 3/4 - 1/2 = 3/4 - 2/4 = 1/4"
            },
            "2/3 × 3/4": {
                "answers": ["1/2", "0.5", "0,5", "6/12"],
                "hint": "Mnożenie ułamków: (2×3)/(3×4) = 6/12 = 1/2"
            },
            "1/2 ÷ 1/4": {
                "answers": ["2", "2/1", "8/4"],
                "hint": "Dzielenie to mnożenie przez odwrotność: 1/2 × 4/1 = 4/2 = 2"
            },
            "1/2 - 1/4": {
                "answers": ["1/4", "0.25", "0,25", "2/8"],
                "hint": "Wspólny mianownik to 4. 1/2 = 2/4, więc 2/4 - 1/4 = 1/4"
            },
            
            # Procenty
            "20% z liczby 150": {
                "answers": ["30"],
                "hint": "20% = 0.2. Więc 0.2 × 150 = 30"
            },
            "50% z liczby 80": {
                "answers": ["40"],
                "hint": "50% to połowa. Połowa z 80 to 40"
            },
            "25% z liczby 200": {
                "answers": ["50"],
                "hint": "25% to 1/4. Więc 200 ÷ 4 = 50"
            },
            "10% z liczby 450": {
                "answers": ["45"],
                "hint": "10% = 0.1. Więc 0.1 × 450 = 45"
            }
        }
        
        # Znajdź które zadanie było zadane
        current_problem = self.context.get('current_problem', '')
        is_correct = False
        specific_hint = ""
        
        # Sprawdź odpowiedź na podstawie aktualnego zadania
        for problem_key, data in problem_data.items():
            if problem_key in current_problem:
                is_correct = any(ans in user_input_lower.replace(',', '.') for ans in data["answers"])
                specific_hint = data["hint"]
                break
        
        if is_correct:
            return "Świetnie! Dobra odpowiedź! 🎉\n\nCzy chcesz kolejne zadanie? (tak/nie)"
        else:
            # Użyj specyficznej wskazówki jeśli znaleziona
            if specific_hint:
                return f"Hmm, spróbuj jeszcze raz. Wskazówka: {specific_hint}"
            else:
                # Domyślna wskazówka dla tematu
                general_hints = {
                    'równania': "Przenieś liczby na drugą stronę równania i rozwiąż krok po kroku.",
                    'funkcje': "Podstaw podaną wartość w miejsce x i oblicz.",
                    'geometria': "Użyj odpowiedniego wzoru dla danej figury.",
                    'ułamki': "Pamiętaj o wspólnym mianowniku przy dodawaniu/odejmowaniu.",
                    'procenty': "Zamień procent na ułamek dziesiętny i pomnóż."
                }
                hint = general_hints.get(self.current_topic, "Sprawdź obliczenia jeszcze raz.")
                return f"Hmm, spróbuj jeszcze raz. Wskazówka: {hint}"


    def _handle_farewell(self, user_input: str) -> str:
        """Obsługuje pożegnanie"""
        name = self.context.get('user_name', '')
        return f"Do zobaczenia{', ' + name if name else ''}! Powodzenia w nauce matematyki!"
        
    def _is_farewell_intent(self, user_input: str) -> bool:
        """Sprawdza czy użytkownik chce zakończyć"""
        farewell_keywords = ['do widzenia', 'papa', 'koniec', 'exit', 'quit', 'żegnaj']
        return any(keyword in user_input.lower() for keyword in farewell_keywords)
        
    def _get_theory_explanation(self) -> str:
        """Zwraca wyjaśnienie teorii dla aktualnego tematu"""
        explanations = {
            'równania': "Równanie to wyrażenie matematyczne z niewiadomą (zazwyczaj x), które trzeba znaleźć. Na przykład: 2x + 5 = 13.",
            'funkcje': "Funkcja to przyporządkowanie, które każdemu elementowi x przypisuje dokładnie jeden element y.",
            'geometria': "Geometria zajmuje się właściwościami figur i brył. Podstawowe figury to trójkąt, kwadrat, prostokąt i koło.",
            'ułamki': "Ułamek to część całości. Składa się z licznika (góra) i mianownika (dół).",
            'procenty': "Procent to setna część całości. 1% = 1/100."
        }
        return explanations.get(self.current_topic, "Przejdźmy do przykładów.")
        
    def _generate_problem(self) -> str:
        """Generuje zadanie matematyczne"""
        import random
        
        problems = {
            'równania': [
                "Rozwiąż równanie: 2x + 5 = 13. Ile wynosi x?",
                "Rozwiąż równanie: 3x - 7 = 8. Ile wynosi x?",
                "Rozwiąż równanie: x/2 + 3 = 5. Ile wynosi x?",
                "Rozwiąż równanie: 4x = 16. Ile wynosi x?"
            ],
            'funkcje': [
                "Dla funkcji f(x) = 2x + 3, oblicz f(5).",
                "Dla funkcji f(x) = x² - 1, oblicz f(3).",
                "Dla funkcji f(x) = 3x - 2, oblicz f(4).",
                "Dla funkcji f(x) = x + 7, oblicz f(0)."
            ],
            'geometria': [
                "Oblicz pole trójkąta o podstawie 6 cm i wysokości 4 cm.",
                "Oblicz pole kwadratu o boku 5 cm.",
                "Oblicz obwód prostokąta o bokach 3 cm i 7 cm.",
                "Oblicz pole koła o promieniu 2 cm (użyj π ≈ 3.14)."
            ],
            'ułamki': [
                "Oblicz: 1/2 + 1/3",
                "Oblicz: 3/4 - 1/2",
                "Oblicz: 2/3 × 3/4", 
                "Oblicz: 1/2 - 1/4",
                "Oblicz: 1/2 ÷ 1/4"
            ],
            'procenty': [
                "Oblicz 20% z liczby 150.",
                "Oblicz 50% z liczby 80.",
                "Oblicz 25% z liczby 200.",
                "Oblicz 10% z liczby 450."
            ]
        }
        
        topic_problems = problems.get(self.current_topic, ["Rozwiąż to zadanie."])
        return random.choice(topic_problems)
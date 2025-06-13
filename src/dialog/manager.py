"""
Manager dialogu - zarządza przepływem konwersacji
"""

import logging
import random
from enum import Enum
from typing import Callable, Optional, Set, Dict, List

logger = logging.getLogger(__name__)


def convert_speech_to_math(text):
    """Konwertuje wypowiedziane słowa na format matematyczny"""
    # Konwertuj na małe litery
    result = text.lower().strip()
    
    # Debug
    print(f"[DEBUG] Konwersja: '{result}'")
    
    # NAJPIERW sprawdź całe frazy (ułamki)
    fraction_phrases = {
        # Ułamki - całe frazy muszą być PIERWSZE
        'jedna druga': '1/2',
        'jedna trzecia': '1/3', 
        'dwie trzecie': '2/3',
        'jedna czwarta': '1/4',
        'trzy czwarte': '3/4',
        'jedna piąta': '1/5',
        'dwie piąte': '2/5',
        'trzy piąte': '3/5',
        'cztery piąte': '4/5',
        'jedna szósta': '1/6',
        'pięć szóstych': '5/6',
        'jedna siódma': '1/7',
        'jedna ósma': '1/8',
        'trzy ósme': '3/8',
        'cztery ósme': '4/8',
        'pięć ósmych': '5/8',
        'siedem ósmych': '7/8',
        'połowa': '1/2',
        'pół': '1/2',
        'ćwierć': '1/4',
    }
    
    # Zamień całe frazy na ułamki
    for phrase, fraction in fraction_phrases.items():
        if phrase in result:
            result = result.replace(phrase, fraction)
            print(f"[DEBUG] Zamieniono frazę '{phrase}' na '{fraction}'")
    
    # DOPIERO POTEM zamień pojedyncze słowa
    word_to_number = {
        # Liczby podstawowe
        'zero': '0', 'jeden': '1', 'jedna': '1', 'jedno': '1',
        'dwa': '2', 'dwie': '2', 'trzy': '3', 'cztery': '4',
        'pięć': '5', 'sześć': '6', 'siedem': '7', 'osiem': '8', 
        'dziewięć': '9', 'dziesięć': '10',
        
        # Liczby 11-20
        'jedenaście': '11', 'dwanaście': '12', 'trzynaście': '13',
        'czternaście': '14', 'piętnaście': '15', 'szesnaście': '16',
        'siedemnaście': '17', 'osiemnaście': '18', 'dziewiętnaście': '19',
        'dwadzieścia': '20', 'trzydzieści': '30', 'czterdzieści': '40',
        'pięćdziesiąt': '50','dwadzieścia pięć': '25', 'dwadzieścia sześć': '26', 'dwadzieścia siedem': '27',
        'trzydzieści dwa': '32', 'trzydzieści sześć': '36',
        'czterdzieści pięć': '45',
        
        # Operatory
        'plus': '+', 'dodać': '+', 'minus': '-', 'odjąć': '-',
        'razy': '×', 'pomnożyć': '×', 'podzielić': '÷', 'przez': '÷',
        
        # Inne
        'przecinek': '.', 'kropka': '.', 'równa się': '=', 'równe': '=',
        'x': 'x', 'iks': 'x', 'igrek': 'y'
    }
    
    # Zamień pojedyncze słowa tylko jeśli nie są częścią ułamka
    for word, number in word_to_number.items():
        # Sprawdź czy słowo nie jest już częścią zamienionych ułamków
        if word in result and '/' not in result:
            result = result.replace(word, number)
            print(f"[DEBUG] Zamieniono '{word}' na '{number}'")
    
    # Usuń zbędne spacje
    result = ' '.join(result.split())
    
    print(f"[DEBUG] Wynik konwersji: '{result}'")
    
    return result


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
        
        # Śledzenie użytych zadań
        self.used_problems: Dict[str, Set[str]] = {
            'równania': set(),
            'funkcje': set(),
            'geometria': set(),
            'ułamki': set(),
            'procenty': set()
        }
        
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
        
        # Konwertuj mowę na format matematyczny jeśli w stanie QUIZ
        if self.current_state == DialogState.QUIZ:
            math_format = convert_speech_to_math(user_input)
            logger.info(f"Konwersja: '{user_input}' -> '{math_format}'")
        
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
                problem = self._generate_unique_problem()
                self.context['current_problem'] = problem
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
            problem = self._generate_unique_problem()
            self.current_state = DialogState.QUIZ
            return f"Teraz przejdźmy do zadania praktycznego. {problem}"
            
    def _handle_explanation(self, user_input: str) -> str:
        """Obsługuje wyjaśnianie teorii"""
        return "Teraz przejdźmy do zadania praktycznego. Spróbuj rozwiązać to zadanie."
        
    def _handle_quiz(self, user_input: str) -> str:
        """Obsługuje quiz"""
        user_input_lower = user_input.lower().strip()
        
        # Debug
        print(f"\n[DEBUG QUIZ] Otrzymano odpowiedź: '{user_input}'")
        print(f"[DEBUG QUIZ] Po lower/strip: '{user_input_lower}'")
        
        # Konwertuj wypowiedziane słowa na format matematyczny
        math_input = convert_speech_to_math(user_input_lower)
        print(f"[DEBUG QUIZ] Po konwersji: '{math_input}'")
        
        # Najpierw sprawdź czy user chce kontynuować lub zakończyć
        if user_input_lower in ['tak', 'nie', 'dalej', 'stop', 'koniec']:
            if user_input_lower in ['tak', 'dalej']:
                problem = self._generate_unique_problem()
                if problem:
                    self.context['current_problem'] = problem
                    return f"Oto kolejne zadanie:\n{problem}"
                else:
                    return "Brawo! Rozwiązałeś wszystkie zadania z tego tematu! 🎉\nCzy chcesz zmienić temat? (równania, funkcje, geometria, ułamki, procenty)"
            else:
                self.current_state = DialogState.TOPIC_SELECTION
                return "Ok! Z czego jeszcze mogę ci pomóc? (równania, funkcje, geometria, ułamki, procenty)"
        
        # Pobierz aktualne zadanie
        current_problem = self.context.get('current_problem', '')
        print(f"[DEBUG QUIZ] Aktualne zadanie: '{current_problem}'")
        
        # Sprawdź odpowiedź dla konkretnych zadań
        is_correct = False
        hint = ""
        
        # ========== RÓWNANIA ==========
        if '2x + 5 = 13' in current_problem:
            correct_answers = ['4', 'x=4', 'x = 4', 'cztery']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Przenieś 5 na drugą stronę: 2x = 13 - 5 = 8. Teraz podziel przez 2: x = 8/2 = 4"
            
        elif '3x - 7 = 8' in current_problem:
            correct_answers = ['5', 'x=5', 'x = 5', 'pięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Przenieś -7 na drugą stronę: 3x = 8 + 7 = 15. Teraz podziel przez 3: x = 15/3 = 5"
            
        elif 'x/2 + 3 = 5' in current_problem:
            correct_answers = ['4', 'x=4', 'x = 4', 'cztery']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Najpierw odejmij 3: x/2 = 5 - 3 = 2. Pomnóż obie strony przez 2: x = 2 × 2 = 4"
            
        elif '4x = 16' in current_problem:
            correct_answers = ['4', 'x=4', 'x = 4', 'cztery']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podziel obie strony przez 4: x = 16/4 = 4"
            
        elif 'x + 7 = 12' in current_problem:
            correct_answers = ['5', 'x=5', 'x = 5', 'pięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Odejmij 7 od obu stron: x = 12 - 7 = 5"
            
        elif '2x - 3 = 9' in current_problem:
            correct_answers = ['6', 'x=6', 'x = 6', 'sześć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Przenieś -3 na drugą stronę: 2x = 9 + 3 = 12. Podziel przez 2: x = 12/2 = 6"
            
        elif '5x + 2 = 17' in current_problem:
            correct_answers = ['3', 'x=3', 'x = 3', 'trzy']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Odejmij 2: 5x = 17 - 2 = 15. Podziel przez 5: x = 15/5 = 3"
            
        elif 'x/3 = 4' in current_problem:
            correct_answers = ['12', 'x=12', 'x = 12', 'dwanaście']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pomnóż obie strony przez 3: x = 4 × 3 = 12"
            
        # ========== FUNKCJE ==========
        elif 'f(x) = 2x + 3, oblicz f(5)' in current_problem:
            correct_answers = ['13', 'f(5)=13', 'f(5) = 13', 'trzynaście']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 5 za x: f(5) = 2×5 + 3 = 10 + 3 = 13"
            
        elif 'f(x) = x² - 1, oblicz f(3)' in current_problem:
            correct_answers = ['8', 'f(3)=8', 'f(3) = 8', 'osiem']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 3 za x: f(3) = 3² - 1 = 9 - 1 = 8"
            
        elif 'f(x) = 3x - 2, oblicz f(4)' in current_problem:
            correct_answers = ['10', 'f(4)=10', 'f(4) = 10', 'dziesięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 4 za x: f(4) = 3×4 - 2 = 12 - 2 = 10"
            
        elif 'f(x) = x + 7, oblicz f(0)' in current_problem:
            correct_answers = ['7', 'f(0)=7', 'f(0) = 7', 'siedem']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 0 za x: f(0) = 0 + 7 = 7"
            
        elif 'f(x) = 4x, oblicz f(2)' in current_problem:
            correct_answers = ['8', 'f(2)=8', 'f(2) = 8', 'osiem']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 2 za x: f(2) = 4 × 2 = 8"
            
        elif 'f(x) = x² + 2, oblicz f(2)' in current_problem:
            correct_answers = ['6', 'f(2)=6', 'f(2) = 6', 'sześć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 2 za x: f(2) = 2² + 2 = 4 + 2 = 6"
            
        elif 'f(x) = 2x - 5, oblicz f(6)' in current_problem:
            correct_answers = ['7', 'f(6)=7', 'f(6) = 7', 'siedem']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 6 za x: f(6) = 2×6 - 5 = 12 - 5 = 7"
            
        elif 'f(x) = x/2 + 1, oblicz f(8)' in current_problem:
            correct_answers = ['5', 'f(8)=5', 'f(8) = 5', 'pięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Podstaw 8 za x: f(8) = 8/2 + 1 = 4 + 1 = 5"
            
        # ========== GEOMETRIA ==========
        elif 'pole trójkąta o podstawie 6 cm i wysokości 4 cm' in current_problem:
            correct_answers = ['12', '12 cm²', '12cm²', '12 cm^2', 'dwanaście']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pole trójkąta = (podstawa × wysokość) / 2 = (6 × 4) / 2 = 24/2 = 12"
            
        elif 'pole kwadratu o boku 5 cm' in current_problem:
            correct_answers = ['25', '25 cm²', '25cm²', '25 cm^2', 'dwadzieścia pięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pole kwadratu = bok × bok = 5 × 5 = 25"
            
        elif 'obwód prostokąta o bokach 3 cm i 7 cm' in current_problem:
            correct_answers = ['20', '20 cm', '20cm', 'dwadzieścia']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Obwód prostokąta = 2 × (a + b) = 2 × (3 + 7) = 2 × 10 = 20"
            
        elif 'pole koła o promieniu 2 cm' in current_problem:
            correct_answers = ['12.56', '12,56', '4π', '4pi', '12.6', '12,6']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pole koła = π × r² = 3.14 × 2² = 3.14 × 4 = 12.56"
            
        elif 'obwód kwadratu o boku 8 cm' in current_problem:
            correct_answers = ['32', '32 cm', '32cm', 'trzydzieści dwa']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Obwód kwadratu = 4 × bok = 4 × 8 = 32"
            
        elif 'pole prostokąta o bokach 4 cm i 9 cm' in current_problem:
            correct_answers = ['36', '36 cm²', '36cm²', '36 cm^2', 'trzydzieści sześć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pole prostokąta = a × b = 4 × 9 = 36"
            
        elif 'obwód trójkąta o bokach 3 cm, 4 cm i 5 cm' in current_problem:
            correct_answers = ['12', '12 cm', '12cm', 'dwanaście']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Obwód trójkąta = suma wszystkich boków = 3 + 4 + 5 = 12"
            
        elif 'pole trójkąta o podstawie 10 cm i wysokości 6 cm' in current_problem:
            correct_answers = ['30', '30 cm²', '30cm²', '30 cm^2', 'trzydzieści']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Pole trójkąta = (podstawa × wysokość) / 2 = (10 × 6) / 2 = 60/2 = 30"
            
        # ========== UŁAMKI ==========
        elif '1/2 + 1/3' in current_problem:
            correct_answers = ['5/6', '5:6', '10/12', '0.83', '0,83']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Wspólny mianownik to 6. 1/2 = 3/6, 1/3 = 2/6. Więc 3/6 + 2/6 = 5/6"
            
        elif '3/4 - 1/2' in current_problem:
            correct_answers = ['1/4', '0.25', '0,25', '2/8']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Wspólny mianownik to 4. 3/4 - 1/2 = 3/4 - 2/4 = 1/4"
            
        elif '1/2 - 1/4' in current_problem:
            correct_answers = ['1/4', '0.25', '0,25', '2/8']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Wspólny mianownik to 4. 1/2 = 2/4, więc 2/4 - 1/4 = 1/4"
            
        elif '2/3 × 3/4' in current_problem or '2/3 * 3/4' in current_problem:
            correct_answers = ['1/2', '0.5', '0,5', '6/12']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Mnożenie ułamków: (2×3)/(3×4) = 6/12 = 1/2"
            
        elif '1/2 ÷ 1/4' in current_problem or '1/2 / 1/4' in current_problem:
            correct_answers = ['2', '2/1', '8/4', 'dwa']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Dzielenie to mnożenie przez odwrotność: 1/2 × 4/1 = 4/2 = 2"
            
        elif '1/3 + 1/6' in current_problem:
            correct_answers = ['1/2', '3/6', '0.5', '0,5', 'połowa']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Wspólny mianownik to 6. 1/3 = 2/6, więc 2/6 + 1/6 = 3/6 = 1/2"
            
        elif '5/6 - 1/3' in current_problem:
            correct_answers = ['1/2', '3/6', '0.5', '0,5', 'połowa']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Wspólny mianownik to 6. 1/3 = 2/6, więc 5/6 - 2/6 = 3/6 = 1/2"
            
        elif '1/4 + 3/4' in current_problem:
            correct_answers = ['1', '4/4', 'jeden', 'całość']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Ten sam mianownik: 1/4 + 3/4 = 4/4 = 1 (całość)"
            
        elif '2/5 + 1/5' in current_problem:
            correct_answers = ['3/5', '0.6', '0,6']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Ten sam mianownik: 2/5 + 1/5 = 3/5"
            
        elif '3/8 + 1/8' in current_problem:
            correct_answers = ['4/8', '1/2', '0.5', '0,5', 'połowa']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "Ten sam mianownik: 3/8 + 1/8 = 4/8 = 1/2"
            
        # ========== PROCENTY ==========
        elif '20% z liczby 150' in current_problem:
            correct_answers = ['30', 'trzydzieści']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "20% = 0.2. Więc 0.2 × 150 = 30"
            
        elif '50% z liczby 80' in current_problem:
            correct_answers = ['40', 'czterdzieści']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "50% to połowa. Połowa z 80 to 40"
            
        elif '25% z liczby 200' in current_problem:
            correct_answers = ['50', 'pięćdziesiąt']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "25% to 1/4. Więc 200 ÷ 4 = 50"
            
        elif '10% z liczby 450' in current_problem:
            correct_answers = ['45', 'czterdzieści pięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "10% = 0.1. Więc 0.1 × 450 = 45"
            
        elif '15% z liczby 100' in current_problem:
            correct_answers = ['15', 'piętnaście']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "15% ze 100 = 0.15 × 100 = 15"
            
        elif '30% z liczby 90' in current_problem:
            correct_answers = ['27', 'dwadzieścia siedem']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "30% = 0.3. Więc 0.3 × 90 = 27"
            
        elif '75% z liczby 40' in current_problem:
            correct_answers = ['30', 'trzydzieści']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "75% = 3/4. Więc (3/4) × 40 = 30"
            
        elif '5% z liczby 200' in current_problem:
            correct_answers = ['10', 'dziesięć']
            is_correct = any(ans in math_input or ans in user_input_lower for ans in correct_answers)
            hint = "5% = 0.05. Więc 0.05 × 200 = 10"
        
        # Jeśli nie znaleziono zadania, daj domyślną wskazówkę
        if not hint:
            hint = "Sprawdź dokładnie obliczenia i spróbuj jeszcze raz."
        
        print(f"[DEBUG QUIZ] Czy poprawne: {is_correct}")
        
        if is_correct:
            # Licznik poprawnych odpowiedzi
            correct_count = self.context.get('correct_answers', 0) + 1
            self.context['correct_answers'] = correct_count
            
            # Komunikat z liczbą rozwiązanych zadań
            return f"Świetnie! Dobra odpowiedź! 🎉\n(Rozwiązane zadania: {correct_count})\n\nCzy chcesz kolejne zadanie? (tak/nie)"
        else:
            return f"Hmm, spróbuj jeszcze raz. Wskazówka: {hint}"

    def _handle_farewell(self, user_input: str) -> str:
        """Obsługuje pożegnanie"""
        name = self.context.get('user_name', '')
        correct_count = self.context.get('correct_answers', 0)
        
        farewell_msg = f"Do zobaczenia{', ' + name if name else ''}! "
        if correct_count > 0:
            farewell_msg += f"Świetnie ci poszło - rozwiązałeś {correct_count} zadań! "
        farewell_msg += "Powodzenia w nauce matematyki!"
        
        self.current_state = DialogState.GREETING
        return farewell_msg
        
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
        """Generuje zadanie matematyczne (stara metoda dla kompatybilności)"""
        problems = self._get_all_problems()
        topic_problems = problems.get(self.current_topic, ["Rozwiąż to zadanie."])
        return random.choice(topic_problems)
        
    def _generate_unique_problem(self) -> str:
        """Generuje zadanie matematyczne, które jeszcze nie było użyte"""
        problems = self._get_all_problems()
        topic_problems = problems.get(self.current_topic, ["Rozwiąż to zadanie."])
        
        # Znajdź nieużyte zadania
        unused_problems = [p for p in topic_problems if p not in self.used_problems[self.current_topic]]
        
        # Jeśli wszystkie zadania zostały użyte
        if not unused_problems:
            # Możemy zresetować listę użytych zadań
            self.used_problems[self.current_topic].clear()
            unused_problems = topic_problems
            print(f"[DEBUG] Zresetowano listę zadań dla tematu: {self.current_topic}")
        
        # Wybierz losowe zadanie z nieużytych
        if unused_problems:
            selected_problem = random.choice(unused_problems)
            self.used_problems[self.current_topic].add(selected_problem)
            print(f"[DEBUG] Wybrano zadanie: {selected_problem}")
            print(f"[DEBUG] Użyte zadania ({self.current_topic}): {len(self.used_problems[self.current_topic])}/{len(topic_problems)}")
            return selected_problem
        else:
            return "Brak dostępnych zadań."
            
    def _get_all_problems(self) -> Dict[str, List[str]]:
        """Zwraca wszystkie dostępne zadania"""
        return {
            'równania': [
                "Rozwiąż równanie: 2x + 5 = 13. Ile wynosi x?",
                "Rozwiąż równanie: 3x - 7 = 8. Ile wynosi x?",
                "Rozwiąż równanie: x/2 + 3 = 5. Ile wynosi x?",
                "Rozwiąż równanie: 4x = 16. Ile wynosi x?",
                "Rozwiąż równanie: x + 7 = 12. Ile wynosi x?",
                "Rozwiąż równanie: 2x - 3 = 9. Ile wynosi x?",
                "Rozwiąż równanie: 5x + 2 = 17. Ile wynosi x?",
                "Rozwiąż równanie: x/3 = 4. Ile wynosi x?"
            ],
            'funkcje': [
                "Dla funkcji f(x) = 2x + 3, oblicz f(5).",
                "Dla funkcji f(x) = x² - 1, oblicz f(3).",
                "Dla funkcji f(x) = 3x - 2, oblicz f(4).",
                "Dla funkcji f(x) = x + 7, oblicz f(0).",
                "Dla funkcji f(x) = 4x, oblicz f(2).",
                "Dla funkcji f(x) = x² + 2, oblicz f(2).",
                "Dla funkcji f(x) = 2x - 5, oblicz f(6).",
                "Dla funkcji f(x) = x/2 + 1, oblicz f(8)."
            ],
            'geometria': [
                "Oblicz pole trójkąta o podstawie 6 cm i wysokości 4 cm.",
                "Oblicz pole kwadratu o boku 5 cm.",
                "Oblicz obwód prostokąta o bokach 3 cm i 7 cm.",
                "Oblicz pole koła o promieniu 2 cm (użyj π ≈ 3.14).",
                "Oblicz obwód kwadratu o boku 8 cm.",
                "Oblicz pole prostokąta o bokach 4 cm i 9 cm.",
                "Oblicz obwód trójkąta o bokach 3 cm, 4 cm i 5 cm.",
                "Oblicz pole trójkąta o podstawie 10 cm i wysokości 6 cm."
            ],
            'ułamki': [
                "Oblicz: 1/2 + 1/3",
                "Oblicz: 3/4 - 1/2",
                "Oblicz: 1/2 - 1/4",
               "Oblicz: 2/3 × 3/4",
               "Oblicz: 1/2 ÷ 1/4",
               "Oblicz: 1/3 + 1/6",
               "Oblicz: 5/6 - 1/3",
               "Oblicz: 1/4 + 3/4",
               "Oblicz: 2/5 + 1/5",
               "Oblicz: 3/8 + 1/8"
           ],
           'procenty': [
               "Oblicz 20% z liczby 150.",
               "Oblicz 50% z liczby 80.",
               "Oblicz 25% z liczby 200.",
               "Oblicz 10% z liczby 450.",
               "Oblicz 15% z liczby 100.",
               "Oblicz 30% z liczby 90.",
               "Oblicz 75% z liczby 40.",
               "Oblicz 5% z liczby 200."
           ]
}
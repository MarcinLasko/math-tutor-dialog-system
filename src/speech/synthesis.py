"""
Moduł syntezy mowy (Text-to-Speech)
Używa pyttsx3 do generowania mowy
"""

import pyttsx3
import threading
import queue
import logging

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextToSpeech:
    def __init__(self):
        """Inicjalizacja silnika TTS"""
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Inicjalizuj silnik
        self._init_engine()
        
    def _init_engine(self):
        """Inicjalizuje silnik pyttsx3"""
        try:
            self.engine = pyttsx3.init()
            
            # Konfiguracja głosu
            voices = self.engine.getProperty('voices')
            
            # Wybierz polski głos jeśli dostępny
            polish_voice = None
            for voice in voices:
                if 'polish' in voice.name.lower() or 'pl' in voice.id.lower():
                    polish_voice = voice
                    break
                    
            if polish_voice:
                self.engine.setProperty('voice', polish_voice.id)
                logger.info(f"Używam polskiego głosu: {polish_voice.name}")
            else:
                # Użyj pierwszego dostępnego głosu
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
                logger.warning("Nie znaleziono polskiego głosu, używam domyślnego")
            
            # Ustaw parametry mowy
            self.engine.setProperty('rate', 150)    # Szybkość mowy
            self.engine.setProperty('volume', 0.9)  # Głośność (0.0 - 1.0)
            
            logger.info("Silnik TTS zainicjalizowany pomyślnie")
            
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji TTS: {e}")
            self.engine = None
            
    def speak(self, text, callback=None):
        """
        Wypowiada podany tekst
        
        Args:
            text (str): Tekst do wypowiedzenia
            callback (function): Funkcja wywoływana po zakończeniu mowy
        """
        if not self.engine:
            logger.error("Silnik TTS nie jest zainicjalizowany")
            if callback:
                callback()
            return
            
        # Dodaj do kolejki
        self.speech_queue.put((text, callback))
        
        # Uruchom wątek mowy jeśli nie działa
        if not self.is_speaking:
            self.speech_thread = threading.Thread(target=self._speech_worker)
            self.speech_thread.daemon = True
            self.speech_thread.start()
            
    def _speech_worker(self):
        """Wątek obsługujący kolejkę mowy"""
        self.is_speaking = True
        
        while not self.speech_queue.empty():
            try:
                text, callback = self.speech_queue.get()
                
                logger.info(f"Wypowiadam: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                
                if callback:
                    callback()
                    
            except Exception as e:
                logger.error(f"Błąd podczas syntezy mowy: {e}")
                
        self.is_speaking = False
        
    def stop(self):
        """Zatrzymuje syntezę mowy"""
        if self.engine:
            self.engine.stop()
            
        # Wyczyść kolejkę
        while not self.speech_queue.empty():
            self.speech_queue.get()
            
        self.is_speaking = False
        logger.info("Synteza mowy zatrzymana")
        
    def set_rate(self, rate):
        """Ustawia szybkość mowy (50-300)"""
        if self.engine:
            self.engine.setProperty('rate', max(50, min(300, rate)))
            
    def set_volume(self, volume):
        """Ustawia głośność (0.0-1.0)"""
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
    def get_voices(self):
        """Zwraca listę dostępnych głosów"""
        if self.engine:
            return self.engine.getProperty('voices')
        return []


# Singleton dla łatwego dostępu
_tts_instance = None

def get_tts():
    """Zwraca instancję TTS (singleton)"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance
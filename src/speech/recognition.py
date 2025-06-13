"""
Moduł rozpoznawania mowy używający VOSK
"""

import json
import queue
import sounddevice as sd
import vosk
import logging
import threading
import os
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpeechRecognizer:
    def __init__(self, on_result: Callable[[str], None], on_partial: Optional[Callable[[str], None]] = None):
        """
        Inicjalizacja rozpoznawania mowy
        
        Args:
            on_result: Callback wywoływany gdy rozpoznano pełną wypowiedź
            on_partial: Opcjonalny callback dla częściowych wyników
        """
        self.on_result = on_result
        self.on_partial = on_partial
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Parametry audio
        self.sample_rate = 16000
        self.channels = 1
        
        # Ścieżka do modelu
        model_path = os.path.join("assets", "models", "vosk-model-pl")
        
        # Inicjalizacja modelu VOSK
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model VOSK nie znaleziony w: {model_path}")
                
            logger.info(f"Ładowanie modelu VOSK z: {model_path}")
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            logger.info("Model VOSK załadowany pomyślnie")
            
        except Exception as e:
            logger.error(f"Błąd podczas ładowania modelu VOSK: {e}")
            self.model = None
            self.recognizer = None
            
        # Wątek przetwarzania
        self.processing_thread = None
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback dla strumienia audio"""
        if status:
            logger.warning(f"Status audio: {status}")
        self.audio_queue.put(bytes(indata))
        
    def _process_audio(self):
        """Wątek przetwarzający audio"""
        logger.info("Rozpoczęto przetwarzanie audio")
        
        while self.is_listening:
            try:
                # Pobierz dane audio z kolejki
                data = self.audio_queue.get(timeout=0.5)
                
                if self.recognizer.AcceptWaveform(data):
                    # Pełny wynik
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        logger.info(f"Rozpoznano: {text}")
                        self.on_result(text)
                else:
                    # Częściowy wynik
                    if self.on_partial:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '').strip()
                        if partial_text:
                            self.on_partial(partial_text)
                            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania audio: {e}")
                
        logger.info("Zakończono przetwarzanie audio")
        
    def start_listening(self):
        """Rozpoczyna nasłuchiwanie"""
        if not self.model or not self.recognizer:
            logger.error("Model VOSK nie jest zainicjalizowany")
            return False
            
        if self.is_listening:
            logger.warning("Już nasłuchuje")
            return True
            
        try:
            # Wyczyść kolejkę
            while not self.audio_queue.empty():
                self.audio_queue.get()
                
            # Ustaw flagę
            self.is_listening = True
            
            # Uruchom wątek przetwarzania
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            # Uruchom strumień audio
            self.stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                callback=self._audio_callback,
                blocksize=8000
            )
            self.stream.start()
            
            logger.info("Rozpoczęto nasłuchiwanie")
            return True
            
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania nasłuchiwania: {e}")
            self.is_listening = False
            return False
            
    def stop_listening(self):
        """Zatrzymuje nasłuchiwanie"""
        if not self.is_listening:
            return
            
        self.is_listening = False
        
        # Zatrzymaj strumień
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
            
        # Poczekaj na zakończenie wątku
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
            
        logger.info("Zatrzymano nasłuchiwanie")
        
    def get_final_result(self):
        """Pobiera ostatni wynik"""
        if self.recognizer:
            result = json.loads(self.recognizer.FinalResult())
            return result.get('text', '').strip()
        return ""


# Test mikrofonu
def test_microphone():
    """Testuje czy mikrofon działa"""
    try:
        # Sprawdź urządzenia audio
        devices = sd.query_devices()
        logger.info("Dostępne urządzenia audio:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                logger.info(f"  [{i}] {device['name']} (wejście)")
                
        # Test nagrywania
        logger.info("Test nagrywania 1 sekundy...")
        recording = sd.rec(int(1 * 16000), samplerate=16000, channels=1, dtype='int16')
        sd.wait()
        logger.info("Test zakończony pomyślnie")
        return True
        
    except Exception as e:
        logger.error(f"Błąd podczas testu mikrofonu: {e}")
        return False
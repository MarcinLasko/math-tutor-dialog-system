"""
Logger sesji - zapisuje pełną historię rozmowy
"""

import os
from datetime import datetime
import json


class SessionLogger:
    def __init__(self):
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        self.log_dir = "session_logs"
        
        # Utwórz folder jeśli nie istnieje
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(
            self.log_dir, 
            f"session_{self.session_id}.log"
        )
        
        self.json_file = os.path.join(
            self.log_dir,
            f"session_{self.session_id}.json"
        )
        
        self.conversation_data = {
            'session_id': self.session_id,
            'start_time': self.session_start.isoformat(),
            'messages': []
        }
        
        self._write_header()
        
    def _write_header(self):
        """Zapisuje nagłówek do pliku tekstowego"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"SESJA KOREPETYCJI MATEMATYCZNYCH\n")
            f.write(f"Data: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"ID sesji: {self.session_id}\n")
            f.write(f"{'='*60}\n\n")
            
    def log_message(self, sender: str, message: str, extra_data: dict = None):
        """Loguje wiadomość do pliku"""
        timestamp = datetime.now()
        
        # Zapis do pliku tekstowego
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp.strftime('%H:%M:%S')}] {sender}: {message}\n")
            
        # Zapis do struktury JSON
        message_data = {
            'timestamp': timestamp.isoformat(),
            'sender': sender,
            'message': message,
            'extra': extra_data or {}
        }
        self.conversation_data['messages'].append(message_data)
        
    def save_session(self, final_stats: dict = None):
        """Zapisuje pełną sesję do JSON"""
        self.conversation_data['end_time'] = datetime.now().isoformat()
        
        if final_stats:
            self.conversation_data['statistics'] = final_stats
            
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_data, f, ensure_ascii=False, indent=2)
            
        # Dodaj podsumowanie do pliku tekstowego
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"KONIEC SESJI: {datetime.now().strftime('%H:%M:%S')}\n")
            if final_stats:
                f.write(f"Poprawnych odpowiedzi: {final_stats.get('correct', 0)}/{final_stats.get('total', 0)}\n")
            f.write(f"{'='*60}\n")
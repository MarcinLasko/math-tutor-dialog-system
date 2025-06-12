#!/usr/bin/env python3
"""
System Dialogowy Korepetytora Matematycznego
Główny punkt wejścia aplikacji
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Dodaj src do ścieżki
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import MathTutorApp


def main():
    """Główna funkcja uruchamiająca aplikację"""
    root = tk.Tk()
    app = MathTutorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
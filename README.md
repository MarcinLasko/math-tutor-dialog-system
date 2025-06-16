# System Dialogowy Korepetytora Matematycznego

System dialogowy z rozpoznawaniem mowy realizujący funkcję korepetytora matematycznego.

## Informacje o projekcie

- **Przedmiot**: Standardy w projektowaniu systemów dialogowych
- **Uczelnia**: Wojskowa Akademia Techniczna
- **Autor**: Marcin Laskowski
- **Rok akademicki**: 2024/2025

## Funkcjonalności

- Dialog z inicjatywą przemienną
- Rozpoznawanie mowy (VOSK)
- Synteza mowy (pyttsx3)
- Graficzny interfejs użytkownika
- Wsparcie dla różnych poziomów nauczania

## Wymagania

- Python 3.8+
- Mikrofon
- System operacyjny: Windows/Linux/macOS

## Instalacja

```bash
# Sklonuj repozytorium
git clone https://github.com/TwojaNazwa/math-tutor-dialog-system.git
cd math-tutor-dialog-system

# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności
python -m pip install --upgrade pip
pip install -r requirements.txt

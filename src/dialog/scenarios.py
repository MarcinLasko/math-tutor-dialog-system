"""
Scenariusze dialogowe dla korepetytora matematycznego
"""

# Słownik reakcji na różne wypowiedzi użytkownika
RESPONSES = {
    'greetings': {
        'patterns': ['cześć', 'hej', 'witaj', 'dzień dobry', 'siema'],
        'responses': [
            "Cześć! Miło cię widzieć. Jak masz na imię?",
            "Witaj! Jestem twoim korepetytorem. Jak się nazywasz?",
            "Hej! Gotowy na matematykę? Najpierw się przedstaw!"
        ]
    },
    
    'help_requests': {
        'patterns': ['pomóż', 'nie wiem', 'nie rozumiem', 'help', 'trudne'],
        'responses': [
            "Spokojnie, pomogę ci krok po kroku.",
            "Nie martw się, razem to rozwiążemy.",
            "Spróbujmy inaczej. Co dokładnie sprawia ci trudność?"
        ]
    },
    
    'praise': {
        'patterns': ['super', 'świetnie', 'dobrze', 'brawo'],
        'responses': [
            "Dziękuję! Ty też świetnie sobie radzisz!",
            "Cieszę się, że ci się podoba!",
            "Super! Matematyka może być fajna!"
        ]
    },
    
    'corrections': {
        'wrong_answer': [
            "Hmm, spróbuj jeszcze raz. Jesteś blisko!",
            "Prawie dobrze! Sprawdź obliczenia.",
            "Nie do końca. Pomyśl jeszcze chwilę."
        ],
        'correct_answer': [
            "Świetnie! Doskonała odpowiedź! 🎉",
            "Brawo! Masz rację! 👏",
            "Dokładnie tak! Super ci idzie! ⭐"
        ]
    }
}

# Poziomy trudności zadań
DIFFICULTY_LEVELS = {
    'klasa_4': {
        'topics': ['dodawanie', 'odejmowanie', 'mnożenie', 'dzielenie'],
        'range': (1, 100)
    },
    'klasa_5': {
        'topics': ['ułamki_proste', 'procenty_proste', 'figury'],
        'range': (1, 200)
    },
    'klasa_6': {
        'topics': ['ułamki', 'procenty', 'równania_proste'],
        'range': (1, 500)
    },
    'klasa_7': {
        'topics': ['równania', 'funkcje_liniowe', 'geometria'],
        'range': (1, 1000)
    },
    'klasa_8': {
        'topics': ['równania_kwadratowe', 'funkcje', 'stereometria'],
        'range': (1, 1000)
    },
    'liceum': {
        'topics': ['funkcje_złożone', 'trygonometria', 'logarytmy'],
        'range': (1, 10000)
    },
    'matura': {
        'topics': ['analiza', 'geometria_analityczna', 'rachunek_prawdopodobieństwa'],
        'range': (1, 10000)
    }
}
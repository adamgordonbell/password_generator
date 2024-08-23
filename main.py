from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from typing import List, Dict, Tuple, Any

app = Flask(__name__)

THREE_DIGIT_PRIMES: List[int] = [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

COMMON_EMOTICONS: List[str] = ["😊", "😂", "🤣", "❤️", "😍", "😒", "👍", "😘", "🤔", "😭"]

ASTROLOGICAL_SIGNS: List[str] = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓"
]

EXTINCT_LANGUAGES: List[str] = [
    "Sumerian", "Akkadian", "Etruscan", "Gothic", "Old Norse", "Ancient Greek",
    "Latin", "Coptic", "Aramaic", "Ancient Egyptian", "Hittite", "Phoenician",
    "Mayan", "Aztec", "Inca", "Old English", "Middle English", "Old French",
    "Old High German", "Old Irish", "Tocharian", "Pictish", "Manx", "Cornish"
]

def count_distinct_digits(password: str) -> int:
    return min(len(set(char for char in password if char.isdigit())), 3)

def count_length_segments(password: str) -> int:
    return min(len(password) // 20, 3)

def count_distinct_special_chars(password: str) -> int:
    return min(len(set(char for char in password if char in '!@#$%^&*()_+-=[]{}|;:,.<>?')), 3)

def count_distinct_uppercase(password: str) -> int:
    return min(len(set(char for char in password if char.isupper())), 3)

def count_distinct_three_digit_primes(password: str) -> int:
    return min(len(set(num for num in re.findall(r'\d{3}', password) if int(num) in THREE_DIGIT_PRIMES)), 3)

def count_distinct_extinct_languages(password: str) -> int:
    return min(len(set(lang for lang in EXTINCT_LANGUAGES if lang.lower() in password.lower())), 3)

def count_distinct_chess_moves(password: str) -> int:
    chess_move_pattern = r'\b([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?|\b[O-O(-O)?]\b)(\+|#)?\b'
    return min(len(set(re.findall(chess_move_pattern, password, re.IGNORECASE))), 3)

def count_unicode_blocks(password: str) -> int:
    blocks = set()
    for char in password:
        if '\u0000' <= char <= '\u007F':
            blocks.add('Basic Latin')
        elif '\u0080' <= char <= '\u00FF':
            blocks.add('Latin-1 Supplement')
        elif '\u0100' <= char <= '\u017F':
            blocks.add('Latin Extended-A')
        else:
            blocks.add('Other')
    return min(len(blocks), 3)

def count_distinct_owl_ascii_art(password: str) -> int:
    owl_patterns = [r'\(o.o\)', r'\(O.O\)', r'\(°v°\)']
    return min(len(set(pattern for pattern in owl_patterns if re.search(pattern, password))), 3)

def count_distinct_mouse_ascii_art(password: str) -> int:
    mouse_patterns = [r'<:3~']
    return min(len(set(pattern for pattern in mouse_patterns if re.search(pattern, password))), 3)

def count_distinct_emoticons(password: str) -> int:
    return min(len(set(emoticon for emoticon in COMMON_EMOTICONS if emoticon in password)), 3)

def count_distinct_astrological_signs(password: str) -> int:
    return min(len(set(sign for sign in ASTROLOGICAL_SIGNS if sign in password)), 3)

def get_db() -> Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        port=os.environ['PGPORT'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        database=os.environ['PGDATABASE']
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

@app.route('/check_password', methods=['POST'])
def check_password() -> Any:
    password = request.json['password']
    strength, conditions = assess_password_strength(password)
    store_attempt(password, strength)
    return jsonify({'strength': strength, 'conditions': conditions})

@app.route('/attempts')
def view_attempts() -> str:
    conn, cur = get_db()
    
    # Get recent high scores (top 5 in the last hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    cur.execute('SELECT * FROM attempts WHERE timestamp > %s ORDER BY strength DESC LIMIT 5', (one_hour_ago,))
    recent_high_scores = cur.fetchall()
    
    # Get recent attempts
    cur.execute('SELECT * FROM attempts ORDER BY timestamp DESC LIMIT 10')
    attempts = cur.fetchall()
    
    # Get all-time high scores
    cur.execute('SELECT * FROM attempts ORDER BY strength DESC LIMIT 5')
    high_scores = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('attempts.html', recent_high_scores=recent_high_scores, attempts=attempts, high_scores=high_scores)

def assess_password_strength(password: str) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    strength = 0
    conditions = [
        {'message': "Contains a number", 'met': 0, 'positive': True, 'hint': "Include at least one digit (0-9) in your password.", 'points': 1},
        {'message': "Longer than 20 characters", 'met': 0, 'positive': True, 'hint': "Make your password longer than 20 characters.", 'points': 2},
        {'message': "Contains a special character", 'met': 0, 'positive': True, 'hint': "Include at least one special character (e.g., !@#$%^&*).", 'points': 1},
        {'message': "Contains an uppercase letter", 'met': 0, 'positive': True, 'hint': "Include at least one uppercase letter.", 'points': 1},
        {'message': "Contains a prime number with 3 digits", 'met': 0, 'positive': True, 'hint': "Include a three-digit prime number (e.g., 101, 103, 107).", 'points': 3},
        {'message': "Includes the name of an extinct language", 'met': 0, 'positive': True, 'hint': "Include the name of an extinct language (e.g., Sumerian, Gothic, Latin).", 'points': 4},
        {'message': "Contains a valid chess move in algebraic notation", 'met': 0, 'positive': True, 'hint': "Include a valid chess move in algebraic notation (e.g., e4, Nf3, O-O).", 'points': 3},
        {'message': "Has a character from a different Unicode block", 'met': 0, 'positive': True, 'hint': "Lots to choose from: Hello☕й→世界123αβγちは", 'points': 3},
        {'message': "Contains an ASCII art owl", 'met': 0, 'positive': True, 'hint': " (e.g. (o.o), (O.O), or (°v°)).", 'points': 2},
        {'message': "Contains an ASCII art mouse", 'met': 0, 'positive': True, 'hint': "(e.g. <:3~ ", 'points': 2},
        {'message': "Contains emoticons", 'met': 0, 'positive': True, 'hint': "Include a common emoticon (e.g., 😊 😂 🤣).", 'points': 2},
        {'message': "Contains an astrological sign", 'met': 0, 'positive': True, 'hint': "Include an astrological sign symbol (e.g., ♈, ♉, ♊).", 'points': 2},
    ]
    
    conditions[0]['met'] = count_distinct_digits(password)
    conditions[1]['met'] = count_length_segments(password)
    conditions[2]['met'] = count_distinct_special_chars(password)
    conditions[3]['met'] = count_distinct_uppercase(password)
    conditions[4]['met'] = count_distinct_three_digit_primes(password)
    conditions[5]['met'] = count_distinct_extinct_languages(password)
    conditions[6]['met'] = count_distinct_chess_moves(password)
    conditions[7]['met'] = count_unicode_blocks(password)
    conditions[8]['met'] = count_distinct_owl_ascii_art(password)
    conditions[9]['met'] = count_distinct_mouse_ascii_art(password)
    conditions[10]['met'] = count_distinct_emoticons(password)
    conditions[11]['met'] = count_distinct_astrological_signs(password)
    
    for condition in conditions:
        strength += condition['points'] * condition['met']
    
    return {'score': strength}, conditions

def store_attempt(password: str, strength: Dict[str, int]) -> None:
    conn, cur = get_db()
    cur.execute('INSERT INTO attempts (password, strength, timestamp) VALUES (%s, %s, %s)',
                (password, strength['score'], datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index() -> str:
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", default="5000")))

# Unnecessary Password Strength Checker

This project is a humorous take on password strength checkers, implementing unnecessarily complex rules for password evaluation.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   python db_setup.py
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Visit `http://localhost:5000` in your web browser.

## Unicode Block Examples

Here are some example passwords that use characters from at least 3 different Unicode blocks:

1. "Hello☕й→世界123αβγちは1" - Uses Basic Latin, CJK Unified Ideographs, and ASCII Digits
2. "Café2023" - Uses Basic Latin, Miscellaneous Symbols, and ASCII Digits
3. "Здравствуй→World" - Uses Cyrillic, Arrows, and Basic Latin
4. "αβγ123!@#" - Uses Greek and Coptic, ASCII Digits, and Basic Latin (for symbols)
5. "こんにちは1234АБВ" - Uses Hiragana, ASCII Digits, and Cyrillic

These passwords would satisfy the condition of having characters from at least 3 different Unicode blocks.

## Cleanup Script

To run the cleanup script manually:
```
python cleanup.py
```

For deployment on Railway, set this up as a cron job to run daily.

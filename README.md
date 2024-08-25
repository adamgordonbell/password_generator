# Unnecessary Password Strength Checker

This project is a humorous take on password strength checkers, using unnecessarily complex rules for password evaluation.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate 
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
   python main.py
   ```

5. Visit `http://localhost:5000` in your web browser.


## Cleanup Script

To run the cleanup script manually:
```
python cleanup.py
```

For deployment on Railway, set this up as a cron job to run daily.

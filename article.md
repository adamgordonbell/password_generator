---
title: "From Silly Passwords to Seamless Deployment: A Developer's Railway Journey"
author: Adam Gordon Bell
---

# From Silly Passwords to Seamless Deployment: A Developer's Railway Journey

### Introduction

Password creation screens often demand an uppercase letter, a number, a special character, your great-grandmother's maiden name, and two Sumerian cuniforms. In a fit of mild frustration, I decided to take this concept to its illogical extreme by creating the Unnecessary Password Strength Checker. 

This Flask-based web application is a game where you attempt to defeat absurd password criteria and get on the high scoreboard. Want points for including a three-digit prime number or throwing in some ASCII art or the name of an extinct language? Absolutely.

But building the app is only half the battle. Deploying it and keeping it up is the real challenge. How do you quickly go from a local Flask app to a live, database-backed web service without getting bogged down in infrastructure management?

Well, let me walk you through my experience building and deploying this over-engineered password checker using Railway, and let's see if it simplifies the whole process. But first, lets build the app. 

### Building the Unnecessary Password Strength Checker

#### Flask Application Setup

The core of my application is built using Flask. Here's are the main routes: 

```Python
app = Flask(__name__)

@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/check_password', methods=['POST'])
def check_password() -> Any:
    password = request.json['password']
    strength, conditions = assess_password_strength(password)
    store_attempt(password, strength)
    return jsonify({'strength': strength, 'conditions': conditions})
```

This JSON object returned by `/check_password` is the key interface our front end will use.

#### Unique Password Strength Rules

The `assess_password_strength` function performs the real magic. Here's a glimpse of how we define our unique (and arguably unnecessary) password strength conditions:

```Python
def assess_password_strength(password: str) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    strength = 0
    conditions = [
        {'message': "Contains a number", 'met': 0, 'positive': True, 'hint': "Include at least one digit (0-9) in your password.", 'points': 1},
        {'message': "Longer than 20 characters", 'met': 0, 'positive': True, 'hint': "Make your password longer than 20 characters.", 'points': 2},
        ... 
    ]
    
    return {'score': strength}, conditions
```

Each condition is checked using specialized functions. Here are some of the more interesting ones:

```Python
def count_distinct_three_digit_primes(password: str) -> int:
    return min(len(set(num for num in re.findall(r'\d{3}', password) if int(num) in THREE_DIGIT_PRIMES)), 3)

def count_distinct_extinct_languages(password: str) -> int:
    return min(len(set(lang for lang in EXTINCT_LANGUAGES if lang.lower() in password.lower())), 3)

def count_distinct_chess_moves(password: str) -> int:
    chess_move_pattern = r'\b([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?|\b[O-O(-O)?]\b)(\+|#)?\b'
    return min(len(set(re.findall(chess_move_pattern, password, re.IGNORECASE))), 3)
```

These functions check for the presence of three-digit primes, extinct languages, and valid chess moves in algebraic notation, respectively. I'm using hard-coded lists where I can to keep the CPU usage down.

#### Unicode and ASCII Art Detection

I even check for the use of different Unicode blocks and ASCII art:

```Python
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
    mouse_patterns = [r'<:3~', r'<:3)~~']
    return min(len(set(pattern for pattern in mouse_patterns if re.search(pattern, password))), 3)
```

#### Database Integration

To keep track of password attempts and high scores, I reach for PostgreSQL:

```Python
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

def store_attempt(password: str, strength: Dict[str, int]) -> None:
    conn, cur = get_db()
    cur.execute('INSERT INTO attempts (password, strength, timestamp) VALUES (%s, %s, %s)',
                (password, strength['score'], datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
```

`store_attempt` is going to power the high scoreboard.

#### Frontend Integration

While the backend logic is where the real magic happens, we also implemented a simple frontend to interact with our API:

```javascript
fetch('/check_password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({password: this.value}),
})
.then(response => response.json())
.then(data => updateUI(data));
```

This JavaScript code sends the password to our backend and updates the UI based on the response.

This all works well locally. Now, let's see about deploying it.

### Deploying with Railway: A Step-by-Step Journey

#### Setting up the project in Railway

The first step was to create a new project in Railway and connect it to my GitHub repository. This process was straightforward:

1. Create a new project in the Railway dashboard
2. Choose the option to deploy from a GitHub repo
3. Select the repository containing my password checker

With the project set up, I needed to configure how Railway would build and run our application. A lot of this is done for me using NIXPACKS. Instead of creating a docker file with a specific Python version and then installing my requirements into it, most of this is autodetected by [NIXPACKS](https://nixpacks.com/docs/providers/python) and seems to work right off the bat.

However, I do have some specific requirements: I need to run a setup script and I need to use `gunicorn` to serve my Flask app. I can change these in the Railway UI, but I decided to use the config file (`railway.toml`) in my repo:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python db_setup.py && gunicorn main:app"
```

This tells Railway to use Nixpacks to build and run the setup file on start. I also need to change my app to listen on `PORT`: 
```Python
if __name__ == '__main__':
    app.run(debug=False, port=int(os.getenv("PORT", default="5000")))
``` 

With that, I can link my project by running `railway link` and then `railway up` in the command line to start my build and deployment. 

After watching the successful nixpack build and then deploy, I visit the provided URL ( passwordgenerator-production-11d0.up.railway.app) and get a 500 error.

Thankfully, Railway comes with a log monitoring tab, and there I see this:

```
psycopg2.OperationalError: FATAL:  database "*******" does not exist
```

Oh yeah, the database! I need to set that up.

#### Configuring the database

Railway makes it easy to provision a PostgreSQL database, by dragging it into the design surface of the project. Once I do that, I can see it exposes several ENVs for `PGHOST` and so on. Then, I can add these to my Flask app.

<div style="display: flex; justify-content: space-between;">
    <img src="https://i.imgur.com/eqfK2jS.png" alt="Railway Database Setup" width="48%">
    <img src="https://i.imgur.com/Mbkbn4o.png" alt="Railway Database Setup" width="48%">
</div>

Doing so creates a visual arrow between my service and the database, showing me at a glance that they are connected. And with that and a deployment, the app works.

<div style="display: flex; justify-content: space-between;">
    <img src="https://imgur.com/bFVCBAw.png" alt="Working App 1" width="48%">
    <img src="https://imgur.com/9A3iqTM.png" alt="Working App 2" width="48%">
</div>

Now, I just have to worry about data maintenance.

#### Implementing the cleanup cron job

To manage the growth of the database, I've implemented a cleanup job to remove passwords that don't make the high score table:

```Python
def cleanup_old_attempts():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the minimum strength score from the top 5 entries
    cur.execute('SELECT MIN(strength) FROM (SELECT strength FROM attempts ORDER BY strength DESC LIMIT 5) AS top_scores')
    min_top_score = cur.fetchone()[0]

    # Delete attempts older than 7 days that are not in the top score list
    seven_days_ago = datetime.now() - timedelta(days=7)
    cur.execute('DELETE FROM attempts WHERE timestamp < %s AND strength < %s', (seven_days_ago, min_top_score))
    
    deleted_count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"Cleanup complete. {deleted_count} entries removed.")
```

To run this job on a schedule, I create a separate service in Railway with its own `Railway.toml` file:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python cleanup.py"
cronSchedule = "55 * * * *"
```

This tells Railway to run our cleanup script every hour at 55 minutes past the hour. I also connected this service to the database, hit deploy, and everything was in place.

<div style="display: flex; justify-content: space-between;">
    <img src="https://i.imgur.com/75Xlr1y.png" alt="Final Version" width="48%">
</div>

#### Everything Else

Now that I have my app deployed and working, this is when I'd usually turn my mind to all the essential but tedious parts of rolling out a side project. Things like getting CI/CD in place, getting a log aggregating solution in place, and setting up alerts so I know if this thing goes down or 'goes viral'.

Thankfully, though, without really meaning to, by choosing Railway, I have those covered. The log aggregation is built in. They are just tabs that are already set up. Same for metrics and an observability dashboard:

<div style="display: flex; justify-content: space-between;">
    <img src="https://i.imgur.com/C7ONQFm.png" alt="Metrics 1" width="48%">
    <img src="https://i.imgur.com/gKoWMTC.png" alt="Metrics 2" width="48%">
</div>

And CI/CD is already in place. I push to my main branch to deploy to production, and setting up other environments for local dev usage is easy. Since this is just a side project, I'm running things locally pointed at the prod DB, using `railway shell` to provide the secrets, and it's working quite well.

Here it is: [https://passwordgenerator-production-11d0.up.railway.app/](https://passwordgenerator-production-11d0.up.railway.app/)

### Faster is More Fun

As I wrap up my little side project, it's clear to me how much modern operations practices can be a drag, both a drag on timelines and just mentally a process that isn't fun and drags down a side project. If I had deployed this service the way I'm most used to, I would have needed docker, ECR, Lambdas or Kubernetes and RDS, and probably Github actions and Terraform.

The irony wasn't lost on me, though, that here I was, creating a tool to judge unnecessarily complex passwords while running it the default 'cloud native' way was becoming unnecessarily complex itself.

Why should a one-file Python service require so much work? What aren't we building because the overhead is too high? I don't know, but man, it feels nice not to have to worry about all those details!

Even Railway's use of NIXPACKs means I don't have to mess with any docker files or worry about my slow process with AWS of building images and pushing them to ECR, then images being pulled from ECR and rolled out. Something similar is happening here, but I don't have to worry about it.

The easy transition from a local Flask application to a live, database-backed web service meant I could spend more time building creative (albeit unnecessary) password-strength rules and less time wrestling with deployment details.

Here is my password checker: [https://passwordgenerator-production-11d0.up.railway.app/](https://passwordgenerator-production-11d0.up.railway.app/). See if you can max out the scoring system and get on the scoreboard. 

And stay tuned for my next project, where I may use Railway again.

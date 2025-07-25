# database.py
import sqlite3
import hashlib
import datetime

DB_NAME = "questions.db"

def create_table():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            difficulty TEXT,
            question TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            answer TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exam_date TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT,
            score INTEGER,
            total_questions INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        conn.commit()

def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Adds a new user to the database."""
    hashed_password = hash_password(password)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True # User added successfully
        except sqlite3.IntegrityError:
            return False # Username already exists

def verify_user(username, password):
    """Verifies user credentials."""
    hashed_input_password = hash_password(password)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result[1] == hashed_input_password:
            return result[0] # Return user_id on successful login
        return None # Invalid credentials or user not found

def record_exam_result(user_id, topic, difficulty, score, total_questions):
    """Records an exam result in the database."""
    exam_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO exam_results (user_id, exam_date, topic, difficulty, score, total_questions)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, exam_date, topic, difficulty, score, total_questions))
        conn.commit()

def get_user_exam_results(user_id):
    """Retrieves all exam results for a given user."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT exam_date, topic, difficulty, score, total_questions
        FROM exam_results
        WHERE user_id = ?
        ORDER BY exam_date DESC
        """, (user_id,))
        return cursor.fetchall()

def insert_question(topic, difficulty, question, options, answer):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO questions (topic, difficulty, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic, difficulty, question, *options, answer))
        conn.commit()

# def get_questions(topic, difficulty):
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#         SELECT id, question, option1, option2, option3, option4, answer FROM questions
#         WHERE topic=? AND difficulty=?
#         """, (topic, difficulty))
#         return cursor.fetchall()

def get_questions(topic="", difficulty=""):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = "SELECT id, topic, difficulty, question, option1, option2, option3, option4, answer FROM questions WHERE 1=1"
        params = []

        if topic:
            query += " AND topic LIKE ?"
            params.append(f"%{topic}%")
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)

        cursor.execute(query, params)
        return cursor.fetchall()

def count_questions():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        return count

def get_questions_all():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, topic, difficulty, question, option1, option2, option3, option4, answer FROM questions
        """)
        return cursor.fetchall()

def delete_question_by_id(qid):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id=?", (qid,))
        conn.commit()

def update_question(qid, question, options, answer):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE questions
            SET question=?, option1=?, option2=?, option3=?, option4=?, answer=?
            WHERE id=?
        """, (question, *options, answer, qid))
        conn.commit()

def is_duplicate_question(question: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions WHERE question = ?", (question,))
        return cursor.fetchone()[0] > 0

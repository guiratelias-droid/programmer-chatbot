"""
create_database.py — builds coding_mentor.db from scratch and fills it with
programming concepts, exercises, and sample learner activity.

Run: python -m scripts.create_database
It is safe to re-run: it deletes and rebuilds the tables each time.
"""

import sqlite3
import random

from faker import Faker

from app.config import settings

fake = Faker()

LANGUAGES = [
    ("Python", "A beginner-friendly, general-purpose programming language"),
    ("JavaScript", "A language commonly used for interactive websites"),
    ("Java", "An object-oriented, general-purpose programming language"),
    ("C++", "A high-performance, compiled programming language"),
]

TOPICS = [
    ("Variables", "Storing and working with data"),
    ("条件", "Making decisions with conditional statements"),
    ("Loops", "Repeating instructions"),
    ("Functions", "Reusable blocks of code"),
    ("Data Structures", "Organizing and storing information"),
]

# Each concept is linked to a topic and a programming language.
CONCEPTS = [
    ("Python variables", "Variables store values under names.", "Beginner", 1, 1),
    ("Python if statements", "If statements run code when a condition is true.", "Beginner", 2, 1),
    ("Python for loops", "For loops repeat code over a sequence.", "Beginner", 3, 1),
    ("Python functions", "Functions group reusable instructions.", "Beginner", 4, 1),
    ("Python lists", "Lists store multiple values in an ordered collection.", "Beginner", 5, 1),
    ("JavaScript variables", "Variables store values using let, const, or var.", "Beginner", 1, 2),
    ("JavaScript functions", "Functions are reusable blocks of JavaScript code.", "Beginner", 4, 2),
    ("Java classes", "Classes define the structure and behavior of objects.", "Intermediate", 4, 3),
    ("C++ pointers", "Pointers store memory addresses.", "Advanced", 5, 4),
]

EXERCISES = [
    ("Create a variable", "Create a variable called age and assign it the value 15.", "Beginner", 1),
    ("Check a number", "Write an if statement that checks whether a number is positive.", "Beginner", 2),
    ("Count to ten", "Use a for loop to print the numbers from 1 to 10.", "Beginner", 3),
    ("Create a function", "Write a function that takes two numbers and returns their sum.", "Beginner", 4),
    ("Work with lists", "Create a list of five numbers and print the first element.", "Beginner", 5),
    ("Find the maximum", "Write a function that returns the largest number in a list.", "Intermediate", 5),
]


def create_tables(cur):
    """Create our tables. DROP first so re-running gives a clean slate."""
    cur.executescript(
        """
        DROP TABLE IF EXISTS attempts;
        DROP TABLE IF EXISTS exercises;
        DROP TABLE IF EXISTS learners;
        DROP TABLE IF EXISTS concepts;
        DROP TABLE IF EXISTS topics;
        DROP TABLE IF EXISTS languages;

        CREATE TABLE languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            explanation TEXT,
            difficulty TEXT,
            topic_id INTEGER,
            language_id INTEGER,
            FOREIGN KEY (topic_id) REFERENCES topics(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );

        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            question TEXT,
            difficulty TEXT,
            concept_id INTEGER,
            FOREIGN KEY (concept_id) REFERENCES concepts(id)
        );

        CREATE TABLE learners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            exercise_id INTEGER,
            completed INTEGER,
            attempt_date TEXT,
            FOREIGN KEY (learner_id) REFERENCES learners(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );
        """
    )


def seed_lookup_tables(cur):
    """Fill the small, fixed tables: languages and topics."""
    cur.executemany(
        "INSERT INTO languages (name, description) VALUES (?, ?)",
        LANGUAGES,
    )
    cur.executemany(
        "INSERT INTO topics (name, description) VALUES (?, ?)",
        TOPICS,
    )


def seed_concepts(cur):
    """Insert programming concepts."""
    cur.executemany(
        """INSERT INTO concepts
           (name, explanation, difficulty, topic_id, language_id)
           VALUES (?, ?, ?, ?, ?)""",
        CONCEPTS,
    )


def seed_exercises(cur):
    """Insert practice exercises linked to programming concepts."""
    cur.executemany(
        """INSERT INTO exercises
           (title, question, difficulty, concept_id)
           VALUES (?, ?, ?, ?)""",
        EXERCISES,
    )


def seed_learners(cur, how_many=10):
    """Create fictional learners using Faker."""
    learners = [(fake.name(),) for _ in range(how_many)]
    cur.executemany("INSERT INTO learners (name) VALUES (?)", learners)


def seed_attempts(cur, how_many=30):
    """Create sample exercise attempts for fictional learners."""
    cur.execute("SELECT id FROM learners")
    learners = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM exercises")
    exercises = [row[0] for row in cur.fetchall()]

    attempts = []
    for _ in range(how_many):
        attempts.append((
            random.choice(learners),
            random.choice(exercises),
            random.randint(0, 1),
            fake.date_between(start_date="-3M", end_date="today").isoformat(),
        ))

    cur.executemany(
        """INSERT INTO attempts
           (learner_id, exercise_id, completed, attempt_date)
           VALUES (?, ?, ?, ?)""",
        attempts,
    )


def main():
    connection = sqlite3.connect(settings.db_path)
    cursor = connection.cursor()

    create_tables(cursor)
    seed_lookup_tables(cursor)
    seed_concepts(cursor)
    seed_exercises(cursor)
    seed_learners(cursor)
    seed_attempts(cursor)

    connection.commit()
    connection.close()
    print(f"✅ Database created at {settings.db_path}")


if __name__ == "__main__":
    main()
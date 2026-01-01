"""
Database initialization and helper functions for the Virtue Habit Tracker.
Based on Aristotelian virtue ethics: habits are formed through repeated practice.
"""

import sqlite3
from datetime import datetime, date, timedelta
from contextlib import contextmanager
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'habits.db')


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize the database with the required schema."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Resolutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                virtue TEXT,
                description TEXT,
                target_frequency TEXT DEFAULT 'daily',
                created_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # Daily check-ins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_check_ins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resolution_id INTEGER NOT NULL,
                date DATE NOT NULL,
                completed BOOLEAN NOT NULL,
                automaticity_score INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resolution_id) REFERENCES resolutions(id),
                UNIQUE(resolution_id, date)
            )
        ''')

        # Weekly reflections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resolution_id INTEGER NOT NULL,
                week_start_date DATE NOT NULL,
                balance_reflection TEXT,
                observations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resolution_id) REFERENCES resolutions(id),
                UNIQUE(resolution_id, week_start_date)
            )
        ''')

        conn.commit()


def get_week_start(target_date=None):
    """Get the Monday of the week for a given date (or today)."""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    # Get the Monday of the week (0 = Monday, 6 = Sunday)
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    return week_start


def calculate_streak(resolution_id, end_date=None):
    """
    Calculate the current streak for a resolution.
    A streak is broken by a missed day, not by an uncompleted day that wasn't checked in.
    """
    if end_date is None:
        end_date = date.today()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    with get_db() as conn:
        cursor = conn.cursor()

        # Get all check-ins for this resolution, ordered by date descending
        cursor.execute('''
            SELECT date, completed
            FROM daily_check_ins
            WHERE resolution_id = ?
            ORDER BY date DESC
        ''', (resolution_id,))

        check_ins = cursor.fetchall()

        if not check_ins:
            return 0

        # Start from today and work backwards
        current_date = end_date
        streak = 0

        # Convert check_ins to a dict for easy lookup
        check_in_dict = {
            datetime.strptime(row['date'], '%Y-%m-%d').date(): row['completed']
            for row in check_ins
        }

        # Count backwards from today
        while current_date >= datetime.strptime(check_ins[-1]['date'], '%Y-%m-%d').date():
            if current_date in check_in_dict:
                if check_in_dict[current_date]:
                    streak += 1
                else:
                    # Explicitly marked as not completed - break streak
                    break
            # If no check-in for this day, we don't break the streak yet
            # (maybe they just haven't checked in today)
            # But we only count days that are explicitly marked complete
            elif current_date < end_date:
                # If it's a past date with no check-in, break the streak
                break

            current_date -= timedelta(days=1)

        return streak


def get_completion_rate(resolution_id, days=30):
    """Calculate completion rate for a resolution over the last N days."""
    with get_db() as conn:
        cursor = conn.cursor()

        start_date = date.today() - timedelta(days=days)

        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM daily_check_ins
            WHERE resolution_id = ? AND date >= ?
        ''', (resolution_id, start_date.strftime('%Y-%m-%d')))

        result = cursor.fetchone()

        if result['total'] == 0:
            return 0.0

        return (result['completed'] / result['total']) * 100


def get_average_automaticity(resolution_id, days=30):
    """Calculate average automaticity score over the last N days."""
    with get_db() as conn:
        cursor = conn.cursor()

        start_date = date.today() - timedelta(days=days)

        cursor.execute('''
            SELECT AVG(automaticity_score) as avg_score
            FROM daily_check_ins
            WHERE resolution_id = ?
              AND date >= ?
              AND automaticity_score IS NOT NULL
              AND completed = 1
        ''', (resolution_id, start_date.strftime('%Y-%m-%d')))

        result = cursor.fetchone()
        return result['avg_score'] if result['avg_score'] else None


def get_calendar_data(resolution_id, year, month):
    """Get check-in data for a specific month for calendar display."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get first and last day of the month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        cursor.execute('''
            SELECT date, completed, automaticity_score
            FROM daily_check_ins
            WHERE resolution_id = ?
              AND date >= ?
              AND date <= ?
        ''', (resolution_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

        # Convert to dict for easy lookup (using string keys for template compatibility)
        return {
            row['date']: {
                'completed': row['completed'],
                'automaticity_score': row['automaticity_score']
            }
            for row in cursor.fetchall()
        }


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")

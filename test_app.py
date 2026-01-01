"""
Simple test script to verify the app functions correctly.
"""

import sys
from datetime import date, timedelta
from database import (
    init_db, get_db, calculate_streak, get_completion_rate,
    get_average_automaticity, get_calendar_data
)

def test_database_operations():
    """Test basic database operations."""
    print("Testing database operations...")

    # Initialize the database
    init_db()
    print("✓ Database initialized")

    with get_db() as conn:
        cursor = conn.cursor()

        # Test 1: Create a resolution
        cursor.execute('''
            INSERT INTO resolutions (name, virtue, description, created_date)
            VALUES (?, ?, ?, ?)
        ''', ('Morning Meditation', 'Mindfulness', 'Practice mindfulness through meditation', date.today().strftime('%Y-%m-%d')))
        resolution_id = cursor.lastrowid
        print(f"✓ Created resolution with ID: {resolution_id}")

        # Test 2: Add some daily check-ins
        today = date.today()
        for i in range(7):
            check_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            completed = i < 5  # Completed for the last 5 days
            automaticity = min(i + 1, 5) if completed else None

            cursor.execute('''
                INSERT INTO daily_check_ins (resolution_id, date, completed, automaticity_score, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (resolution_id, check_date, completed, automaticity, f"Day {i} notes"))

        print("✓ Created 7 daily check-ins")

        # Test 3: Calculate streak
        streak = calculate_streak(resolution_id)
        print(f"✓ Calculated streak: {streak} days")

        # Test 4: Calculate completion rate
        rate = get_completion_rate(resolution_id, days=7)
        print(f"✓ Completion rate (7 days): {rate:.1f}%")

        # Test 5: Calculate average automaticity
        avg_auto = get_average_automaticity(resolution_id, days=7)
        print(f"✓ Average automaticity: {avg_auto:.1f}" if avg_auto else "✓ Average automaticity: N/A")

        # Test 6: Get calendar data
        cal_data = get_calendar_data(resolution_id, today.year, today.month)
        print(f"✓ Retrieved calendar data: {len(cal_data)} days")

        # Test 7: Create a weekly reflection
        from database import get_week_start
        week_start = get_week_start()
        cursor.execute('''
            INSERT INTO weekly_reflections
                (resolution_id, week_start_date, balance_reflection, observations)
            VALUES (?, ?, ?, ?)
        ''', (resolution_id, week_start.strftime('%Y-%m-%d'),
              "Finding good balance", "Practice is becoming easier"))
        print("✓ Created weekly reflection")

    print("\n" + "="*50)
    print("All database tests passed! ✓")
    print("="*50)

    return True


def test_flask_imports():
    """Test that Flask app imports correctly."""
    print("\nTesting Flask app imports...")
    try:
        import app
        print("✓ Flask app imports successfully")
        print(f"✓ App has {len(app.app.url_map._rules)} routes registered")
        return True
    except Exception as e:
        print(f"✗ Failed to import Flask app: {e}")
        return False


if __name__ == '__main__':
    print("="*50)
    print("Virtue Habit Tracker - Test Suite")
    print("="*50)
    print()

    # Run tests
    db_test = test_database_operations()
    flask_test = test_flask_imports()

    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"  Database Tests: {'PASS ✓' if db_test else 'FAIL ✗'}")
    print(f"  Flask Tests: {'PASS ✓' if flask_test else 'FAIL ✗'}")
    print("="*50)

    if db_test and flask_test:
        print("\n🎉 All tests passed! Your app is ready to use.")
        print("\nTo start the app, run:")
        print("  python app.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

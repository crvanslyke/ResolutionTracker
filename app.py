"""
Virtue Habit Tracker - A habit tracking app based on Aristotelian virtue ethics.
The focus is on tracking repeated practice over time and the journey from
conscious effort to automatic habit.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
import calendar
from database import (
    init_db, get_db, calculate_streak, get_completion_rate,
    get_average_automaticity, get_calendar_data, get_week_start
)

app = Flask(__name__)
app.secret_key = 'virtue-ethics-habit-tracker-2026'  # Change this in production

# Initialize database on startup
init_db()


@app.route('/')
def index():
    """Dashboard showing all active resolutions with stats."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get all active resolutions
        cursor.execute('''
            SELECT id, name, virtue, description, created_date
            FROM resolutions
            WHERE is_active = 1
            ORDER BY created_date DESC
        ''')
        resolutions = cursor.fetchall()

        # Calculate stats for each resolution
        resolution_stats = []
        for res in resolutions:
            stats = {
                'id': res['id'],
                'name': res['name'],
                'virtue': res['virtue'],
                'description': res['description'],
                'created_date': res['created_date'],
                'streak': calculate_streak(res['id']),
                'completion_rate': round(get_completion_rate(res['id'], days=30), 1),
                'avg_automaticity': get_average_automaticity(res['id'], days=30)
            }
            if stats['avg_automaticity']:
                stats['avg_automaticity'] = round(stats['avg_automaticity'], 1)
            resolution_stats.append(stats)

        # Check if daily check-in is complete for today
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT resolution_id) as checked_in
            FROM daily_check_ins
            WHERE date = ?
        ''', (today,))
        checked_in_count = cursor.fetchone()['checked_in']

        return render_template('index.html',
                             resolutions=resolution_stats,
                             total_resolutions=len(resolutions),
                             checked_in_today=checked_in_count,
                             today=date.today())


@app.route('/resolutions')
def resolutions():
    """List all resolutions (active and inactive)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, virtue, description, created_date, is_active
            FROM resolutions
            ORDER BY is_active DESC, created_date DESC
        ''')
        all_resolutions = cursor.fetchall()

    return render_template('resolutions.html', resolutions=all_resolutions)


@app.route('/resolutions/add', methods=['GET', 'POST'])
def add_resolution():
    """Add a new resolution."""
    if request.method == 'POST':
        name = request.form.get('name')
        virtue = request.form.get('virtue')
        description = request.form.get('description')

        if not name:
            flash('Resolution name is required!', 'error')
            return redirect(url_for('add_resolution'))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO resolutions (name, virtue, description, created_date)
                VALUES (?, ?, ?, ?)
            ''', (name, virtue, description, date.today().strftime('%Y-%m-%d')))

        flash(f'Resolution "{name}" added successfully!', 'success')
        return redirect(url_for('resolutions'))

    return render_template('add_resolution.html')


@app.route('/resolutions/<int:resolution_id>/edit', methods=['GET', 'POST'])
def edit_resolution(resolution_id):
    """Edit an existing resolution."""
    with get_db() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            name = request.form.get('name')
            virtue = request.form.get('virtue')
            description = request.form.get('description')
            is_active = request.form.get('is_active') == 'on'

            cursor.execute('''
                UPDATE resolutions
                SET name = ?, virtue = ?, description = ?, is_active = ?
                WHERE id = ?
            ''', (name, virtue, description, is_active, resolution_id))

            flash('Resolution updated successfully!', 'success')
            return redirect(url_for('resolutions'))

        cursor.execute('SELECT * FROM resolutions WHERE id = ?', (resolution_id,))
        resolution = cursor.fetchone()

        if not resolution:
            flash('Resolution not found!', 'error')
            return redirect(url_for('resolutions'))

    return render_template('edit_resolution.html', resolution=resolution)


@app.route('/resolutions/<int:resolution_id>')
def resolution_detail(resolution_id):
    """Detailed view of a single resolution with calendar and history."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get resolution details
        cursor.execute('SELECT * FROM resolutions WHERE id = ?', (resolution_id,))
        resolution = cursor.fetchone()

        if not resolution:
            flash('Resolution not found!', 'error')
            return redirect(url_for('index'))

        # Get stats
        stats = {
            'streak': calculate_streak(resolution_id),
            'completion_rate_7d': round(get_completion_rate(resolution_id, days=7), 1),
            'completion_rate_30d': round(get_completion_rate(resolution_id, days=30), 1),
            'avg_automaticity': get_average_automaticity(resolution_id, days=30)
        }
        if stats['avg_automaticity']:
            stats['avg_automaticity'] = round(stats['avg_automaticity'], 1)

        # Get current month calendar data
        today = date.today()
        calendar_data = get_calendar_data(resolution_id, today.year, today.month)

        # Build calendar
        cal = calendar.monthcalendar(today.year, today.month)

        # Get recent check-ins
        cursor.execute('''
            SELECT date, completed, automaticity_score, notes
            FROM daily_check_ins
            WHERE resolution_id = ?
            ORDER BY date DESC
            LIMIT 30
        ''', (resolution_id,))
        recent_checkins = cursor.fetchall()

    return render_template('resolution_detail.html',
                         resolution=resolution,
                         stats=stats,
                         calendar=cal,
                         calendar_data=calendar_data,
                         current_month=today.strftime('%B %Y'),
                         current_year=today.year,
                         current_month_num=today.month,
                         today=today,
                         recent_checkins=recent_checkins)


@app.route('/checkin', methods=['GET', 'POST'])
def daily_checkin():
    """Daily check-in interface for all active resolutions."""
    today = date.today().strftime('%Y-%m-%d')

    with get_db() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            # Process all check-ins from the form
            cursor.execute('SELECT id FROM resolutions WHERE is_active = 1')
            active_resolutions = cursor.fetchall()

            for res in active_resolutions:
                res_id = res['id']
                completed = request.form.get(f'completed_{res_id}') == 'on'
                automaticity = request.form.get(f'automaticity_{res_id}')
                notes = request.form.get(f'notes_{res_id}')

                # Convert automaticity to int or None
                if automaticity and automaticity.strip():
                    automaticity = int(automaticity)
                else:
                    automaticity = None

                # Insert or update check-in
                cursor.execute('''
                    INSERT INTO daily_check_ins
                        (resolution_id, date, completed, automaticity_score, notes)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(resolution_id, date)
                    DO UPDATE SET
                        completed = excluded.completed,
                        automaticity_score = excluded.automaticity_score,
                        notes = excluded.notes,
                        created_at = CURRENT_TIMESTAMP
                ''', (res_id, today, completed, automaticity, notes))

            flash('Daily check-in completed!', 'success')
            return redirect(url_for('index'))

        # GET: Show check-in form
        cursor.execute('''
            SELECT r.id, r.name, r.virtue, r.description,
                   dc.completed, dc.automaticity_score, dc.notes
            FROM resolutions r
            LEFT JOIN daily_check_ins dc
                ON r.id = dc.resolution_id AND dc.date = ?
            WHERE r.is_active = 1
            ORDER BY r.name
        ''', (today,))
        resolutions = cursor.fetchall()

    return render_template('daily_checkin.html',
                         resolutions=resolutions,
                         today=today,
                         today_formatted=date.today().strftime('%A, %B %d, %Y'))


@app.route('/reflections')
def reflections():
    """View weekly reflections."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT wr.*, r.name as resolution_name
            FROM weekly_reflections wr
            JOIN resolutions r ON wr.resolution_id = r.id
            ORDER BY wr.week_start_date DESC, r.name
            LIMIT 50
        ''')
        reflections = cursor.fetchall()

    return render_template('reflections.html', reflections=reflections)


@app.route('/reflections/add', methods=['GET', 'POST'])
def add_reflection():
    """Add a weekly reflection."""
    week_start = get_week_start()

    with get_db() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            resolution_id = request.form.get('resolution_id')
            balance_reflection = request.form.get('balance_reflection')
            observations = request.form.get('observations')

            cursor.execute('''
                INSERT INTO weekly_reflections
                    (resolution_id, week_start_date, balance_reflection, observations)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(resolution_id, week_start_date)
                DO UPDATE SET
                    balance_reflection = excluded.balance_reflection,
                    observations = excluded.observations,
                    created_at = CURRENT_TIMESTAMP
            ''', (resolution_id, week_start.strftime('%Y-%m-%d'),
                  balance_reflection, observations))

            flash('Weekly reflection saved!', 'success')
            return redirect(url_for('reflections'))

        # Get active resolutions for the form
        cursor.execute('''
            SELECT id, name, virtue
            FROM resolutions
            WHERE is_active = 1
            ORDER BY name
        ''')
        active_resolutions = cursor.fetchall()

    return render_template('add_reflection.html',
                         resolutions=active_resolutions,
                         week_start=week_start.strftime('%B %d, %Y'))


@app.route('/api/toggle-resolution/<int:resolution_id>', methods=['POST'])
def toggle_resolution(resolution_id):
    """Toggle resolution active status via API."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE resolutions
            SET is_active = NOT is_active
            WHERE id = ?
        ''', (resolution_id,))

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

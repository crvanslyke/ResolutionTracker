# Virtue Habit Tracker

A simple, elegant habit tracking app based on Aristotelian virtue ethics. Track your daily practices, observe the journey from conscious effort to automatic habit, and cultivate character through repeated action.

## Philosophy

This app is grounded in Aristotle's teaching that **virtue is a habit formed through practice**. The focus is on:

- **Repeated Practice**: Habits are formed through consistent daily action
- **Automaticity**: Track how natural each practice feels over time (1-5 scale)
- **Balance**: Weekly reflections help you find the "golden mean" - not too much, not too little
- **Character Development**: Each resolution develops a specific virtue or character trait

## Features

### Core Functionality
- ✅ **Dashboard**: View all active resolutions with current streaks, completion rates, and automaticity scores
- ✅ **Daily Check-in**: Fast, streamlined interface for marking completion and rating automaticity
- ✅ **Resolution Management**: Create, edit, and manage resolutions (linked to specific virtues)
- ✅ **Calendar View**: Visual representation of practice patterns for each resolution
- ✅ **Weekly Reflections**: Structured prompts for reflection on balance and observations
- ✅ **Statistics**: Track streaks, completion rates, and automaticity trends

### Key Metrics
- **Current Streak**: Consecutive days of completed practice
- **Completion Rate**: Percentage over 7 and 30 days
- **Automaticity Score**: Average rating of how automatic/natural the practice feels (shows habituation progress)

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python database.py
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   Open your browser and go to: `http://localhost:5000`

## Usage Guide

### First Time Setup

1. **Create Your First Resolution**
   - Click "Resolutions" → "Add New Resolution"
   - Name your practice (e.g., "Morning meditation")
   - Specify the virtue it develops (e.g., "Mindfulness")
   - Add a description of what the practice involves

2. **Daily Check-in Workflow**
   - Click "Daily Check-in" in the navigation
   - Check off each completed practice
   - Rate how automatic it felt (1-5 scale, optional)
   - Add any observations in the notes field
   - Submit your check-in

3. **Track Your Progress**
   - View the dashboard to see streaks and completion rates
   - Click on any resolution to see detailed history and calendar view
   - Green days = completed, red days = missed

4. **Weekly Reflection**
   - Click "Reflections" → "Add Reflection"
   - Reflect on balance: Are you doing too much or too little?
   - Note what's working and what challenges you're facing

### Tips for Success

- **Be Consistent**: Check in daily, even if you missed a practice
- **Track Automaticity**: This helps you see habituation progress over time
- **Don't Aim for Perfection**: Aristotle emphasized finding balance, not being perfect
- **Reflect Weekly**: Use reflections to adjust your approach
- **Start Small**: Begin with 2-3 resolutions rather than overwhelming yourself

## Database Schema

The app uses SQLite with three main tables:

**resolutions**
- Stores each resolution/practice
- Links to specific virtues
- Can be marked active/inactive

**daily_check_ins**
- Records daily completion (yes/no)
- Optional automaticity score (1-5)
- Optional notes for each day
- Unique constraint: one check-in per resolution per day

**weekly_reflections**
- Structured weekly reflection on balance
- General observations about progress
- Unique constraint: one reflection per resolution per week

## File Structure

```
ResolutionTracker/
├── app.py                  # Flask application and routes
├── database.py             # Database setup and helper functions
├── habits.db              # SQLite database (created on first run)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── daily_checkin.html
│   ├── resolutions.html
│   ├── add_resolution.html
│   ├── edit_resolution.html
│   ├── resolution_detail.html
│   ├── reflections.html
│   └── add_reflection.html
└── static/
    └── style.css         # Styling
```

## Examples of Virtue-Building Practices

- **Temperance**: Limit social media to 30 minutes daily
- **Courage**: Have one difficult conversation each week
- **Justice**: Volunteer or help someone weekly
- **Wisdom**: Read philosophy/literature for 20 minutes daily
- **Discipline**: Exercise or physical training
- **Mindfulness**: Daily meditation practice
- **Generosity**: Perform one act of kindness each day

## Customization

### Changing the Port
Edit `app.py` and modify the last line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your preferred port
```

### Modifying the Color Scheme
Edit `static/style.css` and update the CSS variables at the top:
```css
:root {
    --primary-color: #2c5f8d;
    --secondary-color: #4a90a4;
    /* ... */
}
```

## Troubleshooting

**Problem**: "Address already in use" error when starting the app
- **Solution**: Another process is using port 5000. Either stop that process or change the port in `app.py`

**Problem**: Database not found
- **Solution**: Run `python database.py` to initialize the database

**Problem**: Changes not appearing
- **Solution**: Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

## Philosophy Behind the Design

This app is intentionally minimal and focused. Unlike modern habit trackers that emphasize gamification, this tool emphasizes:

1. **Reflection over Rewards**: The goal is character development, not points or streaks for their own sake
2. **Balance over Perfection**: Tracking helps you find the right level of practice
3. **Automaticity as Progress**: The real win is when practice becomes effortless
4. **Qualitative Insight**: Notes and reflections matter as much as quantitative metrics

## License

This is a personal tool provided as-is. Feel free to modify and adapt it to your needs.

## Aristotelian Wisdom

> "We are what we repeatedly do. Excellence, then, is not an act, but a habit."
> — Durant, paraphrasing Aristotle

> "Virtue is concerned with passions and actions... The mean is a matter of choosing the right amount - not too much, not too little."
> — Aristotle, Nicomachean Ethics

---

**Start your virtue journey today. Track practice, observe growth, cultivate character.**

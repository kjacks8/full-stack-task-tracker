# -----------------------------------------------------------------------------
# STEP 9: Full-Stack CRUD Application - Database Setup, Create (C) Route, and Read (R)
# This code initializes the app, defines the database model, and handles adding/viewing tasks.
# -----------------------------------------------------------------------------

from flask import Flask, render_template, url_for, request, redirect 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# --- 1. App Initialization and Configuration ---
app = Flask(__name__)

# Configure the SQLite database file path. 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 

# Initialize the database object
db = SQLAlchemy(app)

# --- 2. Database Model Definition (The structure of the data) ---

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False) # The task description
    date_created = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self):
        return f'<Task {self.id}>'

# --- 3. Initial Route (Home Page / Read Operation) ---

@app.route('/', methods=['POST', 'GET']) # Now accepts both POST (for form submission) and GET
def index():
    # If the user visits the page using the GET method (i.e., just opening the page):
    if request.method == 'GET':
        # FIX APPLIED: Added .all() to convert the ScalarResult object into a list.
        tasks = db.session.execute(db.select(Task).order_by(Task.date_created)).scalars().all()
        
        # Pass the tasks to the index.html template for display
        return render_template('index.html', title='Home', tasks=tasks)
    
    # We will remove the POST logic from here and move it to the /add route in the next step
    return redirect(url_for('index'))


# --- 4. Create Route (Handles POST request from the Add Task form) ---

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        # Get the task content from the submitted form (name='content' in index.html)
        task_content = request.form['content']
        
        # Check if content is empty (though the form is required)
        if not task_content:
            return redirect(url_for('index')) # Redirect back if empty
            
        # Create a new Task object
        new_task = Task(content=task_content)

        try:
            # Add the new task to the database session
            db.session.add(new_task)
            # Commit the session to make the change permanent
            db.session.commit()
            
            # Redirect the user back to the home page (where the task will now be listed)
            return redirect(url_for('index'))

        except Exception as e:
            # Basic error handling in case the database operation fails
            return f'There was an issue adding your task: {e}'
# --- 5. Delete Route (Handles deleting an existing task) ---

@app.route('/delete/<int:id>')
def delete(id):
    # Find the task in the database by its ID
    task_to_delete = db.get_or_404(Task, id)

    try:
        # Delete the task
        db.session.delete(task_to_delete)
        # Commit the change
        db.session.commit()
        # Redirect back to the home page
        return redirect(url_for('index'))

    except Exception as e:
        # If the deletion fails for some reason
        return f'There was a problem deleting that task: {e}'

### Your Action

#1.  **Save the HTML:** Overwrite your local `templates/index.html` with the full code I provided above (it contains the new Delete link).
#2.  **Save the Python:** Add the new `delete()` function to your local `app.py` file (and save it).
#3.  **Test Deletion:** Your server should auto-reload. Refresh your browser and try clicking the **Delete** button next to one of your tasks. It should vanish and stay gone after the page reloads!

#Let me know when deletion is working, and we'll tackle the last function, **Update (U)**!
# --- 5. Main Entry Point ---
# --- 6. Update Route (Handles displaying the form and updating the task) ---
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    # Fetch the existing task
    task = db.get_or_404(Task, id)

    if request.method == 'POST':
        # Update task content from submitted form
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f'There was an issue updating your task: {e}'

    # GET request → show edit form
    return render_template('update.html', task=task)

if __name__ == '__main__':
    # Ensure application context is active for database operations
    with app.app_context():
        # Creates the actual 'test.db' file based on the Task model
        db.create_all()
    
    # Run the application server
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error running Flask server: {e}")
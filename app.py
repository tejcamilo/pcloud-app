from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session management

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['healthcare']
patients_collection = db['patients']
history_collection = db['images']  # New collection for patient history

# Simulated database for users
users = {"admin": "admin"}  # Replace with a real authentication mechanism

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('patientList'))
        else:
            flash("Usuario o contraseña inválido", "danger")
    
    return render_template('login.html')

# Route for patient list
@app.route('/patients')
def patientList():
    if 'username' not in session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    patients = patients_collection.find()
    return render_template('patientList.html', patients=patients)

# Route for patient info
@app.route('/patients/<patient_id>')
def patientInfo(patient_id):
    if 'username' not in session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    patient = patients_collection.find_one({"id": patient_id})
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('patientList'))
    
    return render_template('patientInfo.html', patient=patient)

# Route for patient history
@app.route('/patients/<patient_id>/history')
def patientHistory(patient_id):
    if 'username' not in session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    patient = patients_collection.find_one({"id": patient_id})
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('patientList'))
    
    # Fetch patient history from the new collection
    history = history_collection.find({"patient_id": patient_id})
    
    # Fetch image and description from the new collection
    history_details = []
    for entry in history:
        history_details.append({
            "date": entry.get("timestamp"),
            "image": entry.get("image_url"),
            "description": entry.get("description")
        })
    
    return render_template('patientHistory.html', patient=patient, history=history_details)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Ha cerrado sesión", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
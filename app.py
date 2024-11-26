from flask import Flask, render_template, request, redirect, url_for, session as flask_session, flash
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session management

# Load environment variables from .env file
load_dotenv()

# Initialize the DynamoDB resource with session token
boto_session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

dynamodb = boto_session.resource('dynamodb')

# Specify the table names
patients_table = dynamodb.Table('patients')
history_table = dynamodb.Table('history')  # New table for patient history

# Simulated database for users
users = {"admin": "admin"}  # Replace with a real authentication mechanism

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            flask_session['username'] = username
            return redirect(url_for('patientList'))
        else:
            flash("Usuario o contraseña inválido", "danger")
    
    return render_template('login.html')

# Route for patient list
@app.route('/patients')
def patientList():
    if 'username' not in flask_session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    response = patients_table.scan()
    patients = response['Items']
    return render_template('patientList.html', patients=patients)

# Route for patient info
@app.route('/patients/<patient_id>')
def patientInfo(patient_id):
    if 'username' not in flask_session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    response = patients_table.get_item(Key={'_id': patient_id})
    patient = response.get('Item')
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('patientList'))
    
    return render_template('patientInfo.html', patient=patient)

# Route for patient history
@app.route('/patients/<patient_id>/history')
def patientHistory(patient_id):
    if 'username' not in flask_session:
        flash("Por favor Inicie Sesión", "warning")
        return redirect(url_for('login'))
    
    response = patients_table.get_item(Key={'_id': patient_id})
    patient = response.get('Item')
    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('patientList'))
    
    # Fetch all patient history from the history table
    response = history_table.scan()
    history = response['Items']

    # Filter history for the given patient_id
    filtered_history = [entry for entry in history if entry.get('patient_id') == patient.get('id')]
    print(filtered_history)

    
    return render_template('patientHistory.html', patient=patient, history=filtered_history)

# Route for logout
@app.route('/logout')
def logout():
    flask_session.pop('username', None)
    flash("Ha cerrado sesión", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
from importlib.util import spec_from_file_location
import os
from pydoc import doc
from sqlalchemy import desc
from flask import current_app
from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .model import Appointments, User, Doctor, Patient
from flask_login import login_user, login_required, logout_user, current_user
# make separate pages for doctors and patients (dashboards, profile, signup...)
# for now they are displaying similar information so i have used the same pages but differentiated between them using urls

view = Blueprint('view', __name__)


@view.route('/')
def home():
    return render_template('home.html')


@view.route(
    '/patient-signup',
    methods=['GET', 'POST'],
)
def patient_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        gender = request.form.get('gender')
        age = request.form.get('age')

        patient = Patient.query.filter_by(email=email).first()

        if patient:
            flash("email already exists", category="error")
        elif len(name) < 2:
            flash("name should be greater thn one character", category="error")
        elif len(password1) < 7:
            flash("password should be alteast 7 characters long", category="error")
        elif len(email) < 4:
            flash("please enter a valid email", category="error")
        elif password1 != password2:
            flash("passwords don't match", category="error")
        else:
            user = Patient(email=email,
                           name=name,
                           password=generate_password_hash(password1, method='pbkdf2:sha256'),
                           gender=gender,
                           age=age)
            db.session.add(user)
            db.session.commit()
            flash("acount created successfully!", category="success")
            return redirect(url_for("view.patient_login"))
    return render_template("signup.html", user=current_user)


@view.route('/patient-login', methods=['POST', 'GET'])
def patient_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        patient = Patient.query.filter_by(email=email).first()
        print(patient)
        if not patient:
            flash("The account does not exist. Please create another account!", category="error")
        else:
            if check_password_hash(patient.password, password):
                flash("Login successful!", category="success")
                login_user(patient)
                # return redirect(url_for("view.dashboard"))
                return redirect('patient-dashboard')
            else:
                flash("incorrect password. try again", category="error")
    return render_template('login.html', user=current_user)


@view.route('logout_patient')
# fix this(it should simply be logout-patient not get-doctor/logout_patient)
@login_required
def logout_patient():
    logout_user()
    return redirect(url_for("view.home"))


@view.route('patient-dashboard', methods=['POST', 'GET'])
@view.route('doctor-dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    return render_template("dash_home.html", user=current_user)


@view.route('patient-profile', methods=['POST', 'GET'])
@view.route('doctor-profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == 'POST':
        id = request.form.get('id')
        if request.path == "patient-profile":
            patient = Patient.query.filter_by(id=id).first()
            patient.email = request.form.get('email')
            patient.name = request.form.get('name')
            patient.age = request.form.get('age')
            patient.gender = request.form.get('gender')
        else:
            doctor = Doctor.query.filter_by(id=id).first()
            doctor.email = request.form.get('email')
            doctor.name = request.form.get('name')
            doctor.desc = request.form.get('desc')
            doctor.file_name = request.form.get('file')
        db.session.commit()
        flash("chages committed successfully!", category="success")
    return render_template('profile.html', user=current_user)


@view.route("find-doctor")
def find_doctor():
    return render_template("find_doctor.html", user=current_user)


@view.route('/doctor-login', methods=['POST', 'GET'])
def doctor_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        doctor = Doctor.query.filter_by(email=email).first()
        print(doctor)
        if not doctor:
            flash("The account does not exist. Please create another account!", category="error")
        else:
            if check_password_hash(doctor.password, password):
                flash("Login successful!", category="success")
                login_user(doctor)
                # return redirect(url_for("view.dashboard"))
                return redirect('doctor-dashboard')
            else:
                flash("incorrect password. try again", category="error")
    return render_template('login.html', user=current_user)


@view.route('/doctor-signup', methods=['GET', 'POST'])
def doctor_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        work = request.form.get('work')
        desc = request.form.get('desc')
        f = request.files['file']
        basedir = os.path.abspath(os.path.dirname(__file__))

        filename = secure_filename(f.filename)
        f.save(os.path.join(basedir, current_app.config['UPLOAD_FOLDER'], filename))
        # f.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
        doctor = Doctor.query.filter_by(email=email).first()

        if doctor:
            flash("email already exists", category="error")
        elif len(name) < 2:
            flash("name should be greater thn one character", category="error")
        elif len(password1) < 7:
            flash("password should be alteast 7 characters long", category="error")
        elif len(email) < 4:
            flash("please enter a valid email", category="error")
        elif password1 != password2:
            flash("passwords don't match", category="error")
        else:
            user = Doctor(email=email,
                          name=name,
                          password=generate_password_hash(password1, method='pbkdf2:sha256'),
                          speciality=work,
                          desc=desc,
                          file_name=os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            db.session.add(user)
            db.session.commit()
            flash("acount created successfully!", category="success")
            return redirect(url_for("view.doctor_login"))
    return render_template("signup.html", user=current_user)


@view.route('/<speciality>')
def allow(speciality):
    doctor = Doctor.query.filter_by(speciality=speciality).all()
    if doctor != []:
        return render_template("doctor_by_speciality.html", doctor=doctor, user=current_user)
    return render_template("find_doctor.html", user=current_user)


@view.route("get-doctor-<doc_name>", methods=['GET', 'POST'])
def get_doctor(doc_name):
    if request.method == "POST":
        return redirect(url_for())
    doctor = Doctor.query.filter_by(name=doc_name).first()
    if doctor:
        full_filename = doctor.file_name
        return render_template("doctor_profile.html", user=current_user, doctor=doctor, image=full_filename, code=301)
    return redirect(url_for("view.home"))


@view.route("/book-appointment-<doc_id>-<user_id>", methods=['GET', 'POST'])
def book_appointment(doc_id, user_id):
    if request.method == "POST":
        date = request.form.get('date')
        time = request.form.get('time')
        doctor = Doctor.query.filter_by(id=doc_id).first()
        a = Appointments(date=date, time=time, status="Pending")
        patient = Patient.query.filter_by(id=user_id).first()
        a.doctor = doctor
        a.patient = patient
        patient.appointments.append(a)
        flash("request made! VIEW IN APPOINTMENTS", category="success")
        db.session.commit()
    return render_template('book_appointment.html', user=current_user)


@view.route("doctor-show-appointments-<user_id>")
@view.route("patient-show-appointments-<user_id>")
def show_appointments(user_id):
    # use a better way to check which user
    if request.path.startswith('/doctor-'):
        doctor = Doctor.query.filter_by(id=user_id).first()
        a = doctor.appointments

    else:
        patient = Patient.query.filter_by(id=user_id).first()
        a = patient.appointments

    return render_template("appointments.html", user=current_user, appointments=a)


@view.route("doctor-update-appointment-<patient_id>-<doctor_id>", methods=['GET', 'POST'])
def update_appointments(patient_id, doctor_id):
    if request.method == 'POST':
        a = Appointments.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if request.form['button'] == 'accept':
            a.status = "Accepted"
        elif request.form['button'] == 'decline':
            a.status = "Declined"
        doctor = Doctor.query.filter_by(id=doctor_id).first()
        a = doctor.appointments
        db.session.commit()
    return render_template("appointments.html", user=current_user, appointments=a)

from sqlalchemy import desc
from . import db
from flask_login import UserMixin


# appointments = db.Table('appointments',
#                         db.Column('doctor_id', db.Integer,
#                                   db.ForeignKey('doctor.id')),
#                         db.Column('patient_id', db.Integer,
#                                   db.ForeignKey('patient.id'))
#                        )
class Appointments(db.Model):
    __tablename__ = "appointments"
    doctor_id = db.Column(db.ForeignKey("doctor.id"), primary_key=True)
    patient_id = db.Column(db.ForeignKey("patient.id"), primary_key=True)
    date = db.Column(db.String(150), primary_key=True)
    time = db.Column(db.String(150), primary_key=True)
    status = db.Column(db.String(150))
    doctor = db.relationship("Doctor", back_populates="appointments")
    patient = db.relationship("Patient", back_populates="appointments")


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __mapper_args__ = {'polymorphic_identity': 'user'}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    password = db.Column(db.String(150))


class Doctor(User):
    __tablename__ = 'doctor'
    __mapper_args__ = {'polymorphic_identity': 'doctor'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    speciality = db.Column(db.String(150))
    desc = db.Column(db.String(5000))
    file_name = db.Column(db.String(150))
    # appointments = db.relationship(
    #     'Patient', secondary = appointments, backref = 'appointments')
    appointments = db.relationship("Appointments", back_populates="doctor")
    #appointments = db.relationship("Patient", secondary="appointments")


class Patient(User):
    __tablename__ = 'patient'
    __mapper_args__ = {'polymorphic_identity': 'patient'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    gender = db.Column(db.String(150))
    age = db.Column(db.Integer)
    appointments = db.relationship("Appointments", back_populates="patient")

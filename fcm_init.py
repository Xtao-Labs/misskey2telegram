import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("data/google.json")
google_app = firebase_admin.initialize_app(cred)

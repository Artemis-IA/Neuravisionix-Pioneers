from app import db
import hashlib
from sqlalchemy import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'utilisateur'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum('admin', 'utilisateur'), nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role
        }

    def get_all_users():
        users = User.query.all()
        return users

    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role

    def hash_password(self, password):
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return hashed_password
    def check_password(self, password):
        # Compare the hashed password with the provided password
        return self.password == self.hash_password(password)
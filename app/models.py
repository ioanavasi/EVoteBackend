from sqlalchemy import Integer, VARCHAR
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db
import uuid

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid = mapped_column(VARCHAR(36), default=lambda: str(uuid.uuid4()), unique=True)
    cnp = mapped_column(VARCHAR(13), unique=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'cnp': self.cnp,
            'email': self.email,
            'fist_name': self.first_name,
            'last_name': self.last_name
        }

    def __repr__(self):
        return f'<User {self.cnp}>'
from sqlalchemy import Integer, VARCHAR, ForeignKey, BigInteger, Text, UniqueConstraint
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
    first_name = mapped_column(VARCHAR(255))
    last_name = mapped_column(VARCHAR(255))

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'cnp': self.cnp,
            'email': self.email,
            'fist_name': self.first_name,
            'last_name': self.last_name
        }
    
class Candidate(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    election_id = mapped_column(Integer, ForeignKey('election.id'))
    name = mapped_column(VARCHAR(255))
    party = mapped_column(VARCHAR(255))
    slogan = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'election_id', name='unique_candidate_election'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'election_id': self.election_id,
            'name': self.name,
            'party': self.party,
            'slogan': self.slogan
        }

class Election(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(VARCHAR(255), unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Vote(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_uuid = mapped_column(VARCHAR(36), ForeignKey('user.uuid'))
    candidate_id = mapped_column(Integer, ForeignKey('candidate.id'))
    election_id = mapped_column(Integer, ForeignKey('election.id'))
    timestamp = mapped_column(BigInteger)
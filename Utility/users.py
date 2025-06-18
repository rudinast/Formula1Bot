from sqlmodel import Session, select

from Models.user_models import User
from db.db import engine

def select_all_users():
    with Session(engine) as session:
        statement = select(User)
        res = session.exec(statement).all()
        return res

def find_user(name):
    with Session(engine) as session:
        statement = select(User).where(User.username == name)
        return session.exec(statement).first()

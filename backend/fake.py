from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import aliased, sessionmaker
from fastapi_users.db import SQLAlchemyUserDatabase

from core.models.user import User


DATABASE_URL = f"postgresql+psycopg2://postgres:postgres@localhost:5433/medportal"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

user_db = SQLAlchemyUserDatabase(User, SessionLocal())

fake = Faker("ru_RU")

num_users = 10000


def generate_fake_users(session, num_users=num_users):
    users_data = []

    for _ in range(num_users):
        user_data = {
            'email': fake.email(),
            'username': fake.user_name(),
            'registered_at': fake.date_time_this_decade(),
            'role_id': 2,

            'name': fake.first_name(),
            'surname': fake.last_name(),
            'fathername': fake.first_name_male() if fake.boolean(chance_of_getting_true=50) else fake.first_name_female(),
            'phone': fake.phone_number(),

            'hashed_password': fake.password(length=12),
            'is_active': fake.boolean(),
            'is_superuser': fake.boolean(),
            'is_verified': fake.boolean(),
            'verification_token': str(fake.uuid4()),
        }
        users_data.append(user_data)

    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
    session.commit()


generate_fake_users(session, num_users)
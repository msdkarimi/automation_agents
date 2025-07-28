from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 

_user = os.environ.get('postgres_user')
_pass = os.environ.get('postgres_pass')
_db_name = os.environ.get('postgres_db_name')

# 1. Connect to the PostgreSQL database
DATABASE_URL = f"postgresql+psycopg2://{_user}:{_pass}@localhost/{_db_name}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 2. Define the base class
Base = declarative_base()

# 3. Define the table as a Python class
class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    department = Column(String(50))

# 4. Create the table (if it doesn’t exist)
Base.metadata.create_all(engine)

# 5. Insert a row using ORM
new_employee = Employee(name="Alice", age=30, department="HR")
session.add(new_employee)
session.commit()

# 6. (Optional) Query and print all employees
for emp in session.query(Employee).all():
    print(emp.id, emp.name, emp.age, emp.department)

# 7. Close the session
session.close()
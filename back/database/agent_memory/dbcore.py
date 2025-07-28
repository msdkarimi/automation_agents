from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # import the same Base used by models


__all__ = ['DBCore']

class DBCore:
    def __init__(self, user_name, password, db_name, verbose=False):
        self.engine = create_engine(f"postgresql+psycopg2://{user_name}:{password}@localhost/{db_name}")
        self.Session = sessionmaker(bind=self.engine)
        self.verbose = verbose

    def __enter__(self):
        print('opened')
        Base.metadata.create_all(self.engine)  # creates tables for all models on this Base
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('closed')
        if exc_val is not None:
            self.session.rollback()
        else:
            self.session.commit()
        
        self.session.close()
        self.engine.dispose() 
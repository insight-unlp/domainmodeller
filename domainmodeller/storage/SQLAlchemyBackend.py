from domainmodeller.storage import schema
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class SQLAlchemyBackend:
    def __init__(self, engine):
        self.engine = engine
        self.meta = schema.Base.metadata  # @UndefinedVariable
        self.SessionMaker = sessionmaker(bind=self.engine)

    def clear(self):
        for tbl in reversed(self.meta.sorted_tables):
            try:
                tbl.drop(self.engine)
            except:
                pass
        self.create_tables()

    def create_tables(self):
        self.meta.create_all(self.engine)

    def make_session(self):
        return self.SessionMaker()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        # See SQLAlchemy docs:
        # "When do I construct a Session, when do I commit it, and when do I close it ?"
        session = self.SessionMaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def session(self):
        return self.SessionMaker()
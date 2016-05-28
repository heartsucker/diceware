from os import path
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


sqlite_file = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'temp', 'sqlite.db')

engine = create_engine('sqlite:///' + sqlite_file)

db_session = sessionmaker(bind=engine)()

Base = declarative_base()


class WordList(Base):
    __tablename__ = 'wordlist'
    language = Column(String, primary_key=True, nullable=False)
    word = Column(String, primary_key=True, nullable=False)
    state = Column(Integer, nullable=False)

    def __repr__(self):
        return 'WordList<language={language}, word={word}, state={state}>'.format(language=self.language,
                                                                                  word=self.word,
                                                                                  state=self.state,
                                                                                  )
word_states = [
    'pending',
    'accepted',
    'rejected',
    'skipped',
]

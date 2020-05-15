import sqlalchemy
from sqlalchemy import orm, Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext import declarative
import os

sql_alchemy_base = declarative.declarative_base()
object_types_enum = Enum('champion', 'item', 'rune')


class LolObject(sql_alchemy_base):
    """Represents a LoL-related object with its ID, name, locale, and object type.
    """
    __tablename__ = 'lol_id'

    # The id from Riot
    id = Column(Integer, primary_key=True)

    # The locale the name is in
    locale = Column(String, primary_key=True)

    # The name in the given locale
    name = Column(String)

    # The object type, might need a change in the future
    object_type = Column(object_types_enum)

    def __init__(self, id_, locale_, name_, object_type_):
        self.id = id_
        self.locale = locale_
        self.name = name_
        self.object_type = object_type_


class GhostSession:
    """A ghost loader for our sqlalchemy session

    This makes it sure we do not create the session and schema during module import.
    """
    session = None

    @classmethod
    def get_session(cls):
        if not cls.session:
            data_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')
            if not os.path.exists(data_folder):
                os.mkdir(data_folder)

            engine = sqlalchemy.create_engine(f'sqlite:///{os.path.join(data_folder, "lol_id_tools.db")}')
            sql_alchemy_base.metadata.create_all(engine)
            cls.session = orm.sessionmaker(bind=engine)()
        return cls.session


# The ghost session function
ghost_session = GhostSession.get_session

##


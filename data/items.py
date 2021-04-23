import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_available = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    about_on_page = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return "<Item> {}, price - {}, category - {}".format(self.title, self.price, self.category)
from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKeyConstraint

Base = declarative_base()


class User(Base):

    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, primary_key=True)

    username = Column(String(32), nullable=True)
    name = Column(String(100), nullable=False)

    reputation = Column(Integer, default=0, nullable=False)

    voted = relationship(
        "UserVotes",
        backref="fromuser",
        foreign_keys="UserVotes.from_user_id",
        primaryjoin="and_(User.user_id==UserVotes.from_user_id, "
        "User.group_id==UserVotes.group_id)",
    )
    votes = relationship(
        "UserVotes",
        backref="touser",
        foreign_keys="UserVotes.to_user_id",
        primaryjoin="and_(User.user_id==UserVotes.to_user_id, "
        "User.group_id==UserVotes.group_id)",
    )

    __table_args__ = (ForeignKeyConstraint(["group_id"], ["group.group_id"],
                                           name="fk_group_id"), )

    def __str__(self):
        return (f'<a href="tg://user?id={self.user_id}">'
                f"{self.name}</a> [{self.reputation}]")

    def __eq__(self, other):
        if isinstance(other, User):
            return (self.user_id == other.user_id
                    and self.username == other.username
                    and self.group_id == other.group_id
                    and self.name == other.name)
        return False

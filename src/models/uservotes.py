from datetime import datetime
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKeyConstraint

Base = declarative_base()
class UserVotes(Base):

    __tablename__ = "uservotes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(BigInteger, nullable=False)

    from_user_id = Column(BigInteger, nullable=False)
    to_user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    vote = Column(SmallInteger)

    voted_at = Column(DateTime, default=datetime.now())
    __table_args__ = (
        ForeignKeyConstraint(
            ["from_user_id", "group_id"],
            ["user.user_id", "user.group_id"],
            name="fk_from_group_id",
        ),
        ForeignKeyConstraint(
            ["to_user_id", "group_id"],
            ["user.user_id", "user.group_id"],
            name="fk_to_group_id",
        ),
    )

    def __str__(self):
        if self.vote == 1:
            return f"{self.fromuser} votó a {self.touser} con +1"

        return f"{self.fromuser} votó a {self.touser} con -1"


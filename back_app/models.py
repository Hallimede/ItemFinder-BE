from sqlalchemy import DateTime, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(Integer, unique=True, index=True)
    password = Column(String)
    lock_password = Column(Integer)
    # TODO: 锁屏密码 低优先级 待补充

    items = relationship("Item", back_populates="owner")
    spaces = relationship("Space", back_populates="owner")
    inventory = relationship("Inventory", back_populates="owner")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    unique = UniqueConstraint(name, owner_id)
    position_id = Column(Integer, ForeignKey("spaces.id"))

    owner = relationship("User", back_populates="items")
    position = relationship("Space", back_populates="items")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    room = Column(String)
    # TODO: 房间是否单独列表？

    owner_id = Column(Integer, ForeignKey("users.id"))
    address = UniqueConstraint(name, room, owner_id)

    items = relationship("Item", back_populates="position")
    owner = relationship("User", back_populates="spaces")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    space_id = Column(Integer, ForeignKey("spaces.id"))
    time = Column(DateTime)

    owner = relationship("User", back_populates="inventory")

    # TODO: item和space是否要定义相同的？

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

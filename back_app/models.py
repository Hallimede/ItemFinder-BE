from sqlalchemy import DateTime, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(Integer, unique=True, index=True)
    password = Column(String)
    # image = Column(String)
    # lock_password = Column(Integer) 计划存在客户端本地
    # TODO: 锁屏密码 低优先级 待补充

    items = relationship("Item", back_populates="owner")
    rooms = relationship("Room", back_populates="owner")
    storage_spaces = relationship("StorageSpace", back_populates="owner")
    inventory = relationship("Inventory", back_populates="owner")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    unique = UniqueConstraint(name, owner_id)
    # position_id = Column(Integer, ForeignKey("spaces.id"))
    image = Column(String)

    owner = relationship("User", back_populates="items")
    inventory = relationship("Inventory", back_populates="item")

    # position = relationship("Space", back_populates="items")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# class Space(Base):
#     __tablename__ = "spaces"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     room = Column(String)
#
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     address = UniqueConstraint(name, room, owner_id)
#
#     items = relationship("Item", back_populates="position")
#     owner = relationship("User", back_populates="spaces")
#
#     def to_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    storage_spaces = relationship("StorageSpace", back_populates="position")

    owner = relationship("User", back_populates="rooms")
    inventory = relationship("Inventory", back_populates="room")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StorageSpace(Base):
    __tablename__ = "storage_spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    image = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="storage_spaces")
    position = relationship("Room", back_populates="storage_spaces")
    inventory = relationship("Inventory", back_populates="storage_space")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    info = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    storage_space_id = Column(Integer, ForeignKey("storage_spaces.id"))
    time = Column(DateTime)

    unique = UniqueConstraint(room_id, storage_space_id, owner_id, id)
    owner = relationship("User", back_populates="inventory")
    item = relationship("Item", back_populates="inventory")
    room = relationship("Room", back_populates="inventory")
    storage_space = relationship("StorageSpace", back_populates="inventory")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

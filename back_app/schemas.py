from typing import List

from datetime import datetime
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int
    # position_id: int

    class Config:
        orm_mode = True


# class SpaceBase(BaseModel):
#     name: str
#     room: str
#
#
# class SpaceCreate(SpaceBase):
#     pass
#
#
# class SpaceUpdate(SpaceBase):
#     pass
#
#
# class Space(SpaceBase):
#     id: int
#     owner_id: int
#     items: List[Item] = []
#
#     class Config:
#         orm_mode = True

class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    name: str
    owner_id: int

    class Config:
        orm_mode = True


class StorageSpaceBase(BaseModel):
    room_id: int


class StorageSpaceCreate(StorageSpaceBase):
    name: str


class StorageSpaceUpdate(StorageSpaceBase):
    name: str


class StorageSpace(StorageSpaceBase):
    id: int
    name: str
    owner_id: int
    room_id: int

    class Config:
        orm_mode = True


class InventoryBase(BaseModel):
    item_id: int
    room_id: int
    storage_space_id: int


class InventoryRelate(InventoryBase):
    time: datetime = datetime.now()


#
# class InventoryUpdate(InventoryBase):
#     time: datetime = datetime.now()
#     # TODO: 是否需要加id


class Inventory(BaseModel):
    id: int
    owner_id: int
    item_id: int
    room_id: int
    storage_space_id: int
    time: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    phone_number: str


class UserCreate(UserBase):
    password: str
    name: str


class UserLogin(UserBase):
    password: str


class UserUpdate(UserBase):
    name: str = None
    password: str = None


class User(UserBase):
    id: int
    name: str

    # items: List[Item] = []
    # spaces: List[Space] = []
    # inventory: List[Inventory] = []

    class Config:
        orm_mode = True


class UserAll(UserBase):
    id: int
    name: str
    password: str

    items: List[Item] = []
    rooms: List[Room] = []
    storage_spaces: List[StorageSpace] = []
    inventory: List[Inventory] = []

    class Config:
        orm_mode = True

class LoginFeedback(BaseModel):
    code: int
    message: str
    user: User

from typing import List

from datetime import datetime
from pydantic import BaseModel


class ItemQuery(BaseModel):
    item_id: int


class StorageSpaceQuery(BaseModel):
    storage_space_id: int


class ItemBase(BaseModel):
    name: str


class ItemCreate(ItemBase):
    image: str = None


class ItemUpdate(ItemBase):
    image: str = None


class Item(ItemBase):
    id: int
    owner_id: int
    image: str = None

    # position_id: int

    class Config:
        orm_mode = True


class StorageSpaceBase(BaseModel):
    room_id: int


class StorageSpaceCreate(StorageSpaceBase):
    image: str = None
    name: str


class StorageSpaceUpdate(StorageSpaceBase):
    image: str = None
    name: str


class StorageSpace(StorageSpaceBase):
    id: int
    name: str
    owner_id: int
    room_id: int
    image: str = None

    class Config:
        orm_mode = True


class Space(BaseModel):
    room_id: int
    storage_space_id: int


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    image: str = None


class RoomUpdate(RoomBase):
    image: str = None


class Room(RoomBase):
    id: int
    name: str
    owner_id: int
    image: str = None
    storage_spaces: List[StorageSpace] = []

    class Config:
        orm_mode = True


class InventoryBase(BaseModel):
    item_id: int
    room_id: int
    storage_space_id: int


class InventoryRelate(InventoryBase):
    time: datetime = datetime.now()
    info: str = None


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
    info: str = None

    item: Item
    room: Room
    storage_space: StorageSpace

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

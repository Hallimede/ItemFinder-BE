from sqlalchemy.orm import Session, joinedload

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def login(db: Session, log_in: schemas.UserLogin):
    db_user = get_user_by_phone(db, log_in.phone_number)
    res = schemas.LoginFeedback(user=schemas.User(phone_number=0, id=0, name=""), code=404, message="Login failed")
    if db_user:
        if db_user.password == log_in.password + "notreallyhashed":
            res.user = db_user
            res.code = 200
            res.message = "Login successfully"
    return res


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(phone_number=user.phone_number, name=user.name, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, update_user: schemas.UserUpdate):
    if update_user.password:
        update_user.password += "notreallyhashed"
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_dict = update_user.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_user, k, v)
        db.commit()
        db.flush()
        db.refresh(db_user)
        return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        db.flush()
        return db_user


def get_items(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == owner_id).offset(skip).limit(limit).all()


def get_items_by_space(db: Session, owner_id: int, space: schemas.Space, skip: int = 0, limit: int = 100):
    return db.query(models.Item).join(models.Inventory, models.Inventory.item_id == models.Item.id).filter(
        models.Inventory.owner_id == owner_id).filter(
        models.Inventory.room_id == space.room_id).filter(
        models.Inventory.storage_space_id == space.storage_space_id).offset(skip).limit(limit).all()


def get_item(db: Session, item_id):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_item_by_owner_and_name(db: Session, owner_id: int, item_name):
    return db.query(models.Item).filter(models.Item.owner_id == owner_id).filter(models.Item.name == item_name).first()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def relate_user_item(db: Session, user_id: int, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.owner_id = user_id
        db.commit()
        db.flush()
        return db.query(models.User).filter(models.User.id == user_id).first()


def update_item(db: Session, item_id: int, update_item: schemas.ItemUpdate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        update_dict = update_item.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_item, k, v)
        db.commit()
        db.flush()
        db.refresh(db_item)
        return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        db.flush()
        return db_item

def get_rooms(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Room).filter(models.Room.owner_id == owner_id).offset(skip).limit(limit).all()


def get_storage_spaces(db: Session, owner_id: int, room_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.StorageSpace).filter(models.StorageSpace.owner_id == owner_id).filter(
        models.StorageSpace.room_id == room_id).offset(skip).limit(limit).all()


def get_user_all_storage_spaces(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.StorageSpace).filter(models.StorageSpace.owner_id == owner_id).offset(skip).limit(
        limit).all()


def get_room_by_id(db: Session, room_id):
    return db.query(models.Room).filter(models.Room.id == room_id).first()


def get_storage_space_by_id(db: Session, storage_space_id):
    return db.query(models.StorageSpace).filter(models.StorageSpace.id == storage_space_id).first()


def get_room_by_name(db: Session, owner_id: int, name):
    return db.query(models.Room).filter(models.Room.owner_id == owner_id).filter(models.Room.name == name).first()


def get_storage_space_by_name_and_room(db: Session, owner_id: int, base_storage_space):
    return db.query(models.StorageSpace).filter(models.StorageSpace.owner_id == owner_id).filter(
        models.StorageSpace.room_id == base_storage_space.room_id).filter(
        models.StorageSpace.name == base_storage_space.name).first()


def create_user_room(db: Session, room: schemas.RoomCreate, user_id: int):
    db_room = models.Room(**room.dict(), owner_id=user_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def create_user_storage_space(db: Session, storage_space: schemas.StorageSpaceCreate, user_id: int):
    db_room = models.StorageSpace(**storage_space.dict(), owner_id=user_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def update_room(db: Session, room_id: int, update_room: schemas.RoomUpdate):
    db_room = get_room_by_id(db, room_id)
    if db_room:
        update_dict = update_room.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_room, k, v)
        db.commit()
        db.flush()
        db.refresh(db_room)
        return db_room


def update_storage_space(db: Session, storage_space_id: int, update_storage_space: schemas.StorageSpaceUpdate):
    db_storage_space = get_storage_space_by_id(db, storage_space_id)
    if db_storage_space:
        update_dict = update_storage_space.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_storage_space, k, v)
        db.commit()
        db.flush()
        db.refresh(db_storage_space)
        return db_storage_space


def delete_room(db: Session, room_id: int):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
        db.flush()
        return db_room


def delete_storage_space(db: Session, storage_space_id: int):
    db_storage_space = db.query(models.StorageSpace).filter(models.StorageSpace.id == storage_space_id).first()
    if db_storage_space:
        db.delete(db_storage_space)
        db.commit()
        db.flush()
        return db_storage_space


def get_inventory(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Inventory).offset(skip).limit(limit).all()


def get_inventory_by_item(db: Session, owner_id: int, item_id: int):
    return db.query(models.Inventory).filter(models.Inventory.owner_id == owner_id).filter(
        models.Inventory.item_id == item_id).first()


def get_inventory_by_space(db: Session, owner_id: int, storage_space_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inventory).filter(models.Inventory.owner_id == owner_id).filter(
        models.Inventory.storage_space_id == storage_space_id).offset(skip).limit(limit).all()


def find_storage_space_in_room(db: Session, ivt_item: schemas.InventoryRelate, owner_id: int):
    return db.query(models.StorageSpace).filter(models.StorageSpace.owner_id == owner_id).filter(
        models.StorageSpace.id == ivt_item.storage_space_id).filter(
        models.StorageSpace.room_id == ivt_item.room_id).first()


def relate_user_inventory(db: Session, ivt_item: schemas.InventoryRelate, owner_id: int):
    db_ivt_item = db.query(models.Inventory).filter(models.Inventory.owner_id == owner_id).filter(
        models.Inventory.item_id == ivt_item.item_id).first()
    if db_ivt_item is None:
        db_ivt_item = models.Inventory(**ivt_item.dict(), owner_id=owner_id)
        db.add(db_ivt_item)
        db.commit()
    else:
        update_dict = ivt_item.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_ivt_item, k, v)
        db.commit()
        db.flush()
    return db_ivt_item


def delete_inventory(db: Session, item_id: int):
    db_ivt_item = db.query(models.Inventory).options(joinedload('item')).options(joinedload('room')).options(
        joinedload('storage_space')).filter(models.Inventory.item_id == item_id).first()
    if db_ivt_item:
        db.delete(db_ivt_item)
        db.commit()
        db.flush()
        return db_ivt_item

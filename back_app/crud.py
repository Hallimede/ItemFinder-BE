from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(phone_number=user.phone_number, name=user.name, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# TODO: 创建时不包括lock-password


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


def get_items(db: Session, owner_id : int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == owner_id).offset(skip).limit(limit).all()


def get_item(db: Session, item_id):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_item_by_owner_and_name(db: Session, owner_id: int, item_name):
    return db.query(models.Item).filter(models.Item.owner_id == owner_id).filter(models.Item.name == item_name).first()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id, position_id=0)
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


def get_spaces(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Space).filter(models.Space.owner_id == owner_id).offset(skip).limit(limit).all()


def get_space(db: Session, space_id):
    return db.query(models.Space).filter(models.Space.id == space_id).first()


def get_space_by_owner_name_and_room(db: Session, owner_id: int, space_name, space_room):
    return db.query(models.Space).filter(models.Space.owner_id == owner_id).filter(
        models.Space.name == space_name).filter(models.Space.room == space_room).first()


def create_user_space(db: Session, space: schemas.SpaceCreate, user_id: int):
    db_space = models.Space(**space.dict(), owner_id=user_id)
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space


def relate_user_space(db: Session, user_id: int, space_id: int):
    db_space = db.query(models.Space).filter(models.Space.id == space_id).first()
    if db_space:
        db_space.owner_id = user_id
        db.commit()
        db.flush()
        return db.query(models.User).filter(models.User.id == user_id).first()


def update_space(db: Session, space_id: int, update_space: schemas.SpaceUpdate):
    db_space = db.query(models.Space).filter(models.Space.id == space_id).first()
    if db_space:
        update_dict = update_space.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_space, k, v)
        db.commit()
        db.flush()
        db.refresh(db_space)
        return db_space


def delete_space(db: Session, space_id: int):
    db_space = db.query(models.Space).filter(models.Space.id == space_id).first()
    if db_space:
        db.delete(db_space)
        db.commit()
        db.flush()
        return db_space


def get_inventory(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Inventory).offset(skip).limit(limit).all()


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
    db_item = db.query(models.Item).filter(models.Item.id == db_ivt_item.item_id).first()
    db_item.position_id = db_ivt_item.space_id
    db.commit()
    db.refresh(db_ivt_item)
    return db_ivt_item


# TODO: relate = create + update
# def relate_user_inventory(db: Session, user_id: int, inventory_id: int):
#     db_ivt_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
#     if db_ivt_item:
#         db_ivt_item.owner_id = user_id
#         db.commit()
#         db.flush()
#         return db.query(models.User).filter(models.User.id == user_id).first()

#
# def update_inventory(db: Session, inventory_id: int, update_inventory: schemas.InventoryUpdate):
#     db_ivt_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
#     if db_ivt_item:
#         update_dict = update_inventory.dict(exclude_unset=True)
#         for k, v in update_dict.items():
#             setattr(db_ivt_item, k, v)
#         db.commit()
#         db.flush()
#         db.refresh(db_ivt_item)
#         return db_ivt_item


def delete_inventory(db: Session, inventory_id: int):
    db_ivt_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if db_ivt_item:
        db.delete(db_ivt_item)
        db.commit()
        db.flush()
        return db_ivt_item

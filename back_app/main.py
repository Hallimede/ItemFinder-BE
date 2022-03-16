from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone_number=user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone Number already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login/", response_model=schemas.LoginFeedback)
def login(log_in: schemas.UserLogin, db: Session = Depends(get_db)):
    db_res = crud.login(db, log_in=log_in)
    if db_res is None:
        raise HTTPException(status_code=404, detail="Login failed")
    return db_res


@app.delete('/users/{user_id}', response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, update_user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, update_user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# TODO: 可以为不存在的用户创建 item
@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_owner_and_name(db, owner_id=user_id, item_name=item.name)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already registered")
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/{user_id}", response_model=List[schemas.Item])
def read_items(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, owner_id=user_id, skip=skip, limit=limit)
    return items


# @app.put("/items/{user_id}/{item_id}/", response_model=schemas.User)
# def relate_user_item(user_id: int, item_id: int, db: Session = Depends(get_db)):
#     user = crud.relate_user_item(db=db, item_id=item_id, user_id=user_id)
#     return user


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, update_item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    same_item = crud.get_item_by_owner_and_name(db, owner_id=db_item.owner_id, item_name=update_item.name)
    if same_item:
        raise HTTPException(status_code=400, detail="Item already registered")
    updated_item = crud.update_item(db, item_id, update_item)
    # if updated_item is None:
    #     raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@app.delete('/items/{item_id}', response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.post("/users/{user_id}/spaces/", response_model=schemas.Space)
def create_space_for_user(user_id: int, space: schemas.SpaceCreate, db: Session = Depends(get_db)):
    db_space = crud.get_space_by_owner_name_and_room(db, owner_id=user_id, space_name=space.name,
                                                     space_room=space.room)
    if db_space:
        raise HTTPException(status_code=400, detail="Space already registered")
    return crud.create_user_space(db=db, space=space, user_id=user_id)


@app.get("/spaces/{user_id}", response_model=List[schemas.Space])
def read_spaces(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    spaces = crud.get_spaces(db, owner_id=user_id, skip=skip, limit=limit)
    return spaces


# @app.put("/items/{user_id}/{item_id}/", response_model=schemas.User)
# def relate_user_item(user_id: int, item_id: int, db: Session = Depends(get_db)):
#     user = crud.relate_user_item(db=db, item_id=item_id, user_id=user_id)
#     return user


@app.put("/spaces/{space_id}", response_model=schemas.Space)
def update_space(space_id: int, update_space: schemas.SpaceUpdate, db: Session = Depends(get_db)):
    db_space = crud.get_space(db, space_id)
    if db_space is None:
        raise HTTPException(status_code=404, detail="Space not found")
    same_space = crud.get_space_by_owner_name_and_room(db, owner_id=db_space.owner_id, space_name=update_space.name,
                                                       space_room=update_space.room)
    if same_space:
        raise HTTPException(status_code=400, detail="Space already registered")
    updated_space = crud.update_space(db, space_id, update_space)
    return updated_space


@app.delete('/spaces/{space_id}', response_model=schemas.Space)
def delete_space(space_id: int, db: Session = Depends(get_db)):
    db_space = crud.delete_space(db, space_id=space_id)
    if db_space is None:
        raise HTTPException(status_code=404, detail="Space not found")
    return db_space


# TODO: 可以为不存在的用户、item和空间创建
@app.post("/users/{user_id}/ivt/", response_model=schemas.Inventory)
def relate_inventory_for_user(user_id: int, ivt_item: schemas.InventoryRelate, db: Session = Depends(get_db)):
    # db_space = crud.get_space_by_owner_name_and_room(db, owner_id=user_id, space_name=space.name,
    #                                                  space_room=space.room)
    # if db_space:
    #     raise HTTPException(status_code=400, detail="Space already registered")
    return crud.relate_user_inventory(db=db, ivt_item=ivt_item, owner_id=user_id)


# @app.delete('/ivt/{ivt_id}', response_model=schemas.Inventory)
# def delete_inventory(ivt_id: int, db: Session = Depends(get_db)):
#     db_ivt_item = crud.delete_inventory(db, inventory_id=ivt_id)
#     if db_ivt_item is None:
#         raise HTTPException(status_code=404, detail="Inventory not found")
#     return db_ivt_item

@app.delete('/ivt/{item_id}', response_model=schemas.Inventory)
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    db_ivt_item = crud.delete_inventory(db, item_id=item_id)
    if db_ivt_item is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return db_ivt_item
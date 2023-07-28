import hashlib
from typing import List
from pathlib import Path
from fastapi import Request, File
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .extensions.logger import logger
import time

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

LIMIT_SIZE = 5 * 1024 * 1024  # 5M
# BASE_DIR = Path(__file__).resolve().parent
# BASE_DIR = Path('/Users/hallimede/Documents/')
BASE_DIR = Path('/root/images/')


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@logger.catch  # 异常记录装饰器、放到下面好像不行、应该是异步的关系。
def my_function(x, y, z):
    return [x, y, z]


@app.post('/')
async def root(data: dict):
    # get 请求
    logger.debug(f"这是日志！")
    logger.info('这是user接口：username={},当前时间戳为：{tiems}', data["username"], tiems=time.time())
    my_function(0, 0)
    return {'message': 'Hello World!'}


@app.post("/upload/pic/", summary="上传图片")
async def upload_image(request: Request, file: bytes = File(...)):
    logger.debug(f"这是日志！")
    logger.info('这是upload pic接口 {content}\nmethod ={method}\n当前时间戳为：{times}',
                content=request.headers.get("content-type"),
                method=request.method,
                times=time.time())
    if len(file) > LIMIT_SIZE:
        raise HTTPException(status_code=400, detail="每个文件都不能大于5M")
    name = hashlib.md5(file).hexdigest() + ".png"  # 使用md5作为文件名，以免同一个文件多次写入
    path = "http://124.223.160.213/www"
    # subpath = "www"
    # if not (folder := BASE_DIR / subpath).exists():
    #     await AsyncPath(folder).mkdir(parents=True)
    # if not (fpath := folder / name).exists():
    with open(BASE_DIR + name, 'wb') as f:
        f.write(file)
    return f"{path}/{name}"


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone_number=user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone Number already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.UserAll])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"这是日志！")
    logger.info('这是user接口：username={},当前时间戳为：{tiems}', user_id, tiems=time.time())
    # my_function(0, 0)
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


@app.post("/items/{user_id}", response_model=List[schemas.Item])
def read_items_by_space(user_id: int, space: schemas.Space, skip: int = 0, limit: int = 100,
                        db: Session = Depends(get_db)):
    items = crud.get_items_by_space(db, owner_id=user_id, space=space, skip=skip, limit=limit)
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


# @app.post("/users/{user_id}/spaces/", response_model=schemas.Space)
# def create_space_for_user(user_id: int, space: schemas.SpaceCreate, db: Session = Depends(get_db)):
#     db_space = crud.get_space_by_owner_name_and_room(db, owner_id=user_id, space_name=space.name,
#                                                      space_room=space.room)
#     if db_space:
#         raise HTTPException(status_code=400, detail="Space already registered")
#     return crud.create_user_space(db=db, space=space, user_id=user_id)


@app.post("/users/{user_id}/rooms/", response_model=schemas.Room)
def create_room_for_user(user_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_name(db, owner_id=user_id, name=room.name)

    if db_room:
        raise HTTPException(status_code=400, detail="Room already registered")
    return crud.create_user_room(db=db, room=room, user_id=user_id)


@app.post("/users/{user_id}/storage_spaces/", response_model=schemas.StorageSpace)
def create_storage_space_for_user(user_id: int, storage_space: schemas.StorageSpaceCreate,
                                  db: Session = Depends(get_db)):
    db_storage_space = crud.get_storage_space_by_name_and_room(db, owner_id=user_id, base_storage_space=storage_space)

    if db_storage_space:
        raise HTTPException(status_code=400, detail="StorageSpace already registered")
    return crud.create_user_storage_space(db=db, storage_space=storage_space, user_id=user_id)


# @app.get("/spaces/{user_id}", response_model=List[schemas.Space])
# def read_spaces(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     spaces = crud.get_spaces(db, owner_id=user_id, skip=skip, limit=limit)
#     return spaces


@app.get("/rooms/{user_id}", response_model=List[schemas.Room])
def read_rooms(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, owner_id=user_id, skip=skip, limit=limit)
    return rooms


@app.get("/storage_spaces/{user_id}", response_model=List[schemas.StorageSpace])
def read_user_all_storage_spaces(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_user_all_storage_spaces(db, owner_id=user_id, skip=skip, limit=limit)
    return rooms


@app.post("/storage_spaces/{user_id}", response_model=List[schemas.StorageSpace])
def read_storage_spaces(user_id: int, find: schemas.StorageSpaceBase, skip: int = 0, limit: int = 100,
                        db: Session = Depends(get_db)):
    rooms = crud.get_storage_spaces(db, owner_id=user_id, room_id=find.room_id, skip=skip, limit=limit)
    return rooms


# @app.put("/items/{user_id}/{item_id}/", response_model=schemas.User)
# def relate_user_item(user_id: int, item_id: int, db: Session = Depends(get_db)):
#     user = crud.relate_user_item(db=db, item_id=item_id, user_id=user_id)
#     return user


# @app.put("/spaces/{space_id}", response_model=schemas.Space)
# def update_space(space_id: int, update_space: schemas.SpaceUpdate, db: Session = Depends(get_db)):
#     db_space = crud.get_space(db, space_id)
#     if db_space is None:
#         raise HTTPException(status_code=404, detail="Space not found")
#     same_space = crud.get_space_by_owner_name_and_room(db, owner_id=db_space.owner_id, space_name=update_space.name,
#                                                        space_room=update_space.room)
#     if same_space:
#         raise HTTPException(status_code=400, detail="Space already registered")
#     updated_space = crud.update_space(db, space_id, update_space)
#     return updated_space


@app.put("/rooms/{room_id}", response_model=schemas.Room)
def update_room(room_id: int, update_room: schemas.RoomUpdate, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_id(db, room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    same_room = crud.get_room_by_name(db, owner_id=db_room.owner_id, name=update_room.name)
    if same_room:
        raise HTTPException(status_code=400, detail="Room already registered")
    updated_room = crud.update_room(db, room_id, update_room)
    return updated_room


@app.put("/storage_spaces/{storage_space_id}", response_model=schemas.StorageSpace)
def update_storage_space(storage_space_id: int, update_storage_space: schemas.StorageSpaceUpdate,
                         db: Session = Depends(get_db)):
    db_storage_space = crud.get_storage_space_by_id(db, storage_space_id)
    if db_storage_space is None:
        raise HTTPException(status_code=404, detail="Storage Space not found")
    same_storage_space = crud.get_storage_space_by_name_and_room(db, owner_id=db_storage_space.owner_id,
                                                                 base_storage_space=update_storage_space)
    if same_storage_space:
        raise HTTPException(status_code=400, detail="Storage Space already registered")
    updated_storage_space = crud.update_storage_space(db, storage_space_id, update_storage_space)
    return updated_storage_space


# @app.delete('/spaces/{space_id}', response_model=schemas.Space)
# def delete_space(space_id: int, db: Session = Depends(get_db)):
#     db_space = crud.delete_space(db, space_id=space_id)
#     if db_space is None:
#         raise HTTPException(status_code=404, detail="Space not found")
#     return db_space


@app.delete('/rooms/{room_id}', response_model=schemas.Room)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = crud.delete_room(db, room_id=room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room


@app.delete('/storage_spaces/{storage_space_id}', response_model=schemas.StorageSpace)
def delete_storage_space(storage_space_id: int, db: Session = Depends(get_db)):
    db_storage_space = crud.delete_storage_space(db, storage_space_id=storage_space_id)
    if db_storage_space is None:
        raise HTTPException(status_code=404, detail="Storage Space not found")
    return db_storage_space


# TODO: 可以为不存在的用户、item和空间创建
@app.post("/users/{user_id}/ivt/", response_model=schemas.Inventory)
def relate_inventory_for_user(user_id: int, ivt_item: schemas.InventoryRelate, db: Session = Depends(get_db)):
    # db_space = crud.get_space_by_owner_name_and_room(db, owner_id=user_id, space_name=space.name,
    #                                                  space_room=space.room)
    # if db_space:
    #     raise HTTPException(status_code=400, detail="Space already registered")
    db_storage_space = crud.find_storage_space_in_room(db=db, ivt_item=ivt_item, owner_id=user_id)
    if db_storage_space is None:
        raise HTTPException(status_code=404, detail="Storage Space not found in Room")
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


@app.post('/ivt/{user_id}', response_model=schemas.Inventory)
def read_inventory_by_item(user_id: int, item: schemas.ItemQuery, skip: int = 0, limit: int = 100,
                           db: Session = Depends(get_db)):
    db_ivt_item = crud.get_inventory_by_item(db, owner_id=user_id, item_id=item.item_id)
    if db_ivt_item is None:
        raise HTTPException(status_code=404, detail="Item position not found")
    return db_ivt_item


@app.post('/ivt/space/{user_id}', response_model=List[schemas.Inventory])
def read_inventory_by_space(user_id: int, space: schemas.StorageSpaceQuery, skip: int = 0, limit: int = 100,
                            db: Session = Depends(get_db)):
    db_ivt = crud.get_inventory_by_space(db, owner_id=user_id, storage_space_id=space.storage_space_id, skip=skip,
                                         limit=limit)
    if db_ivt is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return db_ivt


@app.get('/ivts/', response_model=List[schemas.Inventory])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_ivt_item = crud.get_inventory(db, skip=skip, limit=limit)
    if db_ivt_item is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return db_ivt_item

from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Session

#engine = create_engine("postgresql://postgres:12345@217.71.129.139:4385/postgres")
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
class Base(DeclarativeBase): pass
 
class Item(Base):
    __tablename__ = "items"
    record_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Text)
    item_name = Column(Text)
    item_type = Column(Text)
    cell_id = Column(Text)
    log = Column(Text)

class Cell(Base):
    __tablename__ = "stock"
    record_id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Text)
    items_type = Column(Text)
    occupied_space = Column(Integer)
    log = Column(Text)

class Params(Base):
    __tablename__ = "stock_params"
    record_id = Column(Integer, primary_key=True, index=True)
    rows = Column(Integer)
    levels = Column(Integer)
    cells = Column(Integer)
    space = Column(Integer)

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)

    with Session(autoflush=False, bind=engine) as db:
        #tom = Params(rows=1, levels=3, cells=5, space=50)
        #db.add(tom)     
        db.commit() 

        #items = db.query(Params).all()
        #for i in items:
            #print(f"{i.rows} {i.levels} {i.cells}")


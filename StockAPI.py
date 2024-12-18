from Optimizator import Optimizator
from Cell import QCell
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Item, Params, Cell
from datetime import datetime
import random

class Stock():

    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port: str = 5432):
        self.__engine = self.__set_connection(dbname, user, password, host, port)
        self.__db_params = self.__init_stock()
        self.__optimizator = self.__init_optimizator()


    def find_add_cell(self, item_id: str, item_name: str, item_type: str) -> str:
        """Метод поиска доступной для добавления ячейки"""

        with Session(autoflush=False, bind=self.__engine) as db:
            #ищем ячейку типа товара 
            cell = db.query(Cell).filter(Cell.items_type==item_type, Cell.occupied_space < self.__db_params['space']).first()
            
            if cell == None: #если не нашли, то ищем пустую
                cell = db.query(Cell).filter(Cell.occupied_space==0).first()

                if cell == None: #если даже пустую не нашли то возвращаем пустое значение
                    return None
                else: #если нашли пустую ячеку
                    return cell.cell_id
            else:
                return cell.cell_id

    def add(self, cell_id:str,  item_id: str, item_name: str, item_type: str, user: str) -> bool:
        """Метод добавляющий товар в ячейку с идентификатиором cell_id и возвращающий true/false в случае успеха/провала"""

        with Session(autoflush=False, bind=self.__engine) as db:

            #ищем ячейку типа товара 
            cell = db.query(Cell).filter(Cell.cell_id==cell_id, Cell.occupied_space < self.__db_params['space']).first()
            
            if cell == None: #если не нашли
                return False

            if cell.items_type == 'None':
                cell.items_type = item_type
            
            #добавляем запись о новом товаре
            time = datetime.now()
            db.add(Item(item_id=item_id, item_name=item_name, item_type=item_type, cell_id=cell.cell_id, log='Добавлен в ячейку ' + cell.cell_id + ' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + ';'))
            cell.occupied_space += 1
            cell.log += ' Добавление ' + item_id + ' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + '; '

            if cell.occupied_space < self.__db_params['space']:
                self.__optimizator.add(QCell(cell.cell_id, cell.occupied_space, cell.items_type))
            else:
                self.__optimizator.erase(QCell(cell.cell_id, cell.occupied_space, cell.items_type))

            db.commit()
            return True


    def find_get_cell(self, item_id:str) -> str: 
        """Метод поиска ячейки с товаром обладающим индетификатором item_id"""
        with Session(autoflush=False, bind=self.__engine) as db:

            item = db.query(Item).filter(Item.item_id==item_id).first()#ищем товар по id

            if item == None:
                return None

            return item.cell_id

         
    def get(self, cell_id: str, item_id: str, user: str) -> bool:
        """Метод для извлечения товара из ячейки cell_id по его id и возвращает true/false в случае успеха/провала"""

        with Session(autoflush=False, bind=self.__engine) as db:
            item = db.query(Item).filter(Item.item_id==item_id).first()#ищем товар по id

            if item != None:#если нашли
                cell = db.query(Cell).filter(Cell.cell_id==item.cell_id).first()#ищем где лежит

                if cell_id == cell.cell_id:
                    #обновляем дейту
                    cell.occupied_space -= 1
                    time = datetime.now()
                    cell.log += 'Извлечение ' + item_id + ' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + '; '

                    if cell.occupied_space > 0:
                        self.__optimizator.add(QCell(cell.cell_id, cell.occupied_space, cell.items_type))
                    else:
                        self.__optimizator.erase(QCell(cell.cell_id, cell.occupied_space, cell.items_type))
                        cell.items_type = 'None'

                    db.delete(item)#удаляем запись об этом товаре
                    db.commit()
                    return True

                else:
                    return False

            else:
                return False


    def get_movements(self, type: str = None):
        """
        Метод возбращающий список перемещений в виде словаря/списка (при наличии параметра type)
        Вывод в формате: {type1: [[cell_out1, cell_in1] ... ], type2: [...], ...}
        """
        all_clusters = self.__optimizator.divide_into_clusters()
        result = {}

        for i in all_clusters.keys():
            clusters = all_clusters[i]
            movements = []

            for cluster in clusters:
                if len(cluster) > 1:
                    cell_in = cluster[0]

                    for j in range(1, len(cluster)):
                        movements.append([cluster[j].get_id(), cell_in.get_id()])

            result[i] = movements

        if type != None:
            return result[type]

        return result


    def move(self, cell_in: str, item_id: str, user: str) -> bool:
        """
        Метод выполняющий пермещение товара item_id в ячейку cell_id
        """
        with Session(autoflush=False, bind=self.__engine) as db:

            item = db.query(Item).filter(Item.item_id==item_id).first()#ищем товар по id

            if item != None:
                cell = db.query(Cell).filter(Cell.cell_id==item.cell_id).first()
                new_cell = db.query(Cell).filter(Cell.cell_id==cell_in, Cell.occupied_space < self.__db_params['space']).first()

                if cell != None and new_cell != None:

                    time = datetime.now()
                    cell.occupied_space -= 1
                    cell.log += 'Извлечение ' + item_id + ' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + '; '

                    item.cell_id = cell_in
                    item.log += 'Перемещен из ' + cell.cell_id + ' в ' + new_cell.cell_id +' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + '; '
                
                    new_cell.occupied_space += 1
                    new_cell.log += 'Добавление ' + item_id + ' в ' + str(time.day) + '-' + str(time.month) + '-' + str(time.year) + ' ' + str(time.hour) + ':' + str(time.minute) + ' пользователем ' + user + '; '

                    if cell.occupied_space > 0:
                        self.__optimizator.add(QCell(cell.cell_id, cell.items_type, cell.occupied_space))
                    else:
                        self.__optimizator.erase(QCell(cell.cell_id, cell.items_type, cell.occupied_space))

                    if new_cell.occupied_space < self.__db_params['space']:
                        self.__optimizator.add(QCell(new_cell.cell_id, new_cell.items_type, new_cell.occupied_space))
                    else:
                        self.__optimizator.erase(QCell(new_cell.cell_id, new_cell.items_type, new_cell.occupied_space))

                    db.commit()
                    return True
                else:
                    return False
            else:
                return False


    def get_items_data(self, item_id: str=None, item_name: str=None, item_type: str=None, cell_id: str=None):
        """Метод для вывода данных о товаре(товарах) по фильтрам id, name, type, cell"""
        items = []
        with Session(autoflush=False, bind=self.__engine) as db:

            if item_id != None:
                items_by_filters = db.query(Item).filter(Item.cell_id==cell_id).all()

            elif item_name != None:
                if item_type == None and cell_id == None:
                    items_by_filters = db.query(Item).filter(Item.item_name==item_name).all()

                elif item_type != None:
                    items_by_filters = db.query(Item).filter(Item.item_name==item_name, Item.item_type==item_type).all()

                elif cell_id != None:
                    items_by_filters = db.query(Item).filter(Item.item_name==item_name, Item.cell_id==cell_id).all()

                else:
                    items_by_filters = db.query(Item).filter(Item.item_name==item_name, Item.cell_id==cell_id, Item.item_type==item_type).all()

            elif item_type != None:
                if cell_id == None:
                    items_by_filters = db.query(Item).filter(Item.item_type==item_type).all()

                else:
                    items_by_filters = db.query(Item).filter(Item.item_type==item_type, Item.cell_id==cell_id).all()

            elif cell_id != None:
                items_by_filters = db.query(Item).filter(Item.cell_id==cell_id).all()

            for i in items_by_filters:
                items.append((i.item_id, i.item_name, i.item_type, i.cell_id, i.log))

        return items


    def get_info(self, iid: str)->str:
        """Метод для получения справки по товару/ячейке с идентификатором iid"""
        with Session(autoflush=False, bind=self.__engine) as db:
            info = db.query(Item).filter(Item.item_id==iid).first()
            if info != None:
                return f'Товар: {info.item_id}, наименование: {info.item_name}, тип товара: {info.item_type}, где лежит {info.cell_id}, история {info.log}'
            else:
                info = db.query(Cell).filter(Cell.cell_id==iid).first()
                if info != None:
                    return f'Ячейка: {info.cell_id}, тип товара: {info.items_type}, занятое пространство {info.occupied_space}, история {info.log}'
                else:
                    return f'Неизвестный идентификатор {iid}'


    def get_items_in_cell(self, cell_id: str):
        """
        Метод возвращающий список товаров в ячейке cell_id
        """
        items = []
        with Session(autoflush=False, bind=self.__engine) as db:

            items_in_cell = db.query(Item).filter(Item.cell_id==cell_id).all()

            if items_in_cell != None:#ищем товары в ячейке cell_id
                for i in items_in_cell:
                    items.append(i.item_id)

        return items


    def get_db_data(self):
        """Метод для вывода данных о ячейках склада"""
        cells = []
        with Session(autoflush=False, bind=self.__engine) as db:

            cells_in_db = db.query(Cell).all()
            for c in cells_in_db:
                cells.append((c.cell_id, c.occupied_space, c.items_type, c.log))

        return cells


    def get_stock_params(self):
        """Метод для вывода параметров склада в виде словаря"""
        return self.__db_params


    def new_item_id(self) -> str:
        """Создание нового уникального id товара для добавления на склад"""
        with Session(autoflush=False, bind=self.__engine) as db:

            while True:

                new_id = str(random.randint(0, 1000))
                while len(new_id) < 4:
                    new_id = '0' + new_id

                if db.query(Item).filter(Item.item_id == new_id).first() == None:
                    return new_id


    def random_item_id(self) -> str:
        """Случайный товар со склада"""
        with Session(autoflush=False, bind=self.__engine) as db:
            items = db.query(Item).filter().all()
            return items[random.randint(0, len(items) - 1)].item_id


    def set_stock_params(self, rows: int, levels: int, cells: int, space: int):
        """Метод задающий новые параметры склада"""
        with Session(autoflush=False, bind=self.__engine) as db:

            items = db.query(Item).filter().all()
            for i in items:
                db.delete(i)

            dcells = db.query(Cell).filter().all()
            for i in dcells:
                db.delete(i)

            for row in range(rows):
                for level in range(levels):
                    for cell in range(cells):
                        db.add(Cell(cell_id=self.__generate_cell_id(row+1, level+1, cell+1),  items_type='None', occupied_space=0, log=''))

            old_params = db.query(Params).filter().first()
            if old_params != None:
                old_params.rows = rows
                old_params.levels = levels
                old_params.cells = cells
                old_params.space = space
            else:
                db.add(Params(rows=rows, levels=levels, cells=cells, space=space))

            db.commit()


    def __init_optimizator(self):
        """Инициализация оптимизатора"""
        optimizator = Optimizator(self.__db_params)
        with Session(autoflush=False, bind=self.__engine) as db:

            cells = db.query(Cell).all()
            for c in cells:
                if c.occupied_space < self.__db_params['space'] and c.occupied_space > 0:
                    optimizator.add(QCell(c.cell_id, c.occupied_space, c.items_type))

        return optimizator


    def __set_connection(self, dbname: str, user: str, password: str, host:str, port:str):
        """Установка соединения с СУБД"""
        return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")


    def __init_stock(self):
        """Инициализация склада"""
        with Session(autoflush=False, bind=self.__engine) as db:

            params = db.query(Params).first()

            if params == None:
                self.set_stock_params(1, 3, 5, 50)
                return {'rows': 1, 'levels': 3, 'cells': 5, 'space': 50}

            return {'rows': params.rows, 'levels': params.levels, 'cells': params.cells, 'space': params.space}


    def __generate_cell_id(self, row:int , level: int, cell: int) -> str:
        """Генерация id ячейки в зависимости от ее положения на складе"""
        result = str(cell)
        while len(result) < 4:
            result = '0' + result

        result = str(level) + result
        while len(result) < 8:
            result = '0' + result

        result = str(row) + result
        while len(result) < 12:
            result = '0' + result

        return result


if __name__ == '__main__':
    stk = Stock(dbname='postgres', user='postgres', password='12345', host='217.71.129.139', port='4385')

    #stk = Stock(dbname='postgres', user='postgres', password='postgres', host='localhost', port='5432')

    #print(stk.set_stock_params(1, 3, 3, 10))
    
    items_types = ['type1', 'type2', 'type3']
    
    '''
    fail_count = 0
    while fail_count < 10:
        iid = stk.new_item_id()
        iname = 'item' + iid
        itype = items_types[random.randint(0, 2)]
        if not stk.add(stk.find_add_cell(iid, iname, itype), iid, iname, itype, 'admin'):
            fail_count += 1
    '''
    print(stk.get_movements())
    
    '''
    fail_count = 0
    db_data = stk.get_db_data()

    while fail_count < 100:
        iid = stk.random_item_id()
        stk.get(stk.find_get_cell(iid), iid, 'admin')
        fail_count += 1
        print(fail_count)
    
    print(stk.get_movements())
    '''
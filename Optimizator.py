from Queue import Queue
from Cell import QCell

class Optimizator():
    def __init__(self, db_params:dict):
        self.__buff = {}
        self.__db_params = db_params

    def add(self, cell: QCell):
        """Добавляем изменения"""
        if cell.get_type() in self.__buff.keys():
            self.__buff[cell.get_type()].push(cell)
        else:
            self.__buff[cell.get_type()] = Queue()
            self.__buff[cell.get_type()].push(cell)

    def erase(self, cell: QCell):
        if cell.get_type() in self.__buff.keys():
             self.__buff[cell.get_type()].pop(cell.get_id())

    def is_cell_in_buff(self, cell_id: str) -> bool:
        for i in self.__buff.keys():
            if self.__buff[i].is_cell_in_buff(cell_id):
                return True
        return False

    def __max_cluster(self, changes: list):
        """Формирование кластера"""
        result = []
        quantity = 0

        for i in changes:

            if len(result) == 0:
                result.append(i)
                quantity += i.get_quantity()
            else:
                if quantity + i.get_quantity() <= self.__db_params['space']:
                    result.append(i)
                    quantity += i.get_quantity()

        return result

    def divide_into_clusters(self):
        """Разделение на множества"""
        result = {}

        for i in self.__buff.keys():
            changes = self.__buff[i].get_elems()
            clusters = []

            while len(changes) > 0:
                cluster = self.__max_cluster(changes)
                clusters.append(cluster)

                for j in cluster:

                    indx = self.__find_indx(changes, j)
                    if indx != None:
                        changes.pop(indx)

            result[i] = clusters
        return result

    def __find_indx(self, changes, claster):
        for i in range(len(changes)):
            if changes[i] == claster:
                return i
        return None
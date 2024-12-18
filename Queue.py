from Cell import QCell

class Queue():
    def __init__(self):
        """Класс очередь с приоритетом по количеству содержимомго в ячейке"""
        self.__queue = []

    def push(self, cell: QCell):
        """Пушим ячейку в буфер"""
        index = 0

        if self.__ind_in_que(cell.get_id()) == None:

            for i in range(len(self.__queue)):
                index = i
                if cell.get_quantity() > self.__queue[i].get_quantity():
                    break;

            if index == len(self.__queue) - 1:

                if self.__queue[index].get_quantity() < cell.get_quantity():
                    self.__queue.insert(index, cell)
                else:
                    self.__queue.insert(index + 1, cell)
            else: 
                self.__queue.insert(index, cell)
        else:
            self.__queue.pop(self.__ind_in_que(cell.get_id()))
            self.push(cell)

    def pop(self, id: str=None):
        """Извлекаем ячейку из буфера"""
        if id == None:
            result = self.__queue[0]
            self.__queue = self.__queue[1:]
            return result
        else:
            result = self.__queue.pop(self.__ind_in_que(id))

    def is_cell_in_buff(self, cell_id: str) -> bool:
        for i in self.__queue:
            if i.get_id == cell_id:
                return True
        return False

    def get_elems(self) -> list:
        """Смотрим буфер"""
        return self.__queue

    def clear(self):
        """Очистка"""
        self.__queue.clear()
        
    def len(self):
        """Вычисление длины"""
        return len(self.__queue)

    def __ind_in_que(self, id):
        """Вычисляем индекс ячейки ао id"""
        for i in range(len(self.__queue)):
            if id == self.__queue[i].get_id():
                return i
        return None
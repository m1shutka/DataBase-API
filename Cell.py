class QCell():
    def __init__(self, cid: str, cquantity: int, ctype: str):
        """Класс ячейка"""
        self.__id = cid 
        self.__type = ctype
        self.__quantity = cquantity
        
    def get_id(self):
        return self.__id

    def get_quantity(self):
        return self.__quantity

    def get_type(self):
        return self.__type

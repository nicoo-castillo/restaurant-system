from models.ElementoMenu import CrearMenu 
class Pedido:
    def __init__(self):
        self.menus = []  

    def agregar_menu(self, menu: CrearMenu):    
        for m in self.menus:
            if m.nombre == menu.nombre:
                m.cantidad += 1
                return
        import copy
        nuevo_menu = copy.deepcopy(menu)
        nuevo_menu.cantidad = 1
        self.menus.append(nuevo_menu)

    def eliminar_menu(self, nombre_menu: str):
        self.menus = [m for m in self.menus if m.nombre != nombre_menu]

    def mostrar_pedido(self):
        pass

    def calcular_total(self) -> float:
        total = 0
        for menu in self.menus:
            total += menu.precio * menu.cantidad
        return total

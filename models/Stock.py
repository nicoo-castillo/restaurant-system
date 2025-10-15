from models.Ingrediente import Ingrediente

class Stock:
    def __init__(self):
        self.lista_ingredientes = []

    def agregar_ingrediente(self, ingrediente):
        for ing in self.lista_ingredientes:
            if ing.nombre == ingrediente.nombre and ing.unidad == ingrediente.unidad:
                ing.cantidad = int(ing.cantidad) + int(ingrediente.cantidad)
                return
        self.lista_ingredientes.append(ingrediente)

    def eliminar_ingrediente(self, nombre_ingrediente):
        self.lista_ingredientes = [ing for ing in self.lista_ingredientes 
                                    if ing.nombre != nombre_ingrediente]    

    def verificar_stock(self):
        pass

    def actualizar_stock(self, nombre_ingrediente, nueva_cantidad):
        pass

    def obtener_elementos_menu(self):
        pass


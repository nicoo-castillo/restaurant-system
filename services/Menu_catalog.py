from typing import List
from models.ElementoMenu import CrearMenu
from models.Ingrediente import Ingrediente
from models.IMenu import IMenu

def get_default_menus() -> List[IMenu]:
    return [
        CrearMenu(
            "Completo",
            [
                Ingrediente("Vienesa","unid", 1),
                Ingrediente("Pan de completo","unid", 1),
                Ingrediente("Palta","kg",0.5),
                Ingrediente("Tomate","kg",0.2),
            ],
            precio=1800,
            icono_path="assets/IMG/icono_hotdog_sin_texto_64x64.png",
        ),
        CrearMenu(
            "Hamburguesa",
            [
                Ingrediente("Pan de hamburguesa","unid",1),
                Ingrediente("Lamina de queso","unid",1),
                Ingrediente("Churrasco de carne","unid",1),
                Ingrediente("Tomate","kg",0.2),
                Ingrediente("Lechuga","unid",1),
            ],
            precio=4500,
            icono_path="assets/IMG/icono_hamburguesa_negra_64x64.png",
        ),
        CrearMenu(
            "Chorrillana",
            [
                Ingrediente("Papas","kg",2.5),
                Ingrediente("Carne de vacuno","kg",1.2),
                Ingrediente("Huevos","unid",4),
                Ingrediente("Cebolla","unid",2),
                Ingrediente("Vienesa","unid",4),
                Ingrediente("Lamina de queso","unid",5),
                Ingrediente("Pollo","kg",1.2),
            ],
            precio=12000,
            icono_path="assets/IMG/icono_chorrillana_64x64.png",
        ),
        CrearMenu(
            "Empana de queso",
            [
                Ingrediente("Masa de empanada","unid",1),
                Ingrediente("Queso de empanada","kg",0.5),
            ],
            precio=2000,
            icono_path="assets/IMG/icono_empanada_queso_64x64.png",
        ),
        CrearMenu(
            "Papas Fritas",
            [
                Ingrediente("Papas","kg",0.5),
            ],
            precio=2000,
            icono_path="assets/IMG/icono_papas_fritas_64x64.png",
        ),
        CrearMenu(
            "Coca-Cola",
            [
                Ingrediente("Coca-Cola","unid",1),
            ],
            precio=1000,
            icono_path="assets/IMG/icono_cola_lata_64x64.png"
        ),
        CrearMenu(
            "Pepsi",
            [
                Ingrediente("Pepsi","unid",1)
            ],
            precio=1000,
            icono_path="assets/IMG/icono_cola_64x64.png"
        )
    ]
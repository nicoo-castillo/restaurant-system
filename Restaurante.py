from models.ElementoMenu import CrearMenu
from models.Ingrediente import Ingrediente
from models.Stock import Stock
from models.Pedido import Pedido
from services.Menu_catalog import get_default_menus
from services.menu_pdf import create_menu_pdf
from services.BoletaFacade import BoletaFacade
from utils.ctk_pdf_viewer import CTkPDFViewer
from tkinter import ttk, Toplevel, Label, messagebox
from tkinter import filedialog as fd
from tkinter.font import nametofont
from PIL import Image
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import pandas as pd
import os
import re



class AplicacionConPestanas(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Gestión de ingredientes y pedidos")
        self.geometry("1100x900")
        nametofont("TkHeadingFont").configure(size=14)
        nametofont("TkDefaultFont").configure(size=11)

        self.stock = Stock()
        self.menus_creados = set()

        self.pedido = Pedido()

        self.menus = get_default_menus()  

        self.tabview = ctk.CTkTabview(self,command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.crear_pestanas()

    def actualizar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ingrediente in self.stock.lista_ingredientes:
            cantidad = ingrediente.cantidad
            if cantidad == int(cantidad): 
                cantidad_str = str(int(cantidad))
            else: 
                cantidad_str = str(cantidad)
        
            self.tree.insert("", "end", values=(ingrediente.nombre, ingrediente.unidad, cantidad_str))

    def on_tab_change(self):
        selected_tab = self.tabview.get()
        if selected_tab == "carga de ingredientes":
            print('carga de ingredientes')
        if selected_tab == "Stock":
            self.actualizar_treeview()
            print('Stock')
        if selected_tab == "Pedido":
            self.actualizar_treeview()
            print('pedido')
        if selected_tab == "Carta restorante":
            self.actualizar_treeview()
            print('Carta restorante')
        if selected_tab == "Boleta":
            self.actualizar_treeview()
            print('Boleta')       

    def crear_pestanas(self):
        self.tab3 = self.tabview.add("Carga de ingredientes")  
        self.tab1 = self.tabview.add("Stock")
        self.tab4 = self.tabview.add("Carta restorante")  
        self.tab2 = self.tabview.add("Pedido")
        self.tab5 = self.tabview.add("Boleta")
        
        self.configurar_pestana1()
        self.configurar_pestana2()
        self.configurar_pestana3()
        self._configurar_pestana_crear_menu()
        self._configurar_pestana_ver_boleta()

    def configurar_pestana3(self):
        label = ctk.CTkLabel(self.tab3, text="Carga de archivo CSV")
        label.pack(pady=20)
        boton_cargar_csv = ctk.CTkButton(self.tab3, text="Cargar CSV", fg_color="#1976D2", text_color="white",command=self.cargar_csv)

        boton_cargar_csv.pack(pady=10)

        self.frame_tabla_csv = ctk.CTkFrame(self.tab3)
        self.frame_tabla_csv.pack(fill="both", expand=True, padx=10, pady=10)
        self.df_csv = None   
        self.tabla_csv = None

        self.boton_agregar_stock = ctk.CTkButton(self.frame_tabla_csv, text="Agregar al Stock", command=self.agregar_csv_al_stock)
        self.boton_agregar_stock.pack(side="bottom", pady=10)

    def agregar_csv_al_stock(self):
        if self.df_csv is None:
            messagebox.showwarning(title="Error", message="Primero debes cargar un archivo CSV.")
            return

        if 'nombre' not in self.df_csv.columns or 'cantidad' not in self.df_csv.columns:
            messagebox.showwarning(title="Error", message="El CSV debe tener columnas 'nombre' y 'cantidad'.")
            return
        for _, row in self.df_csv.iterrows():
            nombre = str(row['nombre'])
            cantidad = str(row['cantidad'])
            unidad = str(row['unidad'])
            ingrediente = Ingrediente(nombre=nombre,unidad=unidad,cantidad=cantidad)
            self.stock.agregar_ingrediente(ingrediente)
        messagebox.showinfo(title="Stock Actualizado", message="Ingredientes agregados al stock correctamente.")
        self.actualizar_treeview()   

    def cargar_csv(self):
        archivo = fd.askopenfilename(filetypes=[("CSV Files", "*.csv" )],initialdir="data/")
        
        if not archivo:
            return
        
        try:
            self.df_csv = pd.read_csv(archivo)
            self.mostrar_dataframe_en_tabla(self.df_csv)
            self.boton_agregar_stock.configure(command=self.agregar_csv_al_stock)
            messagebox.showinfo(title="Éxito", message="CSV Cargado con éxito.")

        except Exception as e:
            messagebox(title="Error", message=f"No se pudo cargar el CSV:\n{e}", icon="cancel")

    def mostrar_dataframe_en_tabla(self, df):
        if self.tabla_csv:
            self.tabla_csv.destroy()

        self.tabla_csv = ttk.Treeview(self.frame_tabla_csv, columns=list(df.columns), show="headings")
        for col in df.columns:
            self.tabla_csv.heading(col, text=col)
            self.tabla_csv.column(col, width=100, anchor="center")

        for _, row in df.iterrows():
            self.tabla_csv.insert("", "end", values=list(row))

        self.tabla_csv.pack(expand=True, fill="both", padx=10, pady=10)

    def actualizar_treeview_pedido(self):
        for item in self.treeview_menu.get_children():
            self.treeview_menu.delete(item)

        for menu in self.pedido.menus:
            self.treeview_menu.insert("", "end", values=(menu.nombre, menu.cantidad, f"${menu.precio:.2f}"))

    def _configurar_pestana_crear_menu(self):
        contenedor = ctk.CTkFrame(self.tab4)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        boton_menu = ctk.CTkButton(
            contenedor,
            text="Generar Carta (PDF)",
            command=self.generar_y_mostrar_carta_pdf
        )
        boton_menu.pack(pady=10)

        self.pdf_frame_carta = ctk.CTkFrame(contenedor)
        self.pdf_frame_carta.pack(expand=True, fill="both", padx=10, pady=10)

        self.pdf_viewer_carta = None

    def generar_y_mostrar_carta_pdf(self):
        try:
            pdf_path = "doc/carta.pdf"
            create_menu_pdf(self.menus, pdf_path,
                titulo_negocio="Restaurante",
                subtitulo="Carta Primavera 2025",
                moneda="$")
            
            if self.pdf_viewer_carta is not None:
                try:
                    self.pdf_viewer_carta.pack_forget()
                    self.pdf_viewer_carta.destroy()
                except Exception:
                    pass
                self.pdf_viewer_carta = None

            abs_pdf = os.path.abspath(pdf_path)
            self.pdf_viewer_carta = CTkPDFViewer(self.pdf_frame_carta, file=abs_pdf)
            self.pdf_viewer_carta.pack(expand=True, fill="both")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"No se pudo generar/mostrar la carta.\n{e}", icon="warning")

    def _configurar_pestana_ver_boleta(self):
        contenedor = ctk.CTkFrame(self.tab5)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)
    
        boton_boleta = ctk.CTkButton(
            contenedor,
            text="Mostrar Boleta (PDF)",
            command=self.mostrar_boleta
        )
        boton_boleta.pack(pady=10)
    
        self.pdf_frame_boleta = ctk.CTkFrame(contenedor)
        self.pdf_frame_boleta.pack(expand=True, fill="both", padx=10, pady=10)
    
        self.pdf_viewer_boleta = None

    def mostrar_boleta(self):
        pdf_path = "doc/boleta.pdf"
        if not os.path.exists(pdf_path):
            messagebox.showerror(
                title="Error", 
                message="No se encontró ninguna boleta generada.\n\nPrimero genera una boleta desde la pestaña 'Pedido'."
            )
            return
    
        try:
            if self.pdf_viewer_boleta is not None:
                try:
                    self.pdf_viewer_boleta.pack_forget()
                    self.pdf_viewer_boleta.destroy()
                except Exception:
                    pass
                self.pdf_viewer_boleta = None
        
            abs_pdf = os.path.abspath(pdf_path)
            self.pdf_viewer_boleta = CTkPDFViewer(self.pdf_frame_boleta, file=abs_pdf)
            self.pdf_viewer_boleta.pack(expand=True, fill="both")
        
        except Exception as e:
            messagebox.showerror(
                title="Error", 
                message=f"No se pudo mostrar la boleta:\n{e}"
            )

    def configurar_pestana1(self):
        frame_principal = ctk.CTkFrame(self.tab1)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
    
        frame_formulario = ctk.CTkFrame(frame_principal)
        frame_formulario.pack(side="left", fill="both", expand=False, padx=(0, 10))
    
        frame_derecha = ctk.CTkFrame(frame_principal)
        frame_derecha.pack(side="right", fill="both", expand=True)

        label_titulo = ctk.CTkLabel(frame_formulario, text="Agregar Ingrediente", 
                                    font=("Helvetica", 14, "bold"))
        label_titulo.pack(pady=10)
    
        label_nombre = ctk.CTkLabel(frame_formulario, text="Nombre del Ingrediente:")
        label_nombre.pack(pady=(10, 5))
        self.entry_nombre = ctk.CTkEntry(frame_formulario, width=200)
        self.entry_nombre.pack(pady=5)
    
        label_unidad = ctk.CTkLabel(frame_formulario, text="Unidad:")
        label_unidad.pack(pady=(10, 5))
        self.combo_unidad = ctk.CTkComboBox(frame_formulario, values=[ "unid"], width=200)
        self.combo_unidad.pack(pady=5)
    
        label_cantidad = ctk.CTkLabel(frame_formulario, text="Cantidad:")
        label_cantidad.pack(pady=(10, 5))
        self.entry_cantidad = ctk.CTkEntry(frame_formulario, width=200)
        self.entry_cantidad.pack(pady=5)
    
        self.boton_ingresar = ctk.CTkButton(frame_formulario, text="Ingresar Ingrediente",
                                        command=self.ingresar_ingrediente)
        self.boton_ingresar.pack(pady=20)
    
        frame_botones = ctk.CTkFrame(frame_derecha)
        frame_botones.pack(fill="x", padx=10, pady=(10, 5))
    
        self.boton_generar_menu = ctk.CTkButton(frame_botones, text="Generar Menú", 
                                            command=self.generar_menus)
        self.boton_generar_menu.pack(side="left", padx=5)
    
        self.boton_eliminar = ctk.CTkButton(frame_botones, text="Eliminar Ingrediente", 
                                        fg_color="red", hover_color="darkred",
                                        command=self.eliminar_ingrediente)
        self.boton_eliminar.pack(side="left", padx=5)
    
        frame_tree = ctk.CTkFrame(frame_derecha)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
        self.tree = ttk.Treeview(frame_tree, columns=("Nombre", "Unidad", "Cantidad"), 
                            show="headings", height=20)
    
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Unidad", text="Unidad")
        self.tree.heading("Cantidad", text="Cantidad")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
    
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def tarjeta_click(self, event, menu):
        suficiente_stock = True
        if self.stock.lista_ingredientes==[]:
            suficiente_stock=False
        for ingrediente_necesario in menu.ingredientes:
            for ingrediente_stock in self.stock.lista_ingredientes:
                if ingrediente_necesario.nombre == ingrediente_stock.nombre:
                    if int(ingrediente_stock.cantidad) < int(ingrediente_necesario.cantidad):
                        suficiente_stock = False
                        break
            if not suficiente_stock:
                break
        
        if suficiente_stock:
            for ingrediente_necesario in menu.ingredientes:
                for ingrediente_stock in self.stock.lista_ingredientes:
                    if ingrediente_necesario.nombre == ingrediente_stock.nombre:
                        ingrediente_stock.cantidad = str(int(ingrediente_stock.cantidad) - int(ingrediente_necesario.cantidad))
            
            self.pedido.agregar_menu(menu)
            self.actualizar_treeview_pedido()
            total = self.pedido.calcular_total()
            self.label_total.configure(text=f"Total: ${total:.2f}")
        else:
            CTkMessagebox(title="Stock Insuficiente", message=f"No hay suficientes ingredientes para preparar el menú '{menu.nombre}'.", icon="warning")
    
    def cargar_icono_menu(self, ruta_icono):
        imagen = Image.open(ruta_icono)
        icono_menu = ctk.CTkImage(imagen, size=(64, 64))
        return icono_menu

    def generar_menus(self):
        for widget in tarjetas_frame.winfo_children():
            widget.destroy()
        self.menus_creados.clear()

        if not self.stock.lista_ingredientes:
            messagebox.showwarning(
                title="Sin stock", 
                message="Primero debes cargar ingredientes al stock."
            )
            return

        menus_disponibles = 0
        for menu in self.menus:
            if menu.esta_disponible(self.stock):
                self.crear_tarjeta(menu)
                self.menus_creados.add(menu.nombre)
                menus_disponibles += 1

        if menus_disponibles == 0:
            messagebox.showwarning(
                title="Sin menús disponibles", 
                message="No hay ingredientes suficientes para crear ningún menú.\n\nRevisa el stock."
            )
        else:
            messagebox.showinfo(
                title="Menús generados", 
                message=f"Se generaron {menus_disponibles} menú(s) disponible(s)."
            )

    def eliminar_menu(self):
        seleccion = self.treeview_menu.selection()
        if not seleccion:
            messagebox.showwarning(
                title="Error", 
                message="Selecciona un menú de la tabla para eliminar."
            )
            return

        item = self.treeview_menu.item(seleccion[0])
        nombre_menu = item['values'][0]  
        
        menu_a_eliminar = None
        for menu in self.pedido.menus:
            if menu.nombre == nombre_menu:
                menu_a_eliminar = menu
                break
    
        if menu_a_eliminar:
            for ingrediente in menu_a_eliminar.ingredientes:
                for ing_stock in self.stock.lista_ingredientes:
                    if ing_stock.nombre == ingrediente.nombre and ing_stock.unidad == ingrediente.unidad:
                        ing_stock.cantidad = float(ing_stock.cantidad) + (float(ingrediente.cantidad) * menu_a_eliminar.cantidad)
                        break
        self.pedido.eliminar_menu(nombre_menu)
    
        self.actualizar_treeview_pedido()
    
        total = self.pedido.calcular_total()
        self.label_total.configure(text=f"Total: ${total:.2f}")
    
        self.actualizar_treeview()
    
        messagebox.showinfo(
            title="Éxito", 
            message=f"Menú '{nombre_menu}' eliminado del pedido."
        )

    def generar_boleta(self):
        if not self.pedido.menus:
            messagebox.showwarning(
                title="Error", 
                message="El pedido está vacío. Agrega menús antes de generar la boleta."
            )
            return
    
        try:
            boleta = BoletaFacade(self.pedido)
            mensaje = boleta.generar_boleta()
        
            messagebox.showinfo(
                title="Boleta generada", 
                message=mensaje
            )
        
            respuesta = messagebox.askyesno(
                title="Limpiar pedido",
                message="¿Deseas limpiar el pedido actual?",
            )
        
            if respuesta:
                self.pedido.menus = []
                self.actualizar_treeview_pedido()
                self.label_total.configure(text="Total: $0.00")
            
            else:
                return
            
        except Exception as e:
            messagebox.showerror(
                title="Error", 
                message=f"No se pudo generar la boleta:\n{e}"
            )

    def configurar_pestana2(self):
        frame_superior = ctk.CTkFrame(self.tab2)
        frame_superior.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        frame_intermedio = ctk.CTkFrame(self.tab2)
        frame_intermedio.pack(side="top", fill="x", padx=10, pady=5)

        global tarjetas_frame
        tarjetas_frame = ctk.CTkFrame(frame_superior)
        tarjetas_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_eliminar_menu = ctk.CTkButton(frame_intermedio, text="Eliminar Menú", command=self.eliminar_menu)
        self.boton_eliminar_menu.pack(side="right", padx=10)

        self.label_total = ctk.CTkLabel(frame_intermedio, text="Total: $0.00", anchor="e", font=("Helvetica", 12, "bold"))
        self.label_total.pack(side="right", padx=10)

        frame_inferior = ctk.CTkFrame(self.tab2)
        frame_inferior.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        self.treeview_menu = ttk.Treeview(frame_inferior, columns=("Nombre", "Cantidad", "Precio Unitario"), show="headings")
        self.treeview_menu.heading("Nombre", text="Nombre del Menú")
        self.treeview_menu.heading("Cantidad", text="Cantidad")
        self.treeview_menu.heading("Precio Unitario", text="Precio Unitario")
        self.treeview_menu.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_generar_boleta=ctk.CTkButton(frame_inferior,text="Generar Boleta",command=self.generar_boleta)
        self.boton_generar_boleta.pack(side="bottom",pady=10)

    def crear_tarjeta(self, menu):
        num_tarjetas = len(self.menus_creados)
        fila = 0
        columna = num_tarjetas

        tarjeta = ctk.CTkFrame(
            tarjetas_frame,
            corner_radius=10,
            border_width=1,
            border_color="#4CAF50",
            width=64,
            height=140,
            fg_color="gray",
        )
        tarjeta.grid(row=fila, column=columna, padx=15, pady=15, sticky="nsew")

        tarjeta.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))
        tarjeta.bind("<Enter>", lambda event: tarjeta.configure(border_color="#FF0000"))
        tarjeta.bind("<Leave>", lambda event: tarjeta.configure(border_color="#4CAF50"))

        if getattr(menu, "icono_path", None):
            try:
                icono = self.cargar_icono_menu(menu.icono_path)
                imagen_label = ctk.CTkLabel(
                    tarjeta, image=icono, width=64, height=64, text="", bg_color="transparent"
                )
                imagen_label.image = icono
                imagen_label.pack(anchor="center", pady=5, padx=10)
                imagen_label.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))
            except Exception as e:
                print(f"No se pudo cargar la imagen '{menu.icono_path}': {e}")

        texto_label = ctk.CTkLabel(
            tarjeta,
            text=f"{menu.nombre}",
            text_color="black",
            font=("Helvetica", 12, "bold"),
            bg_color="transparent",
        )
        texto_label.pack(anchor="center", pady=1)
        texto_label.bind("<Button-1>", lambda event: self.tarjeta_click(event, menu))

    def validar_nombre(self, nombre):
        if re.match(r"^[a-zA-Z\s]+$", nombre):
            return True
        else:
            CTkMessagebox(title="Error de Validación", message="El nombre debe contener solo letras y espacios.", icon="warning")
            return False

    def validar_cantidad(self, cantidad):
        if cantidad.isdigit():
            return True
        else:
            CTkMessagebox(title="Error de Validación", message="La cantidad debe ser un número entero positivo.", icon="warning")
            return False

    def ingresar_ingrediente(self):
        nombre = self.entry_nombre.get().strip()
        unidad = self.combo_unidad.get()
        cantidad = self.entry_cantidad.get().strip()
    
        if not nombre or not cantidad:
            messagebox.showwarning(
                title="Error", 
                message="Todos los campos son obligatorios."
            )
            return
    
        if not self.validar_cantidad(cantidad):
            return
    
        ingrediente = Ingrediente(nombre=nombre, unidad=unidad, cantidad=float(cantidad))
    
        self.stock.agregar_ingrediente(ingrediente)
    
        self.entry_nombre.delete(0, 'end')
        self.entry_cantidad.delete(0, 'end')
    
        self.actualizar_treeview()
        
        messagebox.showinfo(
            title="Éxito", 
            message=f"Ingrediente '{nombre}' agregado correctamente."
        )

    def eliminar_ingrediente(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
            title="Error", 
            message="Selecciona un ingrediente de la tabla para eliminar."
            )
            return

        item = self.tree.item(seleccion[0])
        nombre = item['values'][0] 
    
        respuesta = messagebox.askyesno(
            title="Confirmar eliminación",
            message=f"¿Estás seguro de eliminar '{nombre}'?"
        )
    
        if respuesta:
            self.stock.eliminar_ingrediente(nombre)

            self.actualizar_treeview()
        
            messagebox.Message(
                "Éxito", 
                f"Ingrediente '{nombre}' eliminado correctamente.", 
            )
        else:
            return

if __name__ == "__main__":
    import customtkinter as ctk
    from tkinter import ttk

    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("blue") 
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    app = AplicacionConPestanas()

    try:
        style = ttk.Style(app)   
        style.theme_use("clam")
    except Exception:
        pass

    app.mainloop()

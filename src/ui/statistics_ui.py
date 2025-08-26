import os
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator 
from src.ui_utils.ui_utils import clear_window, create_banner, create_scroll_window, create_dashboard_button
from src.utils.classes import SUBCLASSES, TRANSLATIONS 

category_colors = {
    'plastic': '#49654E',  
    'cans': '#B35D5D',  
    'cardboard': '#A3886B', 
    'detergent': '#444444', 
    'glass': '#6A8E91'   
}

class StatisticsUI:
    """
    Clase para mostrar la ventana de estadísticas.

     Attributes:
        ui (UI): Instancia principal de la aplicación.
        window (tk.Tk): Ventana principal donde se muestra la interfaz.
    """

    def __init__(self, ui):
        """
        Args:
            ui (UI): Instancia principal de la aplicación.
        """
        self.ui = ui
        self.window = ui.window
        self._build()


    def _build(self):
        """
        Construye la interfaz de estadísticas.
        """
        clear_window(self.window)
        self.window.configure(bg="white")
        create_banner(self.window)

        scrollable_frame = create_scroll_window(self.window, enable_mouse_scroll=True)
        container = tk.Frame(scrollable_frame, bg="#F4F7F5", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        if not os.path.exists("resultados.csv"):
            tk.Label(container, text="No hay datos de clasificación aún.", font=("Verdana", 14), bg="#F4F7F5").pack()
            return

        df = pd.read_csv("resultados.csv")

        self.draw_category_chart(container, df)
        self.draw_subcategory_charts(container, df)
        self.draw_category_pie_chart(container, df)

        create_dashboard_button(self.window, self.ui.create_dashboard)


    def draw_category_chart(self, parent, df):
        """
        Dibuja un gráfico de barras con la cantidad de residuos por categoría.

        Args:
            parent (tk.Widget): Contenedor donde se insertará el gráfico.
            df (pandas.DataFrame): DataFrame con columnas 'categoria' y 'subcategoria'.
        """
        conteo_categoria = df["categoria"].value_counts().sort_index()

        labels = [TRANSLATIONS.get(cat, cat) for cat in conteo_categoria.index]
        colors = [category_colors.get(cat, "#7A9E7E") for cat in conteo_categoria.index]

        fig, ax = plt.subplots(figsize=(9, 6))
        fig.subplots_adjust(bottom=0.25)
        ax.bar(labels, conteo_categoria.values, color=colors)
        ax.set_title("Cantidad de residuos clasificados por categoría")
        ax.set_ylabel("Cantidad")
        ax.set_xlabel("Categoría")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xticks(rotation=30, ha="right")

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
        plt.close(fig)
        

    def draw_subcategory_charts(self, parent, df):
        """ 
        Dibuja gráficos de barras por subcategorías.
    
        Args: 
            parent (tk.Widget): Contenedor donde se insertarán los gráficos. 
            df (pandas.DataFrame): DataFrame con columnas 'categoria' y 'subcategoria'. 
        """
        subcat_frame = tk.Frame(parent, bg="#F4F7F5")
        subcat_frame.pack(pady=10, fill="x")

        title = tk.Label(subcat_frame, text="Distribución por subcategorías",
                font=("Verdana", 12, "bold"), bg="#F4F7F5")
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        plastic_subs = SUBCLASSES.get("plastic", [])
        if plastic_subs:
            sub_df = df[df["categoria"] == "plastic"]
            conteo_real = sub_df["subcategoria"].value_counts().to_dict()
            conteo_completo = {sub: conteo_real.get(sub, 0) for sub in plastic_subs}

            values = list(conteo_completo.values())
            ticklabels = [TRANSLATIONS.get(sub, sub) for sub in conteo_completo.keys()]
            x = list(range(len(values)))  

            width_in = max(6, min(0.55 * len(plastic_subs), 14))
            fig, ax = plt.subplots(figsize=(width_in, 3.0))
            color = category_colors.get("plastic", "#7A9E7E")
            ax.bar(x, values, color=color)
            ax.set_title(f"{TRANSLATIONS.get('plastic', 'plastic')} - Subcategorías")
            ax.set_ylabel("Cantidad")
            ax.set_xlabel("Subcategoría")
            ax.set_xticks(x)
            ax.set_xticklabels(ticklabels, rotation=45, ha="right")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            fig.tight_layout()

            graph_frame = tk.Frame(subcat_frame, bg="#F4F7F5")
            graph_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

            sub_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            sub_canvas.draw()
            sub_canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

        restantes = [c for c in SUBCLASSES.keys() if c not in ("plastic", "cans")]
        for idx, categoria in enumerate(restantes):
            row = 2
            col = idx  

            lista_subs = SUBCLASSES[categoria]
            sub_df = df[df["categoria"] == categoria]
            conteo_real = sub_df["subcategoria"].value_counts().to_dict()
            conteo_completo = {sub: conteo_real.get(sub, 0) for sub in lista_subs}

            values = list(conteo_completo.values())
            ticklabels = [TRANSLATIONS.get(sub, sub) for sub in conteo_completo.keys()]
            x = list(range(len(values)))

            fig, ax = plt.subplots(figsize=(3.6, 3.5))
            color = category_colors.get(categoria, "#7A9E7E")
            ax.bar(x, values, color=color)
            ax.set_title(f"{TRANSLATIONS.get(categoria, categoria)} - Subcategorías")
            ax.set_ylabel("Cantidad")
            ax.set_xlabel("Subcategoría")
            ax.set_xticks(x)
            ax.set_xticklabels(ticklabels, rotation=45, ha="right")
            ax.tick_params(axis="x", labelsize=8)  
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            fig.tight_layout()

            graph_frame = tk.Frame(subcat_frame, bg="#F4F7F5")
            graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            sub_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            sub_canvas.draw()
            sub_canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

        for c in range(3):
            subcat_frame.grid_columnconfigure(c, weight=1)


    def draw_category_pie_chart(self, parent, df):
        """
        Dibuja un gráfico de sectores con el porcentaje de residuos por categoría.

        Args:
            parent (tk.Widget): Contenedor donde se insertará el gráfico.
            df (pandas.DataFrame): DataFrame con la columna 'categoria'.
        """
        pie_frame = tk.Frame(parent, bg="#F4F7F5")
        pie_frame.pack(pady=20)

        title = tk.Label(pie_frame, text="Distribución porcentual por categoría",
                 font=("Verdana", 12, "bold"), bg="#F4F7F5")
        title.pack()

        conteo_categoria = df["categoria"].value_counts().sort_index()
        colors = [category_colors.get(cat, "#999999") for cat in conteo_categoria.index]

        labels = [TRANSLATIONS.get(cat, cat) for cat in conteo_categoria.index]

        fig, ax = plt.subplots(figsize=(5, 5)) 
        wedges, texts, autotexts = ax.pie(
            conteo_categoria.values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            labeldistance=0.9,   
            pctdistance=0.7,    
            textprops={'fontsize':10} 
        )
        ax.set_aspect('equal')

        fig.subplots_adjust(left=0.08, right=0.92, top=0.88, bottom=0.12)

        canvas = FigureCanvasTkAgg(fig, master=pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)  
        plt.close(fig)



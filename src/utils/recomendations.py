class Recomendation:
    RECOMENDATIONS = {
        "bottle-blue": "Clasificar como PET azul. Separar y enviar a compactación.",
        "bottle-blue5l": "PET de gran tamaño. Separar y triturar antes de compactar.",
        "bottle-blue5l-full": "PET grande con aire. Vaciar y compactar.",
        "bottle-dark": "Plástico mixto. Derivar a línea de triturado y lavado.",
        "bottle-green": "PET verde. Separar para procesos de fundición específicos.",
        "bottle-milk": "HDPE. Clasificar y almacenar para reciclaje de envases de leche.",
        "bottle-transp": "PET transparente. Priorizar para reciclaje de alta calidad.",
        "bottle-yogurt": "PP. Triturar con otros envases pequeños.",
        "bottle-oil": "Plástico contaminado. Requiere tratamiento especial antes de reciclar.",

        "glass-dark": "Vidrio oscuro. Separar por color y enviar a molino de vidrio.",
        "glass-green": "Vidrio verde. Clasificar para fundición independiente.",
        "glass-transp": "Vidrio blanco. Priorizar para reciclaje de alta calidad.",

        "juice-cardboard": "Envase multicapa. Derivar a reciclaje especializado para separar las fibras.",
        "milk-cardboard": "Cartón multicapa. Procesar en reciclaje químico/térmico.",

        "canister": "HDPE rígido. Triturar en línea de plásticos duros.",
        "detergent-box": "Clasificar según material: cartón o plástico.",
        "detergent-color": "Plástico coloreado. Separar y triturar.",
        "detergent-transparent": "Plástico claro. Triturar y lavar para reciclaje estándar.",
        "detergent-white": "HDPE opaco. Separar por densidad antes de fundir.",

        "cans": "Metales (aluminio/acero). Separar magnéticamente y enviar a fundición.",
    }

    @classmethod
    def get(cls, clase):
        return cls.RECOMENDATIONS.get(clase, "No hay recomendación para esta clase.")

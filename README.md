# TFG - Sistema de clasificación de residuos para unha planta de reciclaxe
Este proyecto está compuesto por varios módulos independientes que pueden ejecutarse por separado.  
A continuación se explican los pasos para configurar el entorno y ejecutar cada módulo.

---

## Requisitos previos

1. **Python 3.10+** instalado en el sistema.  
2. Crear y activar un entorno virtual:  

   - **En Windows (PowerShell):**
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```

   - **En macOS / Linux (bash o zsh):**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
## Dependencias

Instalar las librerías necesarias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Vídeos de ejemplo
Los vídeos necesarios para probar la interfaz no se incluyen en este repositorio por limitaciones de tamaño.
Puedes descargarlos aquí: [Enlace a Drive](https://drive.google.com/drive/folders/1lqyr85amWihoSfO87a29CQaQQm0nSS9A?usp=drive_link)
Colócalos dentro de la carpeta 'videos/' en la carpeta raíz del proyecto.

---

## Entrenamiento de los modelos

> **Nota:** Ejecutar desde la **raíz del proyecto** (donde está `README.md`/`requirements.txt`).  

### Detección (YOLO)
Entrenar el modelo de detección:
```bash
python -m src.detection.yolo_trainer
```

### Módulo de Clasificación (CNN)
Entrenar y validar una red neuronal convolucional (CNN) para la clasificación de imágenes.  

#### 1. Preparar el dataset
Ejecutar el script de preparación de datos:
```bash
python -m src.classification.load_dataset
```

#### 2. Entrenar el modelo
Entrenar el modelo:
```bash
python -m src.classification.train_cnn
```

#### 3. Validar el modelo
Validar el modelo entrenado especificando el tipo de clasificación:

- **Validación multiclase**
```bash
python -m src.classification.validation --type multiclase
```

- **Validación de una clase concreta**: `plastic` | `cardboard` | `glass` | `detergent`
```bash
python -m src.classification.validation --type clase
```

---

### Interfaz gráfica

La interfaz gráfica se ejecuta desde el `main` del proyecto.  

```bash
python -m src.main
```

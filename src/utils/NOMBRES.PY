import os
import shutil

ruta_origen = r"C:\Users\claud\TFG\TFG\archive\Warp-D\train\images"
ruta_destino = r"C:\Users\claud\TFG\TFG\video\images"
os.makedirs(ruta_destino, exist_ok=True)

# Obtener y ordenar las imágenes
imagenes = sorted([f for f in os.listdir(ruta_origen) if f.endswith(".jpg") and f.startswith("POSAD_")])

# Copiar y renombrar
for i, nombre in enumerate(imagenes):
    nuevo_nombre = f"img{i:04d}.jpg"
    shutil.copyfile(os.path.join(ruta_origen, nombre),
                    os.path.join(ruta_destino, nuevo_nombre))

print(f"✅ Renombradas {len(imagenes)} imágenes en: {ruta_destino}")

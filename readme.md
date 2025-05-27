# 🛠️ Sistema de Inventario y Ventas - FerreteríaApp

Sistema web completo para la gestión de inventario y ventas de una ferretería. Incluye control de stock, reportes, gráficos, exportación a PDF y un panel de administración con roles diferenciados.

---

## 🚀 Funcionalidades Principales

✅ Gestión de productos (crear, editar, eliminar)  
✅ Control de stock mínimo y alertas automáticas  
✅ Registro y edición de compras y ventas  
✅ Reporte de ventas por fecha, por categoría y por usuario  
✅ Exportación de reportes a PDF  
✅ Gráficos interactivos con Chart.js  
✅ Sistema de usuarios con autenticación (admin y vendedor)  
✅ Panel de control moderno basado en AdminLTE  
✅ Totalmente responsive para móviles y escritorio  

---

## 🧰 Tecnologías Utilizadas

- **Python 3.10+**
- **Flask** (Microframework web)
- **Jinja2** (Motor de plantillas)
- **Flask-Login** (Autenticación de usuarios)
- **MySQL** (Base de datos relacional)
- **SQLAlchemy** (ORM)
- **AdminLTE** (Plantilla HTML responsive)
- **Bootstrap 4**
- **Chart.js** (Visualización de gráficos)
- **WeasyPrint** o similar para generación de PDF

  
---

## 🧑‍💻 Instalación y ejecución local
---
1. **Clona el repositorio:**

git clone https://github.com/Juangarciaing/ferreteria-inventario.git
-----
2. Crea y activa un entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
----

3.Instala las dependencias
pip install -r requirements.txt
---

4. base de datos en MySQL
 copiala del repositorio
---
5. Configura la conexión
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contraseña@localhost/ferreteria'
   SECRET_KEY = 'una_clave_secreta'
---
6.Ejecución del proyecto
python run.py
---
📦 Estructura del proyecto

ferreteria-inventario/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── templates/
│   └── static/
│
├── config.py
├── run.py
├── requirements.txt
└── README.md
---
📄 Exportación de reportes a PDF
Para exportar reportes a PDF con WeasyPrint, instala también:
pip install weasyprint
Y en sistemas Linux, instala dependencias:
sudo apt install libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2


📊 Capturas de pantalla

![image](https://github.com/user-attachments/assets/31fe07bc-7ed0-41a3-b1fd-b27a3bfb7dea)

![image](https://github.com/user-attachments/assets/259958b5-083c-4395-9f61-a9f7ad7250f0)

🧑‍💻 Autor

Desarrollado por: Juan Camilo Garcia Pomares

Contacto: Juanchogarpo2010@hotmail.com

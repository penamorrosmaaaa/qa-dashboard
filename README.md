# 📊 QA Dashboard Automático

Este repositorio genera automáticamente un **dashboard HTML interactivo** basado en un archivo Excel llamado `reporte_tarjetas.xlsx`.  
Está diseñado para equipos de QA, desarrollo y PMs que manejan flujos de trabajo semanalmente.

---

## 🚀 ¿Qué hace este proyecto?

1. Toma como entrada un archivo `reporte_tarjetas.xlsx` con múltiples hojas de datos.
2. Usa `dashboard_generator.py` para procesar el Excel y generar visualizaciones.
3. Publica automáticamente un dashboard HTML en GitHub Pages:
   👉 [https://penamorrosmaaaa.github.io/qa-dashboard/](https://penamorrosmaaaa.github.io/qa-dashboard/)

---

## 📁 Estructura del repositorio

qa-dashboard/
│
├── reporte_tarjetas.xlsx # Excel semanal con tarjetas
├── dashboard_generator.py # Script para generar el dashboard
├── index.html # Dashboard generado automáticamente
├── .github/
│ └── workflows/
│ └── generate.yml # Workflow para automatización
├── .gitignore # Ignorar archivos temporales
└── README.md # Este documento

yaml
Copy
Edit

---

## 🧑‍💻 Cómo correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/penamorrosmaaaa/qa-dashboard.git
cd qa-dashboard
2. Instalar dependencias
Necesitas Python 3.9+ con estas librerías:

bash
Copy
Edit
pip install pandas openpyxl plotly
3. Ejecutar el script
bash
Copy
Edit
python dashboard_generator.py
Esto generará un archivo index.html actualizado.

🟢 Automatización con GitHub Actions
Este proyecto incluye un workflow (generate.yml) que:

Se activa cada vez que se sube un nuevo reporte_tarjetas.xlsx

Corre dashboard_generator.py

Sube el nuevo index.html

Publica el dashboard en GitHub Pages automáticamente

📤 ¿Cómo subir un nuevo archivo Excel?
Reemplaza reporte_tarjetas.xlsx en tu máquina local con uno nuevo.

Haz push al repositorio:

bash
Copy
Edit
git add reporte_tarjetas.xlsx
git commit -m "Actualizar datos semanales"
git push origin main
El dashboard se actualizará en menos de 1 minuto.

🧹 Archivos ignorados
Este proyecto ignora automáticamente archivos basura de Excel y macOS:

gitignore
Copy
Edit
~$*.xlsx
.DS_Store
🌐 Dashboard online
Visualiza el resultado final en:

👉 https://penamorrosmaaaa.github.io/qa-dashboard/

✍️ Autor
Manuel Peña Morros
💼 penamorros.com
📧 contacto@penamorros.com

yaml
Copy
Edit

---

### ✅ ¿Qué sigue?

1. Crea este archivo en tu proyecto:

```bash
touch README.md
Pega todo el contenido anterior.

Súbelo con:

bash
Copy
Edit
git add README.md
git commit -m "Agregar README completo del proyecto"
git push origin main
¿Quieres que te lo genere directamente como archivo en tu carpeta?






You said:
dame todo el rea dme en formato de git para simpelemtne copiar y epagr


ChatGPT said:
Claro. Aquí tienes el README.md completo en formato listo para copiar y pegar directamente en tu archivo:

markdown
Copy
Edit
# 📊 QA Dashboard Automático

Este repositorio genera automáticamente un **dashboard HTML interactivo** basado en un archivo Excel llamado `reporte_tarjetas.xlsx`.  
Está diseñado para equipos de QA, desarrollo y PMs que manejan flujos de trabajo semanalmente.

---

## 🚀 ¿Qué hace este proyecto?

1. Toma como entrada un archivo `reporte_tarjetas.xlsx` con múltiples hojas de datos.
2. Usa `dashboard_generator.py` para procesar el Excel y generar visualizaciones.
3. Publica automáticamente un dashboard HTML en GitHub Pages:
   👉 [https://penamorrosmaaaa.github.io/qa-dashboard/](https://penamorrosmaaaa.github.io/qa-dashboard/)

---

## 📁 Estructura del repositorio

qa-dashboard/
│
├── reporte_tarjetas.xlsx # Excel semanal con tarjetas
├── dashboard_generator.py # Script para generar el dashboard
├── index.html # Dashboard generado automáticamente
├── .github/
│ └── workflows/
│ └── generate.yml # Workflow para automatización
├── .gitignore # Ignorar archivos temporales
└── README.md # Este documento

yaml
Copy
Edit

---

## 🧑‍💻 Cómo correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/penamorrosmaaaa/qa-dashboard.git
cd qa-dashboard
2. Instalar dependencias
Necesitas Python 3.9+ con estas librerías:

bash
Copy
Edit
pip install pandas openpyxl plotly
3. Ejecutar el script
bash
Copy
Edit
python dashboard_generator.py
Esto generará un archivo index.html actualizado.

🟢 Automatización con GitHub Actions
Este proyecto incluye un workflow (generate.yml) que:

Se activa cada vez que se sube un nuevo reporte_tarjetas.xlsx

Corre dashboard_generator.py

Sube el nuevo index.html

Publica el dashboard en GitHub Pages automáticamente

📤 ¿Cómo subir un nuevo archivo Excel?
Reemplaza reporte_tarjetas.xlsx en tu máquina local con uno nuevo.

Haz push al repositorio:

bash
Copy
Edit
git add reporte_tarjetas.xlsx
git commit -m "Actualizar datos semanales"
git push origin main
El dashboard se actualizará en menos de 1 minuto.

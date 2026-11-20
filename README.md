# SIMTELE-RISK 🚡
### Sistema de Simulación y Análisis de Riesgos en el Transporte por Cable

Proyecto académico desarrollado para la asignatura de Métodos Numéricos.

---

## 📌 1. Descripción del proyecto

SIMTELE-RISK es una aplicación web educativa que permite modelar, simular y analizar escenarios hipotéticos relacionados con un sistema de transporte por cable, mediante la aplicación de métodos numéricos.

El sistema contempla cuatro módulos de estudio:

1. **Detención de emergencia de cabinas:** análisis de situaciones hipotéticas de detención.
2. **Deterioro mecánico y mantenimiento:** modelado del desgaste de componentes mecánicos.
3. **Oscilaciones por viento:** simulación del comportamiento de las cabinas ante condiciones de viento.
4. **Reconstrucción de señales de sensores:** análisis y reconstrucción de datos mediante técnicas numéricas.

Cada módulo contempla escenarios NORMAL, ESTRÉS y MAL CONDICIONADO, permitiendo comparar resultados y estudiar el comportamiento de los métodos numéricos.

**Nota:** Los datos y escenarios utilizados son sintéticos e hipotéticos. El proyecto tiene fines exclusivamente académicos y no representa fallas verificadas ni está conectado a equipos reales de transporte por cable.

---

## 🛠️ 2. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Lenguaje de programación principal |
| Flask | Framework para el desarrollo web |
| Flask-SQLAlchemy | Gestión y definición de modelos de datos |
| Flask-Migrate | Administración de migraciones de la base de datos |
| SQLAlchemy | Mapeo objeto-relacional (ORM) |
| PostgreSQL | Sistema gestor de base de datos |
| Psycopg 3 | Conector entre Python y PostgreSQL |
| python-dotenv | Lectura de variables de entorno desde `.env` |
| HTML5 | Estructura de las páginas |
| CSS3 | Diseño y estilos |
| JavaScript | Funcionalidades e interactividad |
| Chart.js | Visualización de gráficos |
| Git y GitHub | Control de versiones y trabajo colaborativo |

---

## 📋 3. Requisitos previos

Antes de instalar el proyecto, cada integrante debe contar con:

- Python 3.10 o superior.
- PostgreSQL instalado.
- pgAdmin 4 (recomendado para administrar la base de datos).
- Git.
- Visual Studio Code (recomendado).

También es necesario contar con acceso al repositorio de GitHub.

---

## 🚀 4. Instalación del proyecto

### 4.1. Clonar el repositorio

Abrir una terminal y ejecutar:

```bash
git clone https://github.com/Jazmin-lm/MetodosNumericos1.git
```

Ingresar a la carpeta:

```bash
cd Sistema-Teleferico
```

Abrir el proyecto en Visual Studio Code:

```bash
code .
```

### 4.2. Crear el entorno virtual

El entorno virtual permite instalar las dependencias del proyecto de manera aislada.

```bash
python -m venv venv
```

### 4.3. Activar el entorno virtual

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, activar nuevamente:

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
venv\Scripts\activate.bat
```

Cuando el entorno esté activado, aparecerá `(venv)` al inicio de la terminal.

### 4.4. Instalar las dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` debe incluir, como mínimo, las dependencias utilizadas para la aplicación y la conexión con PostgreSQL:

```text
Flask
Flask-SQLAlchemy
Flask-Migrate
python-dotenv
psycopg[binary]
```

Estas dependencias deben agregarse a las existentes si todavía no están incluidas. No se deben eliminar las demás bibliotecas que utiliza el proyecto.

---

## 🗄️ 5. Configuración de PostgreSQL

Cada integrante debe configurar su propia conexión local a PostgreSQL.

**Importante:** todos utilizarán la misma estructura de base de datos, pero cada integrante tendrá su propia instancia local de PostgreSQL.

### 5.1. Crear la base de datos

Abrir pgAdmin 4 y seguir estos pasos:

1. Conectarse al servidor PostgreSQL.
2. Hacer clic derecho sobre `Databases`.
3. Seleccionar `Create` → `Database`.
4. Escribir el siguiente nombre:

```text
simtele_risk
```

5. Guardar los cambios.

Cada integrante debe crear esta base de datos en su propia computadora.

### 5.2. Configurar el archivo .env

En la carpeta principal del proyecto existe el archivo:

```text
.env.example
```

Este archivo contiene una plantilla con las variables necesarias para conectar Flask con PostgreSQL.

Primero, crear una copia del archivo.

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Después, abrir `.env` y modificar los valores de acuerdo con la configuración local de PostgreSQL.

Ejemplo:

```env
SECRET_KEY=mi-clave-local-de-desarrollo
DATABASE_URL=postgresql+psycopg://postgres:mi_password@localhost:5432/simtele_risk
```

Reemplazar:

- `SECRET_KEY`: clave secreta de la aplicación.
- `postgres`: usuario de PostgreSQL.
- `mi_password`: contraseña del usuario de PostgreSQL.
- `localhost`: dirección del servidor.
- `5432`: puerto de PostgreSQL.
- `simtele_risk`: nombre de la base de datos.

Cada integrante debe utilizar sus propias credenciales.

**Importante:**

- No modificar ni subir credenciales reales al archivo `.env.example`.
- No subir el archivo `.env` a GitHub.
- No compartir contraseñas mediante commits o Pull Requests.
- Si la contraseña contiene caracteres especiales, debe codificarse correctamente para utilizarla dentro de la URL de conexión.

### 5.3. Diferencia entre .env y .env.example

| Archivo | Función | ¿Se sube a GitHub? |
|---|---|---|
| `.env` | Contiene las credenciales reales de cada integrante | No |
| `.env.example` | Contiene la plantilla de configuración | Sí |

El archivo `config.py` utiliza `python-dotenv` para leer las variables del archivo `.env` y configurar la conexión de Flask con PostgreSQL.

---

## 🔄 6. Crear las tablas de la base de datos

SIMTELE-RISK utiliza Flask-Migrate y Alembic para administrar los cambios en la estructura de PostgreSQL.

El proyecto ya cuenta con una carpeta `migrations/`, que contiene el historial de migraciones compartidas.

**No es necesario crear nuevamente las migraciones iniciales.**

Una vez configurada la base de datos y el archivo `.env`, ejecutar:

```bash
flask --app app db upgrade
```

Este comando aplica las migraciones existentes y crea las tablas correspondientes en la base de datos local.

Cada integrante debe ejecutar este comando después de descargar el proyecto por primera vez.

También debe ejecutarlo cuando se incorporen nuevas migraciones al repositorio.

### 6.1. ¿Qué contiene la carpeta migrations?

La estructura es similar a la siguiente:

```text
migrations/
│
├── alembic.ini
├── env.py
├── README
│
└── versions/
    ├── migracion_inicial.py
    └── migraciones_posteriores.py
```

La carpeta `versions/` contiene los archivos que registran los cambios realizados en la estructura de la base de datos.

Por ejemplo:

- Creación de tablas.
- Incorporación de columnas.
- Modificación de campos.
- Creación de relaciones entre tablas.

**Reglas importantes:**

- No eliminar la carpeta `migrations/`.
- No eliminar archivos de `migrations/versions/`.
- No ejecutar nuevamente `flask --app app db init`.
- No modificar manualmente el historial de migraciones sin coordinar con el equipo.

---

## 📥 7. Cargar los datos iniciales

Además de crear las tablas, SIMTELE-RISK dispone del archivo:

```text
crear_datos_iniciales.py
```

Este script registra los cuatro casos de estudio iniciales del sistema:

| Caso de estudio | Versión |
|---|---|
| Detención de emergencia | 1.0 |
| Deterioro mecánico | 1.0 |
| Oscilaciones por viento | 1.0 |
| Reconstrucción de sensores | 1.0 |

Para cargar estos registros, ejecutar desde la carpeta principal:

```bash
python crear_datos_iniciales.py
```

Si la ejecución es correcta, aparecerá:

```text
Casos de estudio registrados correctamente
```

El script comprueba si cada caso de estudio ya existe antes de insertarlo.

Por lo tanto, puede ejecutarse nuevamente sin duplicar esos cuatro registros.

**Diferencia entre crear tablas y cargar datos:**

| Comando o archivo | Función |
|---|---|
| `flask --app app db upgrade` | Crea o actualiza las tablas |
| `python crear_datos_iniciales.py` | Inserta los casos de estudio iniciales |

Los dos procedimientos son diferentes y deben ejecutarse en ese orden cuando se prepara una base de datos nueva.

---

## 🧩 8. Organización de los modelos por módulos

Los modelos de la base de datos se encuentran dentro de la carpeta `models/`.

Cada módulo debe mantener sus entidades organizadas para facilitar el trabajo colaborativo.

Ejemplo de estructura:

```text
models/
│
├── __init__.py
│
├── generales.py
│
├── modulo2/
│   ├── __init__.py
│   └── deterioro.py
│
├── modulo1/
│   └── modelos.py
│
├── modulo3/
│   └── modelos.py
│
└── modulo4/
    └── modelos.py
```

Los nombres de los archivos de los módulos pendientes pueden adaptarse a las entidades que cada integrante necesite implementar.

### 8.1. Modelos generales

El archivo `models/generales.py` contiene las entidades compartidas por el sistema:

- CasoEstudio
- Escenario
- Simulacion
- EjecucionMetodo
- IteracionResultado
- ResultadoResumen

Estas entidades constituyen la estructura general de SIMTELE-RISK.

**Los integrantes no deben reemplazar ni eliminar estos modelos para incorporar sus propias tablas.**

### 8.2. Modelos del módulo 2

El archivo `models/modulo2/deterioro.py` contiene las entidades:

- ComponenteMecanico
- MedicionDeterioro

Estas entidades permiten registrar los componentes mecánicos y sus mediciones de deterioro.

Cada módulo debe agregar sus propias entidades sin eliminar las existentes.

---

## 🛠️ 9. Guía para agregar nuevas tablas a la base de datos

Esta sección es especialmente importante para los integrantes que desarrollarán los módulos 1, 3 y 4.

Para incorporar nuevas tablas, se deben seguir estos pasos.

### Paso 1. Crear los archivos del módulo

Dentro de `models/`, crear una carpeta para el módulo correspondiente.

Por ejemplo:

```text
models/
└── modulo3/
    ├── __init__.py
    └── modelos.py
```

### Paso 2. Definir los modelos

Dentro del archivo correspondiente, importar SQLAlchemy:

```python
from extensions import db
```

Después, definir las clases que representarán las tablas.

Ejemplo:

```python
from extensions import db

class EjemploEntidad(db.Model):

    __tablename__ = "ejemplo_entidad"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    descripcion = db.Column(
        db.Text
    )
```

En este ejemplo:

- `class EjemploEntidad(db.Model)` define el modelo.
- `__tablename__` establece el nombre de la tabla en PostgreSQL.
- `id` es la clave primaria.
- `nombre` es un campo obligatorio.
- `descripcion` permite almacenar texto opcional.

Cada integrante debe adaptar los campos a las necesidades de su módulo.

### Paso 3. Registrar los modelos en models/__init__.py

Una vez definidos los modelos, se deben importar en:

```text
models/__init__.py
```

Ejemplo:

```python
from models.generales import (
    CasoEstudio,
    Escenario,
    Simulacion,
    EjecucionMetodo,
    IteracionResultado,
    ResultadoResumen
)

from models.modulo2.deterioro import (
    ComponenteMecanico,
    MedicionDeterioro
)

# Agregar aquí los modelos del módulo 3
from models.modulo3.modelos import (
    EjemploEntidad
)
```

Las importaciones anteriores son ilustrativas para el módulo 3. Cada integrante debe utilizar los nombres reales de sus clases y archivos.

**Importante:** no reemplazar las importaciones anteriores. Cada nuevo módulo debe agregarse conservando los modelos generales y los demás módulos.

### Paso 4. Generar una migración

Abrir la terminal en la carpeta principal del proyecto y ejecutar:

```bash
flask --app app db migrate -m "Agregar tablas del modulo 3"
```

Flask-Migrate analizará los modelos registrados y generará un nuevo archivo dentro de:

```text
migrations/versions/
```

El archivo contendrá las operaciones necesarias para modificar la estructura de PostgreSQL.

### Paso 5. Revisar la migración generada

Antes de aplicar los cambios, abrir el nuevo archivo de migración.

Comprobar que incluya las operaciones esperadas, por ejemplo:

```python
op.create_table(
    'ejemplo_entidad',
    ...
)
```

Si no aparecen las tablas esperadas, revisar las importaciones y la definición de los modelos antes de continuar.

### Paso 6. Aplicar la migración

Cuando la migración esté correctamente generada y revisada, ejecutar:

```bash
flask --app app db upgrade
```

Este comando aplicará los cambios en PostgreSQL.

### Paso 7. Verificar las tablas en pgAdmin

Abrir pgAdmin y navegar hasta:

```text
Servers
└── PostgreSQL
    └── Databases
        └── simtele_risk
            └── Schemas
                └── public
                    └── Tables
```

Hacer clic derecho sobre `Tables` y seleccionar `Refresh`.

Las nuevas tablas deberían aparecer junto con las tablas anteriores.

---

## ⚠️ 10. Reglas para trabajar con migraciones

Para evitar conflictos entre los integrantes, se deben respetar las siguientes reglas:

1. Todos los integrantes deben trabajar con el historial de migraciones existente.
2. No ejecutar `flask db init` nuevamente.
3. No borrar archivos de `migrations/versions/`.
4. No modificar las tablas generales sin autorización del equipo.
5. Cada nuevo modelo debe importarse en `models/__init__.py`.
6. Cada cambio en la estructura de la base de datos debe generar una migración.
7. Los archivos de migración deben incluirse en los commits y Pull Requests.
8. No generar migraciones simultáneamente desde diferentes ramas sin coordinar con el responsable de la base de datos.

### ¿Qué pasa si dos integrantes agregan tablas al mismo tiempo?

Para evitar conflictos, se recomienda que cada integrante desarrolle sus modelos en su propia rama, pero que la generación e integración de las migraciones se coordine con un responsable.

Si se incorporan cambios de otra rama, primero se deben actualizar los archivos del proyecto y comprobar que la base de datos esté al día.

Si GitHub informa conflictos entre migraciones, no se deben borrar archivos ni modificar los identificadores de revisión por cuenta propia. El equipo debe resolver el historial de Alembic antes de aplicar los cambios.

---

## ▶️ 11. Ejecutar la aplicación

Después de configurar la base de datos, instalar las dependencias y aplicar las migraciones, iniciar Flask:

```bash
python app.py
```

También se puede utilizar:

```bash
flask --app app run --debug
```

Abrir el navegador en:

```text
http://127.0.0.1:5000/
```

### Verificar la conexión con PostgreSQL

La aplicación dispone de una ruta para comprobar la conexión:

```text
http://127.0.0.1:5000/verificar-db
```

Si la conexión es correcta, se mostrará:

```json
{
    "mensaje": "Conexión con PostgreSQL exitosa"
}
```

---

## 👥 12. Guía de trabajo colaborativo con Git y GitHub

Para mantener el proyecto organizado, cada integrante debe trabajar en su propia rama.

### 12.1. Actualizar el proyecto

Antes de comenzar una tarea:

```bash
git checkout main
git pull origin main
```

### 12.2. Crear una rama personal

Ejemplos:

```bash
git checkout -b modulo1-detencion
```

```bash
git checkout -b modulo2-deterioro
```

```bash
git checkout -b modulo3-oscilaciones
```

```bash
git checkout -b modulo4-sensores
```

Cada integrante debe trabajar únicamente en las funcionalidades asignadas.

### 12.3. Guardar los cambios

Después de realizar modificaciones:

```bash
git add .
```

Crear un commit descriptivo:

```bash
git commit -m "Agregar modelos del modulo 3"
```

### 12.4. Subir los cambios a GitHub

```bash
git push -u origin nombre-de-tu-rama
```

Si la rama ya existe en GitHub:

```bash
git push
```

### 12.5. Integrar los cambios

Cuando el trabajo esté listo:

1. Entrar al repositorio en GitHub.
2. Seleccionar `Compare & pull request`.
3. Crear un Pull Request dirigido a `main`.
4. Solicitar revisión del equipo.
5. Integrar los cambios mediante Merge pull request cuando sean aprobados.

### 12.6. ¿Qué archivos se deben compartir?

Los siguientes archivos y carpetas deben formar parte del repositorio:

- `app.py`
- `config.py`
- `extensions.py`
- `requirements.txt`
- `.env.example`
- `models/`
- `migrations/`
- `crear_datos_iniciales.py`
- `backend/`
- `templates/`
- `static/`
- `README.md`

**No se deben subir:**

- `.env`
- `venv/`
- `__pycache__/`
- Archivos `.pyc`
- Archivos temporales de desarrollo.

---

## 🆘 13. Solución de problemas frecuentes

### Error: No se puede conectar a PostgreSQL

Posibles causas:

- PostgreSQL no está iniciado.
- El usuario o la contraseña son incorrectos.
- El nombre de la base de datos no coincide.
- El puerto configurado no es correcto.
- El archivo `.env` no existe o no está correctamente configurado.

Comprobar primero las variables de conexión.

### Error: No se encuentra la base de datos

Verificar que se haya creado la base de datos `simtele_risk` en pgAdmin.

### Error: No aparecen las tablas

Ejecutar:

```bash
flask --app app db upgrade
```

Después actualizar la vista de `Tables` en pgAdmin.

### Error: No changes in schema detected

Significa que Flask-Migrate no encontró diferencias entre los modelos registrados y el estado de referencia de las migraciones.

Comprobar:

- Que el modelo esté correctamente definido.
- Que esté importado en `models/__init__.py`.
- Que `app.py` importe los modelos.
- Que se esté utilizando la configuración correcta.

No crear migraciones vacías manualmente.

### Error: Target database is not up to date

Primero revisar el historial y las migraciones pendientes.

Si las migraciones existentes están correctamente integradas, ejecutar:

```bash
flask --app app db upgrade
```

Si hay conflictos de revisiones, coordinar su resolución antes de generar otra migración.

### Error: No se reconoce psycopg

Instalar el controlador:

```bash
pip install "psycopg[binary]"
```

---

## 🎯 14. Objetivo académico

Aplicar métodos numéricos para resolver modelos matemáticos, analizar errores, comparar resultados y estudiar el comportamiento de diferentes escenarios hipotéticos relacionados con el transporte por cable.

---

**SIMTELE-RISK — Métodos Numéricos**

Proyecto académico de desarrollo colaborativo.

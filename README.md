Para empezar, estos son los archivos que necesitamos importar via pip. En mi caso primero genere un *environment* de python nuevo.

```python
python -m venv env
```

Luego genere el *file* de `requirements.txt` y agregue las librerias que necesitamos descargar via `pip`.

```python
fastapi
uvicorn
jinja2
sqlalchemy
```
Una vez instalados los paquetes, cree un *file* llamado `main.py` y coloque el snippet básico para hacer una app via FastAPI.

```python
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
```
La documentación de FastAPI esta [aquí](https://fastapi.tiangolo.com/)

Ya generada mi app, necesito un servidor para revisar el resultado. En este caso estamos usando *uvicorn*. 
Para arrancar el servidor, usamos el siguiente comando en nuestra terminal. 

```bash
uvicorn main:app --reload --port 3333
```

Igual puedes agregar un *file* llamado `run` el cuál contiene el comando de *uvicorn* y lo agregamos via *chmod*

```bash
chmod +x run
``` 
Ahora, vamos a agregar templates de *HTML* via *jinja*. Esta librería nos permite inyectar python dentro de un *html*.

Lo vamos a importar a nuestro archivo `main.py`. De igual forma vamos a agregar la librería *Requests*. 

Una vez importadas las librerías, crearermos una variable (la llamaremos `templates`) que contiene la función Jinja.
```python
#main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
```
Lo que estamos haciendo aquí es buscano la carpeta `templates` dentro de nuestro directorio. Esta carpeta contiene los archivos *html* que rendearemos para nuestra app.

Procedemos a crear nuestra carpeta de templates y nuestros layouts
```bash
mkdir templates
cd templates
touch dashboard.html
touch layout.html
```

De vuelta en el archvio `main.py` creamos un nuevo decorador con `get` y una función que hara el request de nuestro *html*

```python
#main.py
@app.get("/")
def index(request:Request):
    """
    Display the main Dashboard from Youtube.
    """
    return templates.TemplateResponse("index.html",{
        "request":request
    })
```

Nos desplazamos a la carpeta de `templates` y abrimos el archivo de layout. Este archvio va a contener layout básico de *html*.
Lo importante de recordar de este archvio es que le inyectaremos contenido mediante Jinja.
```html
<body>
    <div>
        {% block content %} 
        {% endblock %}
    </div>   
</body>
```
Creado este archvio, abrimos `dashboard.html` y hacemos el layout de nuestra app.
```html
{% extends "layout.html" %}
{% block content %}

<div>
    <h1>Some Content</h1>
</div>

{% endblock %}
```

## Database
Antes de empezar a manejar la base de datos de nuestra app, necesitamos crear los siguientes archvios.

```bash
touch __init__.py
touch database.py
touch models.py
```
Para el ejemplo vamos a usar `sqlite3`. 

### `database.py`
Todo el *boilerplate* code de `SQLAlchemy` para FastAPI esta aquí --> [SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/) 

El *template* básico va dentro de `database.py` y es: 
```python
#database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./stocks.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```
Este *snippet* de código es para conectarnos a la base de datos de sqlite.

Al correr el archivo, generará un *file* llamado `stocks.db`. Este archivo almazenará toda la data necesaria para nuestra app.

Dentro de nuestro *file* `models.py` vamos a crear una clase de pyhton. Esta clase contiene toda la información para nuestra tabla.

```python
#models.py
from sqlalchemy import Column, String, Numeric, Integer
from database import Base

class Video(Base):

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True) 
    price = Column(Numeric(10,2))
``` 

Ya que tenemos nuestra base de datos creada, regresamos a `main.py` y creamos una función `POST`. Esta función enviará la información que deseemos a nuestra base de datos.

Para validar que el usuario haya agregado de forma correcta la información necesaria en su `POST` usaremos la función `BaseModel` de `pydantic`. Esta función se usa dentro de una clase.

En el próximo ejemplo creamos una clase llamada `VideoRequest` que estará compuesta por un elemento `str`

```python
from pydantic import BaseModel

class VideoRequest(BaseModel):
    author: str
```

Para conectarnos a la base el *snippet* de código es:
```python
def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()
```
Ya que tenemos definida nuestra clase con *pydantic*, y tenemos la función que conecta la base de datos, procedemos a crear nuestra función `POST`.

Como ultimo paso, importamos la función `Depends` de fastapi. Esta función valida que haya corrido la función especificada como parametro. 

```python
from fastapi import Depends
from models import Video

@app.post("/video")
def create_video(stock_request: VideoRequest, db:Session=Depends(get_db)):
    """
    Creates a stock and store it on the database.
    """
    video = Video()
    video.author = VideoRequest.author

    db.add(video)
    db.commit()

    return{
        "code":"success",
        "message":"stock created"
    }
``` 


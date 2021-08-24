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

Una vez que tenemos nuestro *layout* básico le agregaremos una tabla sencilla y un panel para filtrar datos. 

Para agregar estilo utilizaré [TailwindCSS]() a través de su CDN.

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

Dentro de nuestro *file* `models.py` vamos a crear una clase de pyhton. Esta clase contiene toda la información para nuestra tabla.

```python
#models.py
from sqlalchemy import Column, String, Numeric, Integer
from database import Base

class Stock(Base):

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True) 
    price = Column(Numeric(10,2))
    forward_pe = Column(Numeric(10,2))
    dividend_yield = Column(Numeric(10,2))
    ma50 = Column(Numeric(10,2))
    ma200 = Column(Numeric(10,2))

``` 

Ya que tenemos nuestra base de datos creada, regresamos a `main.py` y agregamos el siguiente código.

```python
#main.py
import models 
from sqlalchemy.orm import Session
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
```

Al agregarlo y guardar, se generará un *file* llamado `stocks.db`. Este archivo almazenará toda la data necesaria para nuestra app.

Podemos revisar el *schema* de la tabla si dentro de la línea de comando usamos:
```bash
sqlite3 stocks.db
.schema
select * from stocks;
insert 
```
En esta [liga](https://www.youtube.com/watch?v=XA3w8tQnYCA) hay un video de como instalar sqlite3 si no lo tienes en tu computadora. 

Ya que vimos que nuestra base de datos fue creada, podemos comenzar a enviar información a la misma. Para esto crearemos una función `POST`. 

Para validar que el usuario haya agregado de forma correcta la información necesaria en su `POST` usaremos la función `BaseModel` de `pydantic`. Esta función se usa dentro de una clase.

```python
from pydantic import BaseModel

class StockRequest(BaseModel):
    symbol:str
```

En este ejemplo la clase `StockRequest` contiene un `string`. 

Ya con la clase creada podemos crear nuestro `POST` request y agregarsela. Con esta validación nos aseguramos que el usuario envíe al servidor la información en el formato correcto.

```python
#main.py
@app.post("/stock")
def create_stock(stock_request:StockRequest):
    """
    Create a Stock and store it into the database.
    """

    return{
        "code":"success",
        "message":"stock created"
    }
```
Para probarla podemos usar un cliente tipo Postman y hacer el envío de un `json`
```json
{
    "symbol":"AAPL"
}
```

Antes de comenzar a enviar datos a la base de datos, tenemos que estar seguros de que la base está conectada. Para eso utilizaremos la librería `Depends` que forma parte de fastapi.
```python
from fastapi import Depends
```
Ahora creamos una función para revisar la sesión.
```python
#main.py
def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close( )
```
Y agregamos la función a nuestro `POST`.

Adicional, vamos a importar el modelo `stock` que creamos en el archivo `models.py` para poder utilizarlo en nuestra función.

Finalmente, vamos a usar nuestro `POST` request para agregar un stock a nuestra base de datos.

Dentro del modelo `Stock` creamos una columna llamada `symbol` vamos a seleccionar que el envío de nuestro stock sea a esta columna. Ya validamos que el usuario utilizará un *string* para *symbol* usando la clase `StockRequest()` entonces procedemos a terminar nuestra función. 


```python
#main.py

from models import Stock

@app.post("/stock")
def create_stock(stock_request:StockRequest, db: Session=Depends(get_db)):
    """
    Create a Stock and store it into the database.
    """
    # Tramos la clase Stock() de models.py la cuál definio nuestras columnas en nuestra base de datos.
    stock = Stock()

    # Apuntamos a la columna symbol
    stock.symbol = stock_request.symbol

    #Mandamos los datos a la base de datos.
    db.add(stock)
    db.commit()

    return{
        "code":"success",
        "message":"stock created"
    }
```

## Background Tasks
Tenemos la opción de correr una tarea y enviar un mensaje al usuario mientras la misma se completa. 
Para comezar, tenemos que importar:

```python
from fastapi import BackgroundTasks
```
Y agregamos como parametro a nuestro `POST` request:
```python
#main.py
def create_stock(stock_request:StockRequest, background_tasks:BackgroundTasks, db: Session=Depends(get_db))
     
```
Ahora, dentro de nuestra función, vamos a colocar las funciones de las que esperaremos una respuesta.
```python
#main.py
def create_stock(stock_request:StockRequest, background_tasks:BackgroundTasks, db: Session=Depends(get_db)):
    background_tasks.add_task()
```
En este caso vamos a crear una función que irá por la información de un determinado stock. Este llamado se puede tardar en completar, por eso lo agregamos como *backgorund task* y se hace de forma asincrona.
```python
#main.py
def fetch_stock_data(id:int):
    pass
```
Lo que ocurrirá ahora es que 
1. vamos a agregar un record a la base de datos. Este record tendrá asignado un ID de forma automática (porque asi lo decidimos al crear el modelo). 
2. Vamos usar ese id como parametro para nuestra función `fetch_stock_data`.
3. Para seleccionar el id usamos `stock.id`
4. La función se usará como parametro dentro de nuestra función `background_tasks.add_task()`
5. A su vez, el parametro de `fetch_stck_data()` va dentro de `background_tasks.add_task()` dandonos como resultado.
   
```python
#main.py
background_tasks.add_task(fetch_stock_data, stock.id)
```
Completamos la función `fetch_stock_data`
```python
#main.py
def fetch_stock_data(id:int):
    #Iniciamos una sesión en nuestra base de datos.
    db=SessionLocal()

    #Hacemos un query para seleccionar el id que nos llego como parametro.
    stock = db.query(Stock).filter(Stock.id==id).first()

    #Hacemos referencia a la columna a la cuál queremos agregar información.
    stock.forward_pe = 10

    #Agregamos a la base y cerramos la conexión.
    db.add(stock)
    db.commit()
```
Para que todo esto funcione, tenemos que convertir nuestra función `POST` a `async`.

```python
async def create_stock()
```
 
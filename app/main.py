from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()
@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/")
def index(request:Request):
    """
    Display the main Dashboard from Youtube.
    """
    return templates.TemplateResponse("dashboard.html",{
        "request":request
    })
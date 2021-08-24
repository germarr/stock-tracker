from fastapi import FastAPI
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
import models 
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel
from models import Stock


class StockRequest(BaseModel):
    symbol:str

templates = Jinja2Templates(directory="templates")


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/")
def index(request:Request):
    """
    Display the main Dashboard from Youtube.
    """
    return templates.TemplateResponse("dashboard.html",{
        "request":request,
        "somevar":2
    })

@app.post("/stock")
def create_stock(stock_request:StockRequest, db:Session=Depends(get_db)):
    """
    Create a Stock and store it into the database.
    """
    stock = Stock()
    stock.symbol = stock_request.symbol

    db.add(stock)
    db.commit()

    return{
        "code":"success",
        "message":"stock created"
    }
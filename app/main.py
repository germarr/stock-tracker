from fastapi import FastAPI
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
import models 
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel
from models import Stock
import yfinance

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

def fetch_stock_data(id:int):
    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id==id).first()

    yahoo_data = yfinance.Ticker(stock.symbol)

    stock.ma200 = yahoo_data.info["twoHundredDayAverage"]
    stock.ma50 = yahoo_data.info["fiftyDayAverage"]
    stock.price =yahoo_data.info["previousClose"]
    stock.forward_pe =yahoo_data.info["forwardPE"]
    stock.forward_eps = yahoo_data.info["forwardEps"]

    if yahoo_data.info["dividendYield"] is not None:
        stock.dividend_yield =yahoo_data.info["dividendYield"]*100

    db.add(stock)
    db.commit()

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
async def create_stock(stock_request:StockRequest, background_tasks:BackgroundTasks, db:Session=Depends(get_db)):
    """
    Create a Stock and store it into the database.
    """ 

    stock = Stock()
    stock.symbol = stock_request.symbol

    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return{
        "code":"success",
        "message":"stock created"
    }
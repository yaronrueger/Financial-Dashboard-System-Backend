from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel
import datetime
import os
import jwt
import time
import json


import excelfile as excelFile
from authentication import *
from models import *

app = FastAPI(title="Quizapp API")

###########################################
############# DB MANAGEMENT #############
###########################################

DB_URL = os.environ.get("DB_URL", "sqlite://./data/db.sqlite3")
JWT_SECRET = os.environ.get("JWT_SECRET", "secretlolol")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

register_tortoise (
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["main", "models", "authentication"]},
    generate_schemas=True,
    add_exception_handlers=True
)

###########################################
############# USER MANAGEMENT #############
###########################################

def verify_permission(token):
    #TODO: Change your Registrationtoken
    return token=="YOUR_REGISTRATION_TOKEN"

@app.post("/api/login", description="Returns a bearer Access Token on successful login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    tokendump = {
        "id": user_obj.id,
        "sub": user_obj.username,
        "roles": ["user"], 
        "exp": int(time.time() + 7200) # Expires in 2h / 2*3600 seconds
    }
    token = jwt.encode(tokendump, JWT_SECRET)
    return {"access_token" : token, "token_type" : "bearer"}

@app.post("/api/register", response_model=User_Pydantic, description="Creates a new User with given credentials")
async def register(user: UserIn_Pydantic, token: str = ""):
    if not verify_permission(token):
        raise HTTPException(status_code=404, detail="wrong token") 
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

async def get_current_user(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return await User_Pydantic.from_tortoise_orm(user)

async def is_admin_user(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
        if not payload.get("id") == 4:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Admin privileges")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return await User_Pydantic.from_tortoise_orm(user)

#################################
############# LOGIC #############
#################################

@app.get("/api", description="Returns API Status")
async def getStatus():
    return{"API":"online"}

@app.get("/api/refresh")
async def getCash(user: User_Pydantic = Depends(get_current_user)):
    excelFile.refresh()

@app.get("/api/cash")
async def getCash(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getCashArray()

@app.get("/api/cash/yearValues")
async def getCash(user: User_Pydantic = Depends(get_current_user)):
    return {"yearValues":excelFile.getCashArrayYearValues()}

@app.get("/api/income")
async def getIncome(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getIncomeArray()

@app.get("/api/income/searchpage")
async def getIncomeSearch(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.get_artDerEinkünfteSuche()

@app.get("/api/income/names")
async def getIncomeNames(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getIncomeNames()

@app.post("/api/income/specific")
async def getSpecificIncome(income_data: IncomeData, user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getSpecificIncome(income_data.income)

@app.get("/api/expenses")
async def getExpenses(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getExpenseArray()

@app.get("/api/expenses/searchpage")
async def getExpenseSearch(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.get_ausgabenSuche()

@app.get("/api/expenses/names")
async def getExpensesNames(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getExpensesNames()

@app.post("/api/expenses/specific")
async def getSpecificIncome(expenses_data: ExpensesData, user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getSpecificExpense(expenses_data.expenses)

@app.get("/api/sum")
async def getExpenses(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getSumArray()

@app.get("/api/startpage")
async def getStartpageInfos(user: User_Pydantic = Depends(get_current_user)):
    username = user.username
    cash = excelFile.getCashYear()
    income = excelFile.getIncomeYear()
    expense = excelFile.getExpenseYear()
    incomeValues = excelFile.getIncomeYearLastThree()
    expenseValues = excelFile.get_ausgabenJahrLastThree()
    incomePercent = excelFile.getIncomeYearPercent()
    expensePercent = excelFile.getExpenseYearPercent()
    return{
        "username": username,
        "cashYear": cash,
        "incomeYear": income,
        "expenseYear": expense,
        "incomeValues":incomeValues,
        "expenseValues":expenseValues,
        "incomePercent": incomePercent,
        "expensePercent": expensePercent
    }

@app.get("/api/startpage/favourites")
async def getStartpageFavorites(user: User_Pydantic = Depends(get_current_user)):
    return excelFile.getStartpageFavorites()

@app.post("/api/startpage/favourites/change")
async def getStartpageFavorites(data: Data, user: User_Pydantic = Depends(get_current_user)):
    excelFile.addOrRemoveTitle(data.title, data.type)
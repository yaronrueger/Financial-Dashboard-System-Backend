import pandas as pd
import dropbox
import io
from models import *
from passlib.hash import bcrypt
import datetime
import numpy as np

# Set up Dropbox connection
#TODO: Change your Dropbox Appkey, AppSecret and refreshtoken
appkey='YOUR_APPKEY'
appSecret='YOUR_APPSECRET'
refreshToken='YOUR_REFRESHTOKEN'
dbx = dropbox.Dropbox( app_key = appkey, app_secret = appSecret, oauth2_refresh_token = refreshToken)
# Download Excel file as bytes object
file_path = '/mappe1.1.xlsx'
file_metadata, file_content = dbx.files_download(file_path)
file_bytes = file_content.content
#arrays
cashArray=[]
incomeArray=[]
expenseArray=[]
sumArray=[]
favoritesArray=[]
incomeTitlesArray = []
expenseTitlesArray = []

def refresh():
    global file_metadata, file_content, file_bytes
    file_metadata, file_content = dbx.files_download(file_path)
    file_bytes = file_content.content
    updateStartpageFavorites()

# Function to extract data from the Excel file
def getData():
    # Clearing the lists before populating them with new data
    cashArray.clear()
    incomeArray.clear()
    expenseArray.clear()
    sumArray.clear()
    # Opening the Excel file as a bytes object
    with io.BytesIO(file_bytes) as data:
        # Reading the Excel file into a pandas DataFrame
        df = pd.read_excel(data)
        #reading file
        # Iterating over the rows of the DataFrame, starting from the 4th row
        for i in range(3, len(df)):
            #cashArray
            # If the second column of the row is "Monatliches Barvermögen", extract the data
            if(df.iloc[i, 1]=="Monatliches Barvermögen"):
                datavalues=[]
                # Iterating over the columns of the row, starting from the 3rd column
                for j in range(2,len(df.columns)):
                    if np.isnan(df.iloc[i, j]):
                        datavalues.append(0)
                    else:
                        datavalues.append(round(df.iloc[i, j], 2))
                    if(df.iloc[i-1, j]=="DEZ"):
                        break
                cell_value = df.iloc[i, 1]
                cashArray_obj = Cash_Tortoise(title=cell_value,yearValues=datavalues,sumValue=round(df.iloc[i, 14],2))
                cashArray.append(cashArray_obj)
            #income
            # If the second column of the row is "ART DER EINKÜNFTE", extract the data
            if(df.iloc[i, 1]=="ART DER EINKÜNFTE"):
                for m in range (i+1, len(df)):
                    datavalues=[]
                    for j in range(2,len(df.columns)):
                        if np.isnan(df.iloc[m, j]):
                            datavalues.append(0)
                        else:
                            datavalues.append(round(df.iloc[m, j], 2))
                        if(df.iloc[i, j]=="DEZ"):
                            break
                    cell_value = df.iloc[m, 1]
                    if(df.iloc[m, 1]!="sumArray EINKÜNFTE"):
                        cashArray_obj = Income_Tortoise(title=cell_value,yearValues=datavalues,sumValue=round(df.iloc[m, 14], 2))
                        incomeArray.append(cashArray_obj)
                    if(df.iloc[m, 1]=="sumArray EINKÜNFTE"):
                        sum_obj = Sum_Tortoise(title=cell_value,yearValues=datavalues,sumValue=round(df.iloc[m, 14], 2))
                        sumArray.append(sum_obj)
                        break
            #expenses
            # If the second column of the row is "expenseArray", extract the data
            if(df.iloc[i, 1]=="expenseArray"):
                for m in range (i+1, len(df)):
                    datavalues=[]
                    for j in range(2,len(df.columns)):
                        if np.isnan(df.iloc[m, j]):
                            datavalues.append(0)
                        else:
                            datavalues.append(round(df.iloc[m, j], 2))
                        if(df.iloc[i, j]=="DEZ"):
                            break
                    cell_value = df.iloc[m, 1]
                    if(df.iloc[m, 1]!="sumArray expenseArray"):
                        cashArray_obj = Expenses_Tortoise(title=cell_value,yearValues=datavalues,sumValue=round(df.iloc[m, 14], 2))
                        expenseArray.append(cashArray_obj)
                    if(df.iloc[m, 1]=="sumArray expenseArray"):
                        sum_obj = Sum_Tortoise(title=cell_value,yearValues=datavalues,sumValue=round(df.iloc[m, 14], 2))
                        sumArray.append(sum_obj)
                        break
            #end
            # If the second column of the row is "sumArray expenseArray", end the loop
            if(df.iloc[i, 1]=="sumArray expenseArray"):
                break

# Function to get the available cashArray
def getCashArray():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    obj = cashArray[0]
    count = 0
    for number in obj.yearValues[:currentMonth]:
        count += number
    return Cash_Tortoise(title=obj.title,yearValues=obj.yearValues[:currentMonth],sumValue=round(count,2))

# Function to get the type of income
def getIncomeArray():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    value=[]
    for obj in incomeArray:
        count = 0
        for number in obj.yearValues[:currentMonth]:
            count += number
        value.append(IncomeApp_Tortoise(title=obj.title,yearValues=obj.yearValues[:currentMonth],sumValue=round(count,2), percent=getYearPercentSpeical(obj.yearValues[:currentMonth])))
    return value

# Function to get the expenses
def getExpenseArray():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    value=[]
    for obj in expenseArray:
        count = 0
        for number in obj.yearValues[:currentMonth]:
            count += number
        value.append(ExpensesApp_Tortoise(title=obj.title,yearValues=obj.yearValues[:currentMonth],sumValue=round(count,2), percent=getYearPercentSpeical(obj.yearValues[:currentMonth])))
    return value

# Function to get the sumValues of income and expenses
def getSumArray():
    getData()
    return sumArray

# Function to get the total cashArray for the year
def getCashYear():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    value = 0
    for number in cashArray[0].yearValues[:currentMonth]:
        value += number
    return round(value,2)

# Function to get the total income for the year
def getIncomeYear():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    value = 0
    for number in sumArray[0].yearValues[:currentMonth]:
        value += number
    return round(value,2)

# Function to get the total expenses for the year
def getExpenseYear():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    value = 0
    for number in sumArray[1].yearValues[:currentMonth]:
        value += number
    return round(value,2)

# Function to get the percentage change in income for the year
def getIncomeYearPercent():
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    getData()
    return percentageChange(getLastTwo(incomeArray[-1].yearValues[:currentMonth]))

# Function to get the percentage change in expenses for the year
def getExpenseYearPercent():
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    getData()
    return percentageChange(getLastTwo(expenseArray[-1].yearValues[:currentMonth]))

def getLastThree(arr):
    if len(arr) >= 3:
        return arr[-3:]
    else:
        return arr[-len(arr):]
    
def getLastTwo(arr):
    if len(arr) >= 2:
        return arr[-2:]
    else:
        return arr[-len(arr):]   
    
def percentageChange(arr):
    if arr[0] == 0:
        return 0
    if len(arr) == 1:
        return 0
    elif len(arr) >= 2:
        return round(((arr[1] - arr[0]) / arr[0]) * 100, 2)

# Function to get the last three values of the income for the year
def getIncomeYearLastThree():
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    getData()
    return getLastThree(incomeArray[-1].yearValues[:currentMonth])

# Function to get the last three values of the expenses for the year
def getExpenseYearLastThree():
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    getData()
    return getLastThree(expenseArray[-1].yearValues[:currentMonth])

# Function to get the names of the income sources
def getIncomeNames():
    getData()
    data =[]
    for income in incomeArray:
        data.append(income.title)
    return {'title': data}

# Function to get the names of the expense sources
def getExpensesNames():
    getData()
    data = []
    for expense in expenseArray:
        data.append(expense.title)
    return {'title': data}

# Function to get the specific income source
def getSpecificIncome(incomeVar):
    for name in getIncomeArray():
        if(name.title == incomeVar):
            return name
    return {'error': 'title not found'}

# Function to get the specific expense source
def getSpecificExpense(expenseVar):
    for name in getExpenseArray():
        if(name.title == expenseVar):
            return name
    return {'error': 'title not found'}

# Function to get the available cashArray values for the year
def getCashArrayYearValues():
    getData()
    # Aktuelles Datum und Zeit abrufen
    now = datetime.datetime.now()
    # Den aktuellen Monat extrahieren
    currentMonth = now.month
    return cashArray[0].yearValues[:currentMonth]


def getYearPercentSpeical(obj):
    return percentageChange(getLastTwo(obj))


def getYearLastThreeSpecial(obj):
    return getLastThree(obj)

def getStartpageFavorites():
    return favoritesArray


def updateStartpageFavorites():
    getData()
    global favoritesArray
    global expenseArray
    global incomeArray
    favoritesArray = []
    for income in incomeArray:
        if income.title in incomeTitlesArray:
            favoritesArray.append(SearchPage_Tortoise(typeOfValue="income", title=income.title, yearValues=income.yearValues, sumValue=income.sumValue, saved=True, lastThreeValues=getYearLastThreeSpecial(income.yearValues), percent=getYearPercentSpeical(income.yearValues)))
    for expense in expenseArray:
        if expense.title in expenseTitlesArray:
            favoritesArray.append(SearchPage_Tortoise(typeOfValue="expense", title=expense.title, yearValues=expense.yearValues, sumValue=expense.sumValue, saved=True, lastThreeValues=getYearLastThreeSpecial(expense.yearValues), percent=getYearPercentSpeical(expense.yearValues)))

def addOrRemoveTitle(title: str, type: str):
    if type == 'income':
        title_list = incomeTitlesArray
    elif type == 'expense':
        title_list = expenseTitlesArray

    if title in title_list:
        title_list.remove(title)
        title_list.sort()
    else:
        title_list.append(title)
        title_list.sort()
    updateStartpageFavorites()


def get_incomeArraySuche():
    fusion_array = []
    favoritesArray_titles = {fav.title: fav for fav in favoritesArray}
    for income in getIncomeArray():
        if income.title in favoritesArray_titles:
            new_search_page = SearchPage_Tortoise(
                typeOfValue="income",
                title=income.title,
                yearValues=income.yearValues,
                sumValue=income.sumValue,
                saved=True,
                lastThreeValues = getYearLastThreeSpecial(income.yearValues),
                percent = getYearPercentSpeical(income.yearValues)
            )
            fusion_array.append(new_search_page)
        else:
            new_search_page = SearchPage_Tortoise(
                typeOfValue="income",
                title=income.title,
                yearValues=income.yearValues,
                sumValue=income.sumValue,
                saved=False,
                lastThreeValues = getYearLastThreeSpecial(income.yearValues),
                percent = getYearPercentSpeical(income.yearValues)
            )
            fusion_array.append(new_search_page)
    return fusion_array

def get_expenseArraySuche():
    fusion_array = []
    favoritesArray_titles = {fav.title: fav for fav in favoritesArray}
    for expense in getExpenseArray():
        if expense.title in favoritesArray_titles:
            new_search_page = SearchPage_Tortoise(
                typeOfValue="expense",
                title=expense.title,
                yearValues=expense.yearValues,
                sumValue=expense.sumValue,
                saved=True,
                lastThreeValues = getYearLastThreeSpecial(expense.yearValues),
                percent = getYearPercentSpeical(expense.yearValues)
            )
            fusion_array.append(new_search_page)
        else:
            new_search_page = SearchPage_Tortoise(
                typeOfValue="expense",
                title=expense.title,
                yearValues=expense.yearValues,
                sumValue=expense.sumValue,
                saved=False,
                lastThreeValues = getYearLastThreeSpecial(expense.yearValues),
                percent = getYearPercentSpeical(expense.yearValues)
            )
            fusion_array.append(new_search_page)
    return fusion_array
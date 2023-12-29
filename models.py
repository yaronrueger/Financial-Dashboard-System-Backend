from pydantic import BaseModel, Field
from typing import List
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.postgres.fields import ArrayField

class Cash_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()

class Income_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()

class Expenses_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()

class IncomeApp_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()
    percent = fields.FloatField()


class ExpensesApp_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()
    percent = fields.FloatField()


class Sum_Tortoise(Model):
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()

class SearchPage_Tortoise(Model):
    typeOfValue = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    yearValues = ArrayField(base_field=fields.FloatField())
    sumValue = fields.FloatField()
    saved = fields.BooleanField()
    lastThreeValues = ArrayField(base_field=fields.FloatField())
    percent = fields.FloatField()

class ExpensesData(BaseModel):
    expenses: str

class IncomeData(BaseModel):
    income: str

class Data(BaseModel):
    title: str
    type: str
 
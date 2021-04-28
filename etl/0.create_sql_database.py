import sqlalchemy as sa
import pandas as pd
import sqlite3

xl = pd.ExcelFile("data/raw/applications.xlsx")
res = len(xl.sheet_names)
e = sa.create_engine("sqlite:///data/sql/raw_data.sqlite")

for i in range(0,res-1):
        pd.read_excel("data/raw/applications.xlsx", sheet_name=i).to_sql("application_tab_%s" %i, e)

# TODO : Need to build SQL table with shorter names to import csv into ###########
# 
# conn = sqlite3.connect('./data/sql/raw_data.sqlite')
# c = conn.cursor()

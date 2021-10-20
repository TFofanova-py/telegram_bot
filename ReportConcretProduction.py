import openpyxl
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

book = openpyxl.open('Book1.xlsx', data_only=True)
sheet = book.active

nowDate = datetime.now()
startDate_plan = sheet['R483'].value
finishDate_plan = sheet['S483'].value

duration_plan = pd.date_range(startDate_plan, finishDate_plan)
duration_fact = pd.date_range(startDate_plan, nowDate)

concreteProduction_plan = round(sheet['G483'].value / (len(duration_plan)), 2)
concreteProduction_fact = round(sheet['H483'].value / (len(duration_fact)), 2)

myList_concreteProduction_plan = []
for j in range(len(duration_plan)):
    myList_concreteProduction_plan.append(round(sheet['G483'].value / (len(duration_plan)), 2))

myList_concreteProduction_fact = []
for j in range(len(duration_fact)):
    myList_concreteProduction_fact.append(round(sheet['H483'].value / (len(duration_fact)), 2))

fig = plt.figure()
plt.title('План/факт выработки по устройству бетонной подготовки корпуса 6', fontsize=10)
plt.bar(duration_fact, myList_concreteProduction_fact, color='r')
plt.bar(duration_plan, myList_concreteProduction_plan, color='g')
plt.xticks(rotation=90)
plt.show()

if str(nowDate) <= finishDate_plan and \
        sum(myList_concreteProduction_fact) >= (sum(myList_concreteProduction_plan) / len(duration_plan) * len(duration_fact)):
    print('На '
          + nowDate.strftime('%d.%m.%Y')
          + ' мы в графике.\nВыработка составляет '
          + str(myList_concreteProduction_fact[0])
          + ' м3/в смену')
else:
    print('На '
          + nowDate.strftime('%d.%m.%Y')
          + ' отстаем, '
          + str(myList_concreteProduction_fact[0])
          + ' м3/в смену - фактическая выработка.\nПлановая выработка '
          + str(myList_concreteProduction_plan[0]) + ' м3/в смену')






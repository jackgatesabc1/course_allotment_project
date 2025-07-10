import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, StringConstraints
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random


#For creating unit tests we need students data without the preferences
df = pd.read_csv('sample_files/students_data_with_preferences.csv')



def unit_test_1(df): 

    #{'AE':{0,1},'CE':{0,1}}
    #'AE','CE'

    #12females, and 30 males per department, and we have two departments, and two sections, and two projects, and 7 group size
    #Preferences are distributed across project1, project2, i.e no project is more preferred overall
    departments = ['AE']*42+['CE']*42
    genders = ['male']*30+['female']*12+['male']*30+['female']*12
    cpis = [10]*84
    preferences = [[50,50]]*84
    df = df.iloc[:84].copy()
    df['department'] = departments
    df['gender']=genders
    df['cpi'] = cpis
    df['preferences'] = preferences
    df.to_csv('sample_files/unit_test_1.csv', index=False)
    return df

# print(unit_test_1(df).iloc[30:40])

    


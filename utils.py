from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, conlist, StringConstraints, PrivateAttr
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random
import ast
from collections import defaultdict
from scipy.stats import truncnorm
import os
import config

#These below values are imported in all other files, so here is the place where we fix these values
# no_of_projects =6 
# no_of_sections = 8 #S1 to S8
# groupSize = 6
# department_literal = Literal['AE','CE','CH','CL','CS','EC','EE','EN','EP','ES','ME','MM']
# max_size_for_dept_diversity = 4 #maximum number of students from a single department in a group, if this is not satisfied, then the group is not considered to have department diversity
#Assumption: These available slots will be given to us by the professor. Currently using last year's slots
# available_slots= {'CL': {0, 4}, 'ME': {0, 4}, 'MM': {1, 5}, 'CE': {1, 5}, 'CS': {2, 6}, 'AE': {2, 6}, 'CH': {2}, 'EN': {2, 6}, 'ES': {3, 7}, 'EC': {3, 7}, 'EP': {3, 7}, 'EE': {3, 7}}


# student_count_per_department = {'CL': 145, 'ME': 196, 'MM': 132, 'CE': 168, 'CS': 185, 'AE': 81, 'CH': 28, 'EN': 46, 'ES': 45, 'EC': 35, 'EP': 60, 'EE': 204}



# These will hold your dynamic classes

    


# other globals, unchanged
list_of_students = []
departments = set()
roll_to_student = {}
student_count_per_department = defaultdict(int)



class variableContainer:
    def __init__(self,list_of_alphas, id):
        self.alphas = list_of_alphas
        self.id = id
        self.index_to_student = [] # It will give the student(object of class 'Student') corresponding to a particular alpha at that 'index', i.e self.index_to_student[i] gives student who corresponds to self.alphas[i]
        for alpha in list_of_alphas:
            roll_number = alpha.Name().split('_')[1]
            self.index_to_student.append(roll_to_student[roll_number])

    def maleSum(self):
        male_indices=[]
        for i in range(len(self.alphas)):
            if(self.index_to_student[i].gender=='male'):
                male_indices.append(i)
        return sum(self.alphas[i] for i in male_indices)
    
    def femaleSum(self):
        female_indices=[]
        for i in range(len(self.alphas)):
            if(self.index_to_student[i].gender=='female'):
                female_indices.append(i)
        return sum(self.alphas[i] for i in female_indices)
    
    def cpiSumScaled(self): #sum of CPIs multiplied by 100
        return sum(self.alphas[i]*int(self.index_to_student[i].cpi*100) for i in range(len(self.alphas)))
    
    def numberOfStudents(self):
        return sum(self.alphas)
    
    def departmentSum(self, department: config.department_literal):
        department_indices=[]
        for i in range(len(self.alphas)):
            if(self.index_to_student[i].department==department):
                department_indices.append(i)
        return sum(self.alphas[i] for i in department_indices)
    
    def preferencesSum(self):
        list_of_preferences=[]
        for i,alpha in enumerate(self.alphas):
            student  = self.index_to_student[i]
            projectId = int(alpha.Name().split('_')[2]) 
            preference = student.preferences[projectId]
            list_of_preferences.append(preference*alpha)
        return sum(list_of_preferences)
    
    def getAllocation(self, solver): #returns a List[Student] based on whether their alpha here in this container is 1 or 0
        allocatedStudents = []
        for i,alpha in enumerate(self.alphas):
            if (solver.value(alpha)>0.5):
                allocatedStudents.append(self.index_to_student[i])
        return allocatedStudents
    
    def departmentDiversity(self,model):
        boolvar = model.new_bool_var(f'department_diversity_{id(self)}') #This is a boolean variable which will be true if group has department diversity
        for department in departments:
            model.add(self.departmentSum(department) <= config.max_size_for_dept_diversity).only_enforce_if(boolvar)
        return boolvar


def gauss(low,high,sigma): #randomly generates an integer from a truncated gaussian distribution
    mean = (low+high)/2
    return int(round(truncnorm.rvs((low-mean)/sigma, (high-mean)/sigma, loc=mean, scale=sigma)))
            

def generate_and_save_students_data(filetype:Literal['json','csv']='csv'): #randomly generated CPI, preferences and saves it
    ##Last year's DE 250 dataset
    student_df = pd.read_csv('sample_files/students_data_random_names.csv')
    student_count=  len(student_df)
    
    #Uniformly generated preferences and cpis
    # preferences = [[random.randint(0, 100) for _ in range(no_of_projects)] for _ in range(student_count)] 
    # cpis = [random.randint(600, 1000)/100 for _ in range(student_count)] 
       
    # Non-uniform preferences and cpis
    preferences = [[gauss(60,100,15), gauss(0,40,10), gauss(40,100,20), gauss(0,30,5), gauss(0,20,5),gauss(0,100,40)] for _ in range(student_count)] #randomly generated preferences
    cpi_low, cpi_high, cpi_mean= 6,10,8
    std = 2
    a, b = (cpi_low - cpi_mean) / std, (cpi_high - cpi_mean) / std  # if std=1, mean=8
    trunc_normal = truncnorm(a, b, loc=cpi_mean, scale=std)
    samples = trunc_normal.rvs(student_count).tolist() # generate 1000 samples
    cpis = [round(sample,2) for sample in samples]


    list_of_students = []
    for i,student in student_df.iterrows():
        list_of_students.append(config.Student(name=student['name'], gender =student['gender']  ,rollNumber=student['rollNumber'],cpi=cpis[i], department=student['department'], preferences=preferences[i]))

    df= pd.DataFrame([student.model_dump() for student in list_of_students])
    if filetype=='csv':
        df.to_csv('sample_files/students_data_with_preferences.csv',index=False) #In this data, preferences were generated randomly for each student
    else:
        if(not isinstance(df['preferences'].iloc[0]), list):
            df['preferences'] = df['preferences'].apply(ast.literal_eval)
        df.to_json('sample_files/students_data_with_preferences.json', indent=2, orient='records')
    
    

    

def absolute_value(x,model: cp_model.CpModel): #check the 100000 
    absolute = model.new_int_var(0, 500000, f"abs_{id(x)}")  # Assuming a max value of 500000 for the absolute value variable
    model.add(x<=absolute)
    model.add(x>=-1*absolute)
    return absolute
    


        
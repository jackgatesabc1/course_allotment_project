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

#These below values are imported in all other files, so here is the place where we fix these values
no_of_projects =6 
no_of_sections = 8 #S1 to S8
groupSize = 6
# departments = ['AE','CE','CH','CL','CS','EC','EE','EN','EP','ES','ME','MM'] #List of all departments, used in utils.py and group_allocator.py

class Student(BaseModel):
    name: str
    gender: Literal['male', 'female']
    rollNumber: Annotated[str,StringConstraints(pattern=r"2\dB\d{4}")]
    cpi: Annotated[float, Field(ge=0.00, le=10.00)]
    department: Literal['AE','CE','CH','CL','CS','EC','EE','EN','EP','ES','ME','MM']
    preferences: Annotated[List[Annotated[int, Field(ge=0, le=100)]],Field(min_length=no_of_projects, max_length=no_of_projects)]

    
    def __init__(self,**data):
        super().__init__(**data)

class allocated_student(BaseModel):
    section: Annotated[int,Field(ge=1,le=no_of_sections)] #note that here section numbers are from 1 but not 0, because this class is for real data
    project: Annotated[int,Field(ge=1,le=no_of_projects)]
    group: Annotated[int,Field(ge=1)]
    name: str
    cpi: Annotated[float, Field(ge=0.00, le=10.00)]
    gender: Literal['male', 'female']
    department: Literal['AE','CE','CH','CL','CS','EC','EE','EN','EP','ES','ME','MM']
    allocated_preference: Annotated[int,Field(ge=0,le=100)]
    preferences: Annotated[List[Annotated[int, Field(ge=0, le=100)]],Field(min_length=no_of_projects, max_length=no_of_projects)]
  

df = pd.read_csv('students_data_with_preferences.csv')
df['preferences'] = df['preferences'].apply(ast.literal_eval)
list_of_students = [Student(**row) for row in df.to_dict(orient='records')]
departments = set() #to store all departments
roll_to_student = {}
student_count_per_department = defaultdict(int) #to store the number of students in each department, so that we can use it later in section_allocator.py
for student in list_of_students:
    roll_to_student[student.rollNumber] = student #check whether python maps allow this
    departments.add(student.department) #to store all departments, so that we can use it later in utils.py and group_allocator.py
    student_count_per_department[student.department] += 1 #to store the number of students in each department, so that we can use it later in section_allocator.py

class Section(BaseModel):
    section: Annotated[int,Field(ge=0,le=no_of_sections-1)] #note that section numbers are from 0 but not 1 (this is to maintain consistency while indexing)
    students: List[Student]
    _model: cp_model.CpModel = PrivateAttr() #check whether needed
    _projectAlphas: list[list[cp_model.IntVar]] = PrivateAttr(default_factory=list) #check, uncomment this if needed

    def __init__(self, **data):
        super().__init__(**data)
        self._model = cp_model.CpModel()
        self._projectAlphas = [[self._model.new_bool_var(f"projectAlpha_{student.rollNumber}_{project_id}") for project_id in range(no_of_projects)] for student in self.students]

class Project(BaseModel):
    projectCode: Annotated[int,Field(ge=0,le=no_of_projects-1)] #note that project numbers are from 0 but not 1 (this is to maintain consistency while indexing)
    section: Annotated[int,Field(ge=0,le=no_of_sections-1)]
    students: List[Student]
    _model: cp_model.CpModel = PrivateAttr() #check whether needed
    _groupAlphas: list[list[cp_model.IntVar]] = PrivateAttr(default_factory=list) #check, uncomment this if needed

    def __init__(self, **data):
        super().__init__(**data)
        no_of_groups = len(self.students)//groupSize
        self._model = cp_model.CpModel()  
        self._groupAlphas = [[self._model.new_bool_var(f"groupAlpha_{student.rollNumber}_{group_id}") for group_id in range(no_of_groups)] for student in self.students]


class Group(BaseModel):
    groupId: int
    projectCode: Annotated[int,Field(ge=0,le=no_of_projects-1)]
    section: Annotated[int,Field(ge=0,le=no_of_sections-1)]
    students: List[Student] # list of roll numbers of students


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
    
    def departmentSum(self, department: Literal['AE','CE','CH','CL','CS','EC','EE','EN','EP','ES','ME','MM']):
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
        boolvar = model.new_bool_var(f'department_diversity_{id(self)}') #This is a boolean variable which will be true if group has
        for department in departments:
            model.add(self.departmentSum(department) <= 4).only_enforce_if(boolvar)
        return boolvar


def gauss(low,high,sigma): #randomly generates an integer from a truncated gaussian distribution
    mean = (low+high)/2
    return int(round(truncnorm.rvs((low-mean)/sigma, (high-mean)/sigma, loc=mean, scale=sigma)))
            

def generate_and_save_students_data(): #randomly generated CPI, preferences and saves it
    ##Last year's DE 250 dataset
    student_df = pd.read_csv('students_data_random_names.csv')
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
        list_of_students.append(Student(name=student['name'], gender =student['gender']  ,rollNumber=student['rollNumber'],cpi=cpis[i], department=student['department'], preferences=preferences[i]))

    df= pd.DataFrame([student.model_dump() for student in list_of_students])
    df.to_csv('students_data_with_preferences.csv',index=False) #In this data, preferences were generated randomly for each student
    
    

    

def absolute_value(x,model: cp_model.CpModel): #check the 100000 
    absolute = model.new_int_var(0, 500000, f"abs_{id(x)}")  # Assuming a max value of 10000 for the absolute value variable
    model.add(x<=absolute)
    model.add(x>=-1*absolute)
    return absolute
    


        
    


    

    
    

    

    









































# model = cp_model.CpModel()

# num_projects = 6
# student_count = 1325
# female_count = 261
# male_count = 1064

# def compute_values(male_count,female_count):
#     total_count = male_count+female_count
#     y = (6-(total_count%6))%6 # no of 5 membered groups
#     x = (male_count+female_count-5*y)/6 # no of 6 membered groups
#     x1 = y # groups with 1 female and 4 males
#     x2 = (5*female_count - male_count - y)/6 # 2 females 4 males
#     x3 = x-x2 # 1 female 5 males
#     return x1, x2, x3

# class Student:
#     def __init__(self,rollnum,name,department,cpi,gender,preferences:list,groups):
#         self.rollnum = rollnum
#         self.name = name
#         self.department = department
#         self.cpi = cpi
#         self.gender = gender # 0 if male, 1 if female (might add more later ;)
#         self.preferences = [preferences[g.type] for g in groups]
#         self.alpha = [model.new_bool_var(f"alpha_{self.rollnum}_{i}") for i in range(len(groups))]
#         self.beta = [model.new_bool_var(f"beta_{self.rollnum}_{i}") for i in range(num_projects)]
        
        
# class Project:
#     def __init__(self,id,type,male_count,female_count):
#         self.id = id # serial number
#         self.type = type
#         self.male_count = male_count
#         self.female_count = female_count
#         # self.average_cpi =   
    
#     def __str__(self):
#         return f"project type: {self.type}\ngroup id: {self.id}"     

# def generate_nodes(x1, x2, x3):
#     groups = []
#     id=0
#     for i in range(x1):
#         groups.append(Project(id,i%num_projects,4,1))
#         id+=1
#     for i in range(x2):
#         groups.append(Project(id,i%num_projects,4,2))
#         id+=1
#     for i in range(x3):
#         groups.append(Project(id,i%num_projects,5,1))
#         id+=1
#     return groups






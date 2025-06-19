from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, StringConstraints
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random
from utils import Student, allocated_student, Project, Group, Section, no_of_projects, no_of_sections, groupSize
from section_allocator import sectionAllocator
from project_allocator import projectAllocator
from group_allocator import groupAllocator
import json


class CourseAllocator:
    def __init__(self, students: List[Student]):
        self.students = students
        self.rollToIndex = {student.rollNumber: i for i, student in enumerate(students)} #check, not needed, already calculated this in utils.py
        self.groups = []  # List to store allocated groups

        #These below values must match the global variables values in utils.py
        self.numberOfSections = no_of_sections
        self.numberOfProjects = no_of_projects
        self.groupSize=groupSize

        # self.section_divider_model = cp_model.CpModel()
        # self.sectionAlphas = [[self.section_divider_model.new_bool_var(f"sectionAlpha_{student.rollNumber}_{section_id}") for section_id in range(self.numberOfSections)] for student in self.students]
    
    def allocate(self) -> List[Group]:
        sections = sectionAllocator(self.students,self.numberOfSections)
        projects = []
        for section in sections:
            projects.extend(projectAllocator(section, self.numberOfProjects))
        groups = []
        for project in projects:
            groups.extend(groupAllocator(project, self.groupSize))
        self.groups = groups
        self.projects = projects
        self.sections = sections
        return self.groups
    
    def save_allocation(self,filetype:Literal['csv','json']='json', filename:str="", dontsave=False):
        if not self.groups:
            raise ValueError("No groups allocated yet. Please run allocate() method first.")
        
        jsondata=[]
        csvdata=[]
        for group in self.groups:
            project_id = group.projectCode
            section_id = group.section
            group_id = group.groupId
            for student in group.students:
                jsondata.append(allocated_student(cpi=student.cpi,section=section_id+1,project=project_id+1,group=group_id+1 ,name=student.name,gender= student.gender, #+1 because zero indexing to one indexing conversion
                    department= student.department,
                    allocated_preference= student.preferences[project_id], preferences=student.preferences))
                csvdata.append({'name':student.name,'gender': student.gender,'department': student.department,'cpi': student.cpi,'section':section_id+1,'project':project_id+1,'group':group_id+1 , #+1 because zero indexing to one indexing conversion 
                        'allocated_preference': student.preferences[project_id], 'preferences':student.preferences})
        if(filetype=='json'):
            json_serialisable_data = [student_data.model_dump() for student_data in jsondata]
            if(dontsave==False):
                try:
                    with open(f"allocations_files/allocated_students_data_{filename}.json", "w") as f:
                        json.dump(json_serialisable_data, f, indent=2)
                    print("JSON file saved successfully")
                except Exception as e:
                    print("Error writing file:", e)
            return json.dumps(json_serialisable_data, indent=2).encode('utf-8')
        else:
            if(dontsave==False):
                try:
                    pd.DataFrame(csvdata).to_csv(f'allocations_files/allocated_students_data_{filename}.csv',index=False)
                    print("CSV file saved successfully")
                except Exception as e:
                    print("Error writing file:", e)
            return pd.DataFrame(csvdata).to_csv(index=False).encode('utf-8')
            

    

    def get_allocation_metrics(self):
        preference_scores_of_groups=[]
        project_cpi_diversity = [0] * self.numberOfProjects
        gender_diversity=0
        department_diversity=0
        for group in self.groups:
            gender_diversity_in_group = 0
            departments = set()
            preference_score=0
            project_id = group.projectCode
            for student in group.students:
                if student.gender=='female':
                    gender_diversity_in_group= 1
                departments.add(student.department)
                preference_score += student.preferences[project_id]
                project_cpi_diversity[project_id] += student.cpi
            preference_scores_of_groups.append(preference_score/len(group.students))
            gender_diversity+=gender_diversity_in_group
            if(len(departments) > 1):  
                department_diversity+=1

        print("From professor point of view, the following metrics are important:")
        department_diversity = (department_diversity / len(self.groups))*100
        print("Department Diversity: ",department_diversity, "%")

        project_cpi_diversity = [cpi /(len(self.students)//self.numberOfProjects)  for cpi in project_cpi_diversity]
        print("Project CPI standard deviation: ",np.std(project_cpi_diversity))
        print("Project CPI minimum: ",min(project_cpi_diversity))
        print("---------------------------------------------------------------")

        print("From student point of view, the following metrics are important:")
        preference_scores_of_groups = np.array(preference_scores_of_groups)
        print("Average preference score: ",np.mean(preference_scores_of_groups))
        print("Preference score standard deviation: ",np.std(preference_scores_of_groups))
        print("Preference score minimum: ",min(preference_scores_of_groups))
        gender_diversity = (gender_diversity / len(self.groups))*100
        print("Gender Diversity: ",gender_diversity, "%")
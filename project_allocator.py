from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, StringConstraints
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random
from utils import variableContainer, absolute_value
import config

def projectAllocator(section:config.Section, numberOfProjects:int) -> list[config.Project]:

        model = section._model #check, whether instantiation in Section class is ok or not, ask professor Dominic
        numberOfStudents = len(section.students)
        # Constraints for project allocation
        for student_alphas in section._projectAlphas:
            model.add(sum(student_alphas) == 1)
         
        transpose = [[row[i] for row in section._projectAlphas] for i in range(numberOfProjects)]
        projectContainers=[]
        no_of_females = sum(1 for student in section.students if student.gender=='female')

        for projectId, alphas in enumerate(transpose):
             projectContainers.append(variableContainer(alphas,projectId))
        
        for project in projectContainers: #this project is of type variableContainer, dont confuse it with 'Project' class
            model.add(project.numberOfStudents() >= int((numberOfStudents//numberOfProjects)/1.5)) #check
            model.add(project.numberOfStudents() <= int((numberOfStudents//numberOfProjects)*1.5))  #check, this restriction of only allowing +1 range might fail to have a mathematical solution 


        # projectsize_bools =[] #these represent whether project size is multiple of group_size or not
        # for projectId, project in enumerate(projectContainers):
        #     projectsize_bools.append(model.new_bool_var(f'groupsizemultiple_{projectId}'))
        #     projectsize = model.new_int_var(0,500,f'projectCardinality_{projectId}') #check limits, integer version of the boolean sum: project.numOfStudents() so as to use for modulo
        #     model.add(projectsize==project.numberOfStudents())
        #     projectsize_remainder = model.new_int_var(0,10,f'remainder_{projectId}')
        #     model.add_modulo_equality(projectsize_remainder,projectsize,config.group_size)
        #     model.add(projectsize_remainder==0).only_enforce_if(projectsize_bools[-1])


        # Objective function to maximize the number of students in their preferred projects
        #ToDo: Edit the objective function to include more things
        scaled_median_cpi = int(100*np.median([student.cpi for student in section.students])) #check
        abs_cpi = []
        
        project_size_differences=[] #difference between project size and mean project size
        for projectId, project in enumerate(projectContainers):
            project_size_differences.append(absolute_value(project.numberOfStudents() - numberOfStudents//numberOfProjects, model)) 
         
     
    

        for projectId,project in enumerate(projectContainers):
            model.add(int(1/config.min_female_proportion)*project.femaleSum()>= project.numberOfStudents()) #check, gender diversity
            abs_cpi.append(absolute_value(project.cpiSumScaled() - project.numberOfStudents()*scaled_median_cpi,model))

        gender_diversity_bools = []  # This will be used to check if

        for projectId,project in enumerate(projectContainers):

             gender_diversity_bools.append(absolute_value(project.femaleSum()-no_of_females//numberOfProjects,model))

        department_diversity_bools = []
        for projectId,project in enumerate(projectContainers):

             department_diversity_bools.append(project.departmentDiversity(4,3,project.numberOfStudents(),model))
        
        model.maximize(100*sum(project.preferencesSum() for project in projectContainers)
                        - sum(cpi_diff_from_median for cpi_diff_from_median in abs_cpi) - sum(difference for difference in project_size_differences) -sum(gender_diversity for gender_diversity in gender_diversity_bools) + 10*sum(department_diversity_bools))  # check, add weightages for terms

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2
        status = solver.solve(model)

        if status != cp_model.OPTIMAL:
            if(status!=cp_model.FEASIBLE):
                raise RuntimeError("No solution found for project allocation. Constraints are impossible to satisfy")
            else:
                print("Project solver timedout, giving the best solution found")
                female_count = 0
                for student in section.students:
                    if(student.gender=='female'):
                        female_count+=1
                print(f"Section: {section.section}, Number of students: {numberOfStudents}, Female count: {female_count}, Number of projects: {numberOfProjects}")
        projects = []

        for projectContainer in projectContainers:
            projects.append(config.Project(projectCode=projectContainer.id, section=section.section, students=projectContainer.getAllocation(solver)))
        for project in projects:
            project.describe()
        return projects
from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, StringConstraints
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random
from utils import variableContainer
import config

def groupAllocator(project: config.Project, groupSize: int) -> List[config.Group]:
        model = project._model
        numberOfStudents = len(project.students)
        numberOfGroups = numberOfStudents// groupSize
        
        # Constraints for group allocation
        for student_alphas in project._groupAlphas:
            model.add(sum(student_alphas) == 1)

        transpose = [[row[i] for row in project._groupAlphas] for i in range(numberOfGroups)]
        groupContainers=[]
        for groupId, alphas in enumerate(transpose):
             groupContainers.append(variableContainer(alphas,groupId))

        # print(groupSize)
        for group in groupContainers: #this group is of type variableContainer, dont confuse it with 'Group' class
            model.add(group.numberOfStudents() >= groupSize) #check
           
        if(numberOfStudents % groupSize <=numberOfGroups):  #We are doing this to resolve an issue, which is: If suppose total 15 students in project and you want to divide them into groups, then it is not possible to divide them using only groups of size 6,7. We need atleast one group of size 8
            for group in groupContainers:
                model.add(group.numberOfStudents() <= groupSize+1)
        else:
            for group in groupContainers: 
                model.add(group.numberOfStudents() <= groupSize+3)  #check, Currently this simple trick is enough for solving, if still this doesnt solve the issue, then do something in future. 
            

        scaled_median_cpi = int(100*np.median([student.cpi for student in project.students])) #check
        abs_cpi = []
        gender_diversity_bools = []  # This will be used to check if

        for groupId,group in enumerate(groupContainers):
             gender_diversity_bools.append(model.new_bool_var(f'group_gender_diversity_{groupId}')) #This is a boolean variable which will be true if group has gender diversity
             model.add(group.femaleSum() >= 1).only_enforce_if(gender_diversity_bools[-1])

             abs_cpi.append(model.new_int_var(0,10000,f"abs_cpi_{groupId}")) #check 10000 
             model.add(group.cpiSumScaled() - group.numberOfStudents()*scaled_median_cpi <= abs_cpi[groupId])
             model.add(group.cpiSumScaled() - group.numberOfStudents()*scaled_median_cpi >= -1*abs_cpi[groupId])
        
        groupsize_booleans=[]
        for groupId,group in enumerate(groupContainers):
            groupsize_booleans.append(model.new_bool_var(f'groupsize_isperfect_{groupId}'))
            model.add(group.numberOfStudents()==groupSize).only_enforce_if(groupsize_booleans[-1])

        model.maximize(10*sum(groupsize_booleans) + sum(gender_diversity_bools) - sum(cpi for cpi in abs_cpi)) #We also want to maximise the number of groups which have size==groupSize
        #+sum(groupContainer.departmentDiversity(model) for groupContainer in groupContainers) check, not including department diversity

        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 1
        status = solver.solve(model)

        if status != cp_model.OPTIMAL:
            if(status!=cp_model.FEASIBLE):
                raise RuntimeError("No solution found for group allocation. Constraints are impossible to satisfy")
            else:
                print(" Group solver timedout, giving the best solution found")
                female_count = 0
                for student in project.students:
                    if(student.gender=='female'):
                        female_count+=1
                print(f"Total number of students: {numberOfStudents}, Female count: {female_count}, Number of groups: {numberOfGroups}")


        groups = []
        for groupContainer in groupContainers:
            groups.append(config.Group(groupId=groupContainer.id, projectCode=project.projectCode, section=project.section, students=groupContainer.getAllocation(solver)))

        return groups

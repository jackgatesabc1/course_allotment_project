from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, StringConstraints
from typing import Literal, List, Annotated
from typing_extensions import Annotated
import random
from utils import Student, Section, variableContainer, absolute_value, student_count_per_department, available_slots




def sectionAllocator(students: List[Student],numberOfSections:int) -> List[Section]: # Divides students into sections
    model = cp_model.CpModel()
    sectionAlphas = [[model.new_bool_var(f"sectionAlpha_{student.rollNumber}_{section_id}") for section_id in range(numberOfSections)] for student in students]

    for i,student_alphas in enumerate(sectionAlphas):
        model.add(sum(student_alphas) == 1)
        for slot in range(numberOfSections):
            if(slot not in available_slots[students[i].department]):
                model.add(student_alphas[slot] == 0)  # If the slot is not available for the student's department, set the variable to 0


    
    transpose = [[row[i] for row in sectionAlphas] for i in range(numberOfSections)]
    sectionContainers=[]
    for sectionId, alphas in enumerate(transpose):
        sectionContainers.append(variableContainer(alphas,sectionId))

    #Constraints and objectives
    for section_id, section in enumerate(sectionContainers):
        model.add(section.numberOfStudents() >= len(students)//numberOfSections-20)  #Check
        model.add(section.numberOfStudents() <= len(students)//numberOfSections+20)  


    scaled_median_cpi = int(100*np.median([student.cpi for student in students])) #check
    abs_cpi = []
    for sectionId,section in enumerate(sectionContainers):
        model.add(6*section.femaleSum()>= section.numberOfStudents()) #check
        abs_cpi.append(absolute_value(section.cpiSumScaled() - section.numberOfStudents()*scaled_median_cpi,model))


   ## ------------------ Multiple of 6 constraint #Optional, check later whether this is needed or not ---------------------##
    # sectionsize_bools = []  # These represent whether section size is a multiple of 6 or not
    # for sectionId, section in enumerate(sectionContainers):
    #     sectionsize_bools.append(model.new_bool_var(f'6multiple_{sectionId}'))
    #     sectionsize = model.new_int_var(0, 500, f'sectionCardinality_{sectionId}')  # Integer version of the boolean sum: section.numOfStudents() so as to use for modulo
    #     model.add(sectionsize == section.numberOfStudents())
    #     sectionsize_remainder = model.new_int_var(0, 10, f'remainder_{sectionId}')
    #     model.add_modulo_equality(sectionsize_remainder, sectionsize, 6)
    #     model.add(sectionsize_remainder == 0).only_enforce_if(sectionsize_bools[-1])


    #Constraint of equal splitting of departments into its available section 
    students_per_slot_differences = []
    for department, slots in available_slots.items():
        no_of_slots= len(slots)
        total_students = student_count_per_department[department]
        for slot in slots: 
            students_per_slot_differences.append(absolute_value(no_of_slots*sectionContainers[slot].departmentSum(department)-total_students,model))

    
    model.maximize(-sum(cpi_diff_from_median for cpi_diff_from_median in abs_cpi) -sum(students_per_slot_differences) )  # Objective function to maximize the number of sections with size multiple of 6

    

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.solve(model)

    if status != cp_model.OPTIMAL:
        if(status!=cp_model.FEASIBLE):
            raise RuntimeError("No solution found for section allocation. Constraints are impossible to satisfy")
        else:
            print(" Section solver timedout, giving the best solution found")

    sections = []
    for sectionContainer in sectionContainers:
        sections.append(Section(section=sectionContainer.id,students=sectionContainer.getAllocation(solver)))
    return sections



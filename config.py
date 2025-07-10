from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, constr, conint, confloat, conlist, StringConstraints, PrivateAttr
from typing import Literal, List, Annotated, Type
from typing_extensions import Annotated
import random
import ast
from collections import defaultdict
from scipy.stats import truncnorm
import os


no_of_projects = 6
no_of_sections = 8
group_size = 6

min_female_proportion = 1/6 #This is the minimum proportion of female students among all students. Such as IITB has minimum 1/6 female students out of total students

Student: Type[BaseModel] = None
AllocatedStudent: Type[BaseModel] = None
Section: Type[BaseModel] = None
Project: Type[BaseModel] = None
Group: Type[BaseModel] = None
available_slots = None
max_size_for_dept_diversity = None
department_literal = None
project_names = None
section_names = None


def initialize_models(___no_of_projects: int, ___no_of_sections: int, ___group_size: int, ___available_slots, ___list_of_departments, ___max_size_for_dept_diversity: int = 4):
    global Student, AllocatedStudent, Section, Project, Group, available_slots, max_size_for_dept_diversity, department_literal, no_of_sections, no_of_projects, group_size

    no_of_projects = ___no_of_projects
    no_of_sections = ___no_of_sections
    group_size = ___group_size

    department_literal = Literal.__getitem__(tuple(___list_of_departments))
    available_slots = ___available_slots
    max_size_for_dept_diversity = ___max_size_for_dept_diversity

    class StudentModel(BaseModel):
        name: str
        gender: Literal['male', 'female']
        rollNumber: Annotated[str, StringConstraints(pattern=r"2\d[Bb]\d{4}")]
        cpi: Annotated[float, Field(ge=0.00, le=10.00)]
        department: department_literal
        preferences: Annotated[
            List[Annotated[int, Field(ge=0, le=100)]],
            Field(min_length=no_of_projects, max_length=no_of_projects)
        ]

        def __init__(self, **data):
            super().__init__(**data)

    class AllocatedStudentModel(BaseModel):
        section: Annotated[int, Field(ge=1, le=no_of_sections)]
        project: Annotated[int, Field(ge=1, le=no_of_projects)]
        group: Annotated[int, Field(ge=1)]
        name: str
        cpi: Annotated[float, Field(ge=0.00, le=10.00)]
        gender: Literal['male', 'female']
        department: department_literal
        allocated_preference: Annotated[int, Field(ge=0, le=100)]
        preferences: Annotated[
            List[Annotated[int, Field(ge=0, le=100)]],
            Field(min_length=no_of_projects, max_length=no_of_projects)
        ]

    class SectionModel(BaseModel):
        section: Annotated[int, Field(ge=0, le=no_of_sections - 1)]
        students: List[StudentModel]
        _model: cp_model.CpModel = PrivateAttr()
        _projectAlphas: list[list[cp_model.IntVar]] = PrivateAttr(default_factory=list)

        def __init__(self, **data):
            super().__init__(**data)
            self._model = cp_model.CpModel()
            self._projectAlphas = [
                [
                    self._model.new_bool_var(f"projectAlpha_{student.rollNumber}_{project_id}")
                    for project_id in range(no_of_projects)
                ]
                for student in self.students
            ]
        def describe(self):
            print(f"Section {self.section} has {len(self.students)} students.")
            male_students = sum(1 for student in self.students if student.gender=='male')
            female_students = sum(1 for student in self.students if student.gender=='female')
            print(f"Section {self.section} has {male_students} males and {female_students} females")
            student_count_per_department_in_section = defaultdict(int)
            for student in self.students:
                student_count_per_department_in_section[student.department] += 1
            print(student_count_per_department_in_section)
            # for department, count in student_count_per_department_in_section.items():
            #     print(f"Department {department} has {count} students in section {self.section}.")




    class ProjectModel(BaseModel):
        projectCode: Annotated[int, Field(ge=0, le=no_of_projects - 1)]
        section: Annotated[int, Field(ge=0, le=no_of_sections - 1)]
        students: List[StudentModel]
        _model: cp_model.CpModel = PrivateAttr()
        _groupAlphas: list[list[cp_model.IntVar]] = PrivateAttr(default_factory=list)

        def __init__(self, **data):
            super().__init__(**data)
            no_of_groups = max(1, len(self.students) // group_size)
            self._model = cp_model.CpModel()
            self._groupAlphas = [
                [
                    self._model.new_bool_var(f"groupAlpha_{student.rollNumber}_{group_id}")
                    for group_id in range(no_of_groups)
                ]
                for student in self.students
            ]
        def describe(self):
            print(f"Project {self.projectCode} in section {self.section} has {len(self.students)} students.")
            male_students = sum(1 for student in self.students if student.gender=='male')
            female_students = sum(1 for student in self.students if student.gender=='female')
            print(f"Project {self.projectCode} in Section {self.section} has {male_students} males and {female_students} females")
            student_count_per_department_in_project = defaultdict(int)
            for student in self.students:
                student_count_per_department_in_project[student.department] += 1
            print(student_count_per_department_in_project)


    class GroupModel(BaseModel):
        groupId: int
        projectCode: Annotated[int, Field(ge=0, le=no_of_projects - 1)]
        section: Annotated[int, Field(ge=0, le=no_of_sections - 1)]
        students: List[StudentModel]  # list of Student instances

    Student = StudentModel
    AllocatedStudent = AllocatedStudentModel
    Section = SectionModel
    Project = ProjectModel
    Group = GroupModel
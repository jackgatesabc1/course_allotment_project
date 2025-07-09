from course_allocator import CourseAllocator
from utils import generate_and_save_students_data
import pandas as pd
import ast
import utils
import config

if __name__ == "__main__":
    # generate_and_save_students_data('csv')        #Generates new data and stores in sample_files folder

    df=pd.read_csv('sample_files/students_data_with_preferences.csv')
    if(not isinstance(df['preferences'].iloc[0],list)):
        df['preferences'] = df['preferences'].apply(ast.literal_eval)
    list_of_students = [config.Student(**row) for row in df.to_dict(orient='records')]
    utils.list_of_students = list_of_students
    for student in list_of_students:
        utils.roll_to_student[student.rollNumber] = student #check whether python maps allow this
        utils.departments.add(student.department) #to store all departments, so that we can use it later in utils.py and group_allocator.py
        utils.student_count_per_department[student.department] += 1 #to store the number of students in each department, so that we can use it later in section_allocator.py
    de250= CourseAllocator(list_of_students) #see utils.py for list_of_students
    de250.allocate()
    de250.save_allocation('json') #You can mention type of file to save as here. (Either 'csv' or 'json')
    de250.get_allocation_metrics()
   
    
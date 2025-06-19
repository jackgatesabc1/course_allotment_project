from course_allocator import CourseAllocator
from utils import Student, generate_and_save_students_data
import pandas as pd
import ast

if __name__ == "__main__":
    # generate_and_save_students_data()  #If this is not called, then each time same dataset will be used
    df=pd.read_csv('students_data_with_preferences.csv')
    df['preferences'] = df['preferences'].apply(ast.literal_eval)
    list_of_students = [Student(**row) for row in df.to_dict(orient='records')]
    de250= CourseAllocator(list_of_students) #see utils.py for list_of_students
    de250.allocate()
    de250.save_allocation('json') #You can mention type of file to save as here. (Either 'csv' or 'json')
    de250.get_allocation_metrics()
   
    
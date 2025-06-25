# # # # import pandas as pd
# # # # from collections import defaultdict
# # # # # student_df = pd.read_csv('students_data_2024.csv')
# # # # # # sections_department_wise = defaultdict(lambda: defaultdict(int))
# # # # # # for index, row in student_df.iterrows():
# # # # # #     if(row['name'].split(' ')[0]=='Ms.'):
# # # # # #         sections_department_wise[row['department']]['female']+=1
# # # # # #     else:
# # # # # #         sections_department_wise[row['department']]['male']+=1

# # # # # # #print female ratio for each department
# # # # # # for department in sections_department_wise.keys():
# # # # # #     total_students = sections_department_wise[department]['male']+ sections_department_wise[department]['female']
# # # # # #     female_students = sections_department_wise[department]['female']
# # # # # #     print(f"Department: {department} has female ratio:{female_students/total_students:.2%}")

# # # # # count_department_wise = defaultdict(int)
# # # # # for index, row in student_df.iterrows():
# # # # #     count_department_wise[row['department']] += 1

# # # # # # Print the number of students in each department
# # # # # print(count_department_wise)

# # # # # #print the sections for each department
# # # # # # for department, sections in sections_department_wise.items():
# # # # # #     print(f"Department: {department}, Sections: {sections}")
    
# # # # # # # Print the number of unique sections for each department
# # # # # # for department, sections in sections_department_wise.items():
# # # # # #     print(f"Department: {department}, Number of Unique Sections: {len(sections)}")

# # # # # # print(sections_department_wise)


# # # # generated_data = pd.read_csv('indian_full_names_1500.csv', names=['name'])
# # # # generated_data['name'] = generated_data['name'].sample(frac=1).reset_index(drop=True)
# # # # df = pd.read_csv('private_data/students_data_2024.csv')
# # # # # olddf = pd.read_csv('students_data_2024.csv')
# # # # df['gender'] = df['name'].apply(lambda x: 'female' if x.split(" ")[0]=='Ms.' else 'male')
# # # # # olddf['gender'] = olddf['name'].apply(lambda x: 'female' if x.split(" ")[0]=='Ms.' else 'male')
# # # # df['rollNumber'] = df['rollNumber'].sample(frac=1).reset_index(drop=True)
# # # # df['name'] = generated_data['name']
# # # # df.to_csv('students_data_random_names.csv', index=False)
# # # # # olddf.to_csv('students_data_2024.csv', index=False)

# # # import numpy as np
# # # from scipy.stats import truncnorm

# # # cpi_low=6
# # # cpi_high=10
# # # cpi_mean=8
# # # std = 2
# # # a, b = (cpi_low - cpi_mean) / std, (cpi_high - cpi_mean) / std  # if std=1, mean=8
# # # trunc_normal = truncnorm(a, b, loc=cpi_mean, scale=std)
# # # samples = trunc_normal.rvs(51).tolist() # generate 1000 samples
# # # samples = [round(sample,2) for sample in samples]
# # # print(type(samples))
# # # print(samples)



# # import json
# # import pandas as pd
# # import numpy as np
# # import ast

# # df = pd.read_csv('students_data_with_preferences.csv')
# # if(not isinstance(df['preferences'].iloc[0]), list):
# #     df['preferences'] = df['preferences'].apply(ast.literal_eval)
# # df.to_json('students_data_with_preferences.json', indent=2, orient='records')
# list_s=[1]
# for s in list_s:
#     print(s)


import streamlit as st


col1, col2, col3 = st.columns(3)

col1.metric("Temperature", "70 °F", "-1 °F", help="Measured at 9 AM local time.")
col2.metric("Wind", "9 mph", "1 mph", help="Average over past hour.")
col3.metric("Humidity", "86%", "4%", help="Current relative humidity.")





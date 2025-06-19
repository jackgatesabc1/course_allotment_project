import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict
from utils import Group, Student, Project, allocated_student, generate_and_save_students_data
from typing import List, Literal
import os
import copy
import json
import ast
import matplotlib.pyplot as plt
from course_allocator import CourseAllocator
import utils

#These must be hardcoded
project_names = {1:'theme 1: Food wastage mitigation', 2:'theme 2: Outdoor spaces improvement', 3:'theme 3: Improving lifes of labourers', 4:'theme 4: Solution for easy cleaning', 5:'theme 5: Automating watering of plants', 6:'theme 6: Wheelchair design improvement'}
section_names = {1:'S1: Mon 2PM-5PM', 3:'S3: Tue 2PM-5PM', 5:'S5: Thu 2PM-5PM', 7:'S7: Fri 2PM-5PM', 2:'S2: Mon 5:30PM-8:30PM', 4:'S4: Tue 5:30PM-8:30PM', 6:'S6: Thu 5:30PM-8:30PM', 8:'S8: Fri 5:30PM-8:30PM'}

avg_cpis = []



def display_readme(choicee: Literal['allocator','viewer','readme']):
    if(choicee=='allocator'):
        with st.expander("View Format Guidelines"):
            st.markdown("""
            **Expected Format for JSON:**
            ```json
            [
            {
                "name": "Rekha Sengupta",
                "gender": "female",
                "rollNumber": "23B3909",
                "cpi": 7.73,
                "department": "CL",
                "preferences": [81, 13, 60, 8, 12, 73]
            },
            ...
            ]
            ```

            **Expected Format for CSV:**
            ```
            name,gender,rollNumber,cpi,department,preferences
            Rekha Sengupta,female,23B3909,7.73,CL,"[81, 13, 60, 8, 12, 73]"
            ...
            ```

            - Ensure all fields are present and are in the given format
            - Only `.csv` and `.json` files are supported
            """)
            st.write("Download sample files here:")
            with open("sample_files/students_data_with_preferences.csv", "r", encoding="utf-8") as f:
                csv_data = f.read()

            st.download_button(
                label="📄 Students data (sample) as csv file",
                data=csv_data,
                file_name="students_data_with_preferences.csv",
                mime="text/csv"
            )
            with open("sample_files/students_data_with_preferences.json", "r", encoding="utf-8") as f:
                json_data = f.read()

            st.download_button(
                label="📄 Students data (sample) as json file",
                data=json_data,
                file_name="students_data_with_preferences.json",
                mime="application/json"
            )
    elif(choicee=='viewer'):
        with st.expander("View Format Guidelines "):
            st.markdown("""
            **Expected Format for JSON:**
            ```json
            [
            {
                "name": "Rekha Sengupta",
                "gender": "female",
                "department": "CL",
                "cpi": 7.73,
                "section": 1,
                "project": 1,
                "group": 1,
                "allocated_preference": 81,
                "preferences": [81, 13, 60, 8, 12, 73]
            },
            ...
            ]
            ```

            **Expected Format for CSV:**
            ```
            name,gender,department,cpi,section,project,group,allocated_preference,preferences
            Aditya Reddy,male,CL,7.09,1,1,1,99,"[99, 11, 45, 6, 14, 2]"
            ...
            ```

            - Ensure all fields are present and are in the given format
            - Only `.csv` and `.json` files are supported
            """)
            st.write("Download sample files here:")
            with open("sample_files/allocated_students_data.csv", "r", encoding="utf-8") as f:
                csv_data = f.read()

            st.download_button(
                label="📄 Project allocations data (sample) as csv file",
                data=csv_data,
                file_name="allocated_students_data.csv",
                mime="text/csv"
            )
            with open("sample_files/allocated_students_data.json", "r", encoding="utf-8") as f:
                json_data = f.read()

            st.download_button(
                label="📄 Project allocations data (sample) as json file",
                data=json_data,
                file_name="allocated_students_data.json",
                mime="application/json"
            )
    else:
        with open("README.md", "r", encoding="utf-8") as file:
            readme_content = file.read()
            with st.expander("README"):
                st.markdown(readme_content)
        
            


def display_allocation(students_data: List[allocated_student]):
    st.title("Student Allocations by Section, Project, and Group")

    # Organize students by section → project → group
    section_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    student_lookup = copy.deepcopy(students_data)

    for student in students_data:
        section_map[student.section][student.project][student.group].append(student)

    # -------------------- Search Box --------------------
    search_name = st.text_input("🔍 Search student by name (partial allowed)").strip().lower()

    if search_name:
        matching_students = [s for s in student_lookup if search_name in s.name.lower()]

        if matching_students:
            options = [s.name for s in matching_students]
            selected_name = st.selectbox("Select a matching student", options)

            selected = next(s for s in matching_students if s.name == selected_name)
            st.success(f"📌 {selected_name} is in Section {section_names[selected.section]}, "
                       f"Project {project_names[selected.project]}, Group {selected.group}")
        else:
            st.warning("No matching student found.")

    # -------------------- Full Allocation Display --------------------
    for section in sorted(section_map):
        with st.expander(f"📘 Section {section_names[section]}", expanded=False):
            project_tabs = st.tabs([f"📁 Project {project_names[selected_project]}" for selected_project in sorted(section_map[section].keys())])
            for i,selected_project in enumerate(sorted(section_map[section].keys())):
                with project_tabs[i]:

            # for selected_project in sorted(section_map[section].keys()):
            #     with st.expander(f"📁 Project {project_names[selected_project]}", expanded=False):

            # selected_project = st.selectbox(
            #     f"Select a project in Section {section_names[section]}",
            #     project_list,
            #     key=f"select_project_section_{section}"
            # )
                    avg_project_cpi = np.mean([s.cpi for group_students in section_map[section][selected_project].values() for s in group_students ])
                    avg_preference = np.mean([s.allocated_preference for group_students in section_map[section][selected_project].values() for s in group_students])
            
                    st.markdown(f"### 📁 Project {project_names[selected_project]}")
                    st.markdown(f"""
                        <div style="
                            border-radius: 10px;
                            padding: 16px;
                            background-color: #f9f9f9;
                            color: #111111;
                            border: 1px solid #ccc;
                            box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.05);
                            margin-bottom: 16px;
                        ">
                            <h4 style="margin-top: 0; font-size: 18px;">📌 <strong>Project Overview</strong></h4>
                            <p style="margin: 6px 0;">📈 <strong>Average CPI:</strong> {avg_project_cpi:.2f}</p>
                            <p style="margin: 6px 0;">🎯 <strong>Average Preference Score:</strong> {avg_preference:.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    for group_id in sorted(section_map[section][selected_project].keys()):
                        st.markdown(f"**👥 Group {group_id}**")

                        group_students = section_map[section][selected_project][group_id]
                        avg_group_cpi = np.mean([s.cpi for s in group_students])
                        
                        
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; 📈 *Average CPI:* `{avg_group_cpi:.2f}`")

                        # df = pd.DataFrame([{
                        #     "Name": s.name,
                        #     "Gender": s.gender,
                        #     "Department": s.department,
                        #     "Allocated preference": s.allocated_preference
                        # } for s in group_students])

                        # st.table(df)

                        rows = []
                        for s in group_students:    
                            highlighted = ", ".join(
                            f"<mark>{v}</mark>" if i==selected_project-1 else str(v)
                                for i,v in enumerate(s.preferences)
                            )
                            rows.append({
                                "Name": s.name,
                                "Gender": s.gender,
                                "Department": s.department,
                                "CPI:":s.cpi,
                                "Allocated preference": highlighted
                            })

                        # Convert to DataFrame
                        df = pd.DataFrame(rows)

                        # Render as HTML table manually
                        html = df.to_html(escape=False, index=False)
                        st.markdown(html, unsafe_allow_html=True)




###### Stats:

def display_allocation_stats(students_data: List[allocated_student]):
    st.markdown("## 📊 Allocation Statistics")

    # Organize data by group ID
    
    section_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for student in students_data:
        section_map[student.section][student.project][student.group].append(student)
    min_avg_group_cpi = float('inf')
    max_avg_group_cpi = float('-inf')

    preference_scores_of_groups = []
    gender_diversity_count = 0
    department_diversity_count = 0
    total_groups = 0

    for projects in section_map.values():
        for groups in projects.values():
            for group_students in groups.values():
                total_groups += 1
                departments = set()
                preference_sum = 0
                female_present = False
                group_cpis = []
                for student in group_students:
                    departments.add(student.department)
                    preference_sum += student.allocated_preference
                    group_cpis.append(student.cpi)
                    if student.gender.lower() == 'female':
                        female_present = True

                avg_preference = preference_sum / len(group_students)
                avg_group_cpi = np.mean(group_cpis)
                avg_cpis.append(avg_group_cpi)
                preference_scores_of_groups.append(avg_preference)
                min_avg_group_cpi = min(min_avg_group_cpi, avg_group_cpi)
                max_avg_group_cpi = max(max_avg_group_cpi, avg_group_cpi)

                if female_present:
                    gender_diversity_count += 1
                if len(departments) > 1:
                    department_diversity_count += 1

    dept_diversity = (department_diversity_count / total_groups) * 100 if total_groups > 0 else 0
    gender_diversity = (gender_diversity_count / total_groups) * 100 if total_groups > 0 else 0

    preference_scores_of_groups = np.array(preference_scores_of_groups)
    pref_mean = np.mean(preference_scores_of_groups) if preference_scores_of_groups.size > 0 else 0
    pref_std = np.std(preference_scores_of_groups) if preference_scores_of_groups.size > 0 else 0
    pref_min = np.min(preference_scores_of_groups) if preference_scores_of_groups.size > 0 else 0

    st.markdown(f"""
        <div style="
            border-radius: 12px;
            padding: 20px;
            background-color: #ffffff;
            color: #111111;
            border: 1px solid #ddd;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        ">
            <h3 style="margin-top: 0; font-size: 22px;">📊 <strong>Allocation Summary</strong></h3>
            <ul style="line-height: 1.8; font-size: 16px; margin-left: -20px;">
                <li>🧑‍🎓 <strong>Department Diversity:</strong> {dept_diversity:.2f}%</li>
                <li>👩‍🔬 <strong>Gender Diversity:</strong> {gender_diversity:.2f}%</li>
                <li>🎯 <strong>Average Preference Score:</strong> {pref_mean:.2f}</li>
                <li>📉 <strong>Std. Deviation of Preference:</strong> {pref_std:.2f}</li>
                <li>⛔ <strong>Minimum Preference Score:</strong> {pref_min:.2f}</li>
                <li>📈 <strong>Minimum Group Avg. CPI:</strong> {min_avg_group_cpi:.2f}</li>
                <li>📈 <strong>Maximum Group Avg. CPI:</strong> {max_avg_group_cpi:.2f}</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    

def plot_group_cpis():
    fig, ax = plt.subplots(figsize=(4, 2))  # smaller figure
    bins = np.arange(6.0, 10.1, 0.2)

    ax.hist(avg_cpis, bins=bins, edgecolor='black', color='mediumseagreen')
    ax.set_title("📊 Group CPI Distribution", fontsize=10)
    ax.set_xlabel("CPI Range", fontsize=9)
    ax.set_ylabel("No. of Groups", fontsize=9)
    ax.tick_params(axis='both', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.4)

    col1, col2, col3 = st.columns([1, 2, 1])  # narrow center column
    with col2:
        st.pyplot(fig, clear_figure=True)

def toggle_histogram():
    st.session_state.show_cpi_histogram = not st.session_state.show_cpi_histogram



if __name__ == "__main__":
    st.set_page_config(page_title="Student Allocation Viewer", layout="wide")
    display_readme('readme')

    st.title("DE 250 Student Project Allocation")
    choice = st.radio("Choose:", 
                      ["Run the allocator on students data and download the allocations","View results of an allocation"])

    if choice == "Run the allocator on students data and download the allocations":
        # st.subheader("⚙️ Running Allocator...")
        display_readme('allocator')
        uploaded_file = st.file_uploader("Upload a JSON or CSV file containing student data with preferences (ensure it has the correct format): Please refer to format guidelines for more info", type=["json","csv"])
        list_of_students=[]
        if uploaded_file is not None:
            try:
                uploaded_file_name = uploaded_file.name.lower()
                if uploaded_file_name.endswith(".json"):
                    uploaded_file_data = json.load(uploaded_file)
                    for s in uploaded_file_data:
                        if(not isinstance(s['preferences'],list)):
                            s['preferences']= ast.literal_eval(s['preferences'])
                        list_of_students.append(Student.model_validate(s))
                    
                elif uploaded_file_name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                    uploaded_file_data = df.to_dict(orient='records')
                    for s in uploaded_file_data:
                        if(not isinstance(s['preferences'],list)):
                            s['preferences']= ast.literal_eval(s['preferences'])
                        list_of_students.append(Student.model_validate(s))
                else:
                    st.error("Unsupported file format. Please upload a .csv or .json file")

                
                utils.list_of_students = list_of_students
                for student in list_of_students:
                    utils.roll_to_student[student.rollNumber] = student #check whether python maps allow this
                    utils.departments.add(student.department) #to store all departments, so that we can use it later in utils.py and group_allocator.py
                    utils.student_count_per_department[student.department] += 1 #to store the number of students in each department, so that we can use it later in section_allocator.py

                de250= CourseAllocator(list_of_students) #see utils.py for list_of_students
                de250.allocate()

                allocated_students_data_csv = de250.save_allocation('csv',dontsave=True) 
                allocated_students_data_json = de250.save_allocation('json', dontsave=True)
                st.download_button(
                    label="Download allocations as CSV",
                    data=allocated_students_data_csv,
                    file_name='allocated_students_data.csv',
                    mime='text/csv'
                )
                st.download_button(
                    label="Download allocations as JSON",
                    data=allocated_students_data_json,
                    file_name='allocated_students_data.json',
                    mime='application/json'
                )
            
            except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.info("Please upload a JSON or CSV file to proceed.")


    else:
        display_readme('viewer')
        uploaded_file = st.file_uploader("Upload a JSON or CSV file containing allocated students data (ensure it has the correct format): Please refer to format guidelines for more info", type=["json","csv"])

        if uploaded_file is not None:
            try:
                uploaded_file_name = uploaded_file.name.lower()
                
                if uploaded_file_name.endswith(".json"):
                    uploaded_file_data = json.load(uploaded_file)
                    students_data=[]
                    for s in uploaded_file_data:
                        if(not isinstance(s['preferences'],list)):
                            s['preferences']= ast.literal_eval(s['preferences'])
                        students_data.append(allocated_student.model_validate(s))
                    # students_data = [allocated_student.model_validate(s) for s in uploaded_file_data]                   
                elif uploaded_file_name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                    uploaded_file_data = df.to_dict(orient='records')
                    students_data=[]
                    for s in uploaded_file_data:
                        if(not isinstance(s['preferences'],list)):
                            s['preferences']= ast.literal_eval(s['preferences'])
                        students_data.append(allocated_student.model_validate(s))
                    # students_data = [allocated_student.model_validate(s) for s in uploaded_file_data]
                else:
                    st.error("Unsupported file format. Please upload a .csv or .json file")
                display_allocation_stats(students_data)
                display_allocation(students_data)
                if "show_cpi_histogram" not in st.session_state:
                        st.session_state.show_cpi_histogram = False
                # Button that toggles the histogram visibility
                st.button("Group-CPI Distribution", on_click=toggle_histogram)
                # Show plot only if toggle state is True
                if st.session_state.show_cpi_histogram:
                    plot_group_cpis()
        
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.info("Please upload a JSON or CSV file to proceed.")




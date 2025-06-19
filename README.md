Instructions to use: 
See the Format Guidelines below for file formats. We have also given sample data in the format guidelines that you can use to test the Project Allocator. First choose the "Run the allocator" option and upload a file with correct format. Then it processes and outputs the allocations file. You can download any one of csv or json. Next select the option "View results of an allocation" in the website, and upload the allocations that you downloaded. It will then display the allocations and statistics.

Quick glossary:
1) Section: Initial division of total batch of students into 8 parts called as sections (S1 to S8). Each section is associated with a particular time slot (Eg: S1 is Monday 2PM-5PM)
2) Department: The field of study (Example: Computer Science, Chemical Engineering)
3) Project: The different themes (for example in 2024 there were 6 themes, Food wastage mitigation, Outdoor spaces, Wheelchair design, etc..)
4) Group: The team of 6 or 7 members who all belong to same section and have same project(theme)
5) CPI: The GPA or overall performance of the student(range is 0 to 10)
6) Preferences: An integer value between 0 to 100 given by each student for each project(theme) that represents how much he likes that theme


There are students of different departments(such as Computer Science, Chemical Engineering, etc..) who are taking this course. 

There are eight "Sections" (slots). Each section corresponds to a specific time slot of the week.
Eg: Section-1 is Monday afternoon, Section-2 is Monday evening

There are 6 different project themes available (Eg: Solution for food wastage, Ideas for outdoor spaces, etc..). Each student will provide us with his preferences of the projects(he will assign an integer between 0 to 100 for each project indicating his affection for that project)

Now, we need to assign each student to a particular section(based on his available time slots) and in that section, assign him a particular project theme.

We need to assign students to projects by keeping in mind two things:
1) Preferences of students
2) Diversity: Each project should get approximately equal distribution of grades of students (i.e no project should have only students with low grades), and also try to have an equal distribution of students of a department among the projects, so that each project has students of diverse departments. Gender diversity as well should be taken care of.

Now, we need to form groups(of around size 6) of students who have the same project theme and section. The students will now work together as a group to finish their project. This group must be diverse. What exactly do we mean by diverse?
1) No group should have students of only low grades
2) Each group should have students of multiple departments
3) Gender diversity(try to maximise the number of groups which have both the genders)



Extra: 

-> If you want to use different dataset, then refer to the files main.py and generate_and_save_students_data() function in utils.py

-> sample_files folder contains generated data and some other data

-> To run locally you can use python3 main.py(this has option for generating new data) or can also use streamlit run display_allocation.py

-> After the allocator is run, allocations will be stored in allocations_files folder
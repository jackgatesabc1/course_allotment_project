Instructions to use: "python3 main.py", and then "streamlit run display_allocation.py"
If you want to use different dataset, then uncomment the first line in main.py

Quick glossary:
1) Section: Initial division of total batch of students into 8 parts called as sections
2) Department: The field of study (Example: Computer Science, Chemical Engineering)
3) Project: The different themes (for example in 2024 there were 6 themes, Food wastage, Outdoor spaces, Wheelchair design, etc..)
4) Group: The team of 6 or 7 members who all belong to same section and have same project(theme)
5) CPI: The GPA or overall performance of the student(range is 0 to 10)
6) Preferences: A value from 0 to 100 given by each student for each project(theme) that represents how much he likes the theme


There are students of different departments(such as Computer Science, Chemical Engineering, etc..) who are taking this course. 

There are eight "Sections" (slots). Each section corresponds to a specific time slot of the week.
Eg: Section-1 is Monday afternoon, Section-2 is Monday evening

There are different projects available (Eg: Solution for food wastage, Ideas for outdoor spaces, etc..). Each student will provide us with his preferences of the projects(he will assign an integer between 0 to 100 for each project indicating his affection for that project)

Now, we need to assign each student to a particular section(based on his available time slots) and in that section, assign him a particular project. We are assigning sections 

We need to assign students to projects by keeping in mind two things:
1) Preferences of students
2) Diversity: Each project should get approximately equal distribution of grades of students (i.e no project should have only students with low grades), and also try to have an equal distribution of students of a department among the projects, so that each project has students of diverse departments. Gender diversity as well should be taken care of.

Now, we need to form groups(of around size 6) of students who have the same project and section. The students will now work together as a group to finish their project. This group must be diverse. What exactly do we mean by diverse?
1) No group should have students of only low grades
2) Each group should have students of multiple departments
3) Gender diversity(try to maximise the number of groups which have both the genders)

Additional stuff:
1) Friends: Each student can provide us with one or two names of students that he wants to do the project with, and we will try to accomodate such requests as much as we can.

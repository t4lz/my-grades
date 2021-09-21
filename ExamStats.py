#!/usr/bin/env python
# coding: utf-8

# Loading the json with the grade data:

# In[1]:


import json
with open('grades.json', 'rb') as f:
    data = json.load(f)


# Extracting the relevant information out of the json for one course:

# In[2]:


build_dict = lambda course: {
    'id': course['content']['achievementDto']['cpCourseLibDto']['id'], 
    'course_name_de': course['content']['achievementDto']['cpCourseLibDto']['courseTitle']['value'], 
    'course_name_en': course['content']['achievementDto']['cpCourseLibDto']['courseTitle']['translations']['translation'][1]['value'], 
    'course_number': course['content']['achievementDto']['cpCourseLibDto']['courseNumber']['courseNumber'], 
    'ects': course['content']['achievementDto']['cpCourseLibDto']['ectsCredits'], 
    'semester_code': course['content']['achievementDto']['semesterLibDto']['key'], 
    'semester_name_de': course['content']['achievementDto']['semesterLibDto']['semesterDesignation']
    ['value'], 
    'semester_name_en': course['content']['achievementDto']['semesterLibDto']['semesterDesignation']
    ['translations']['translation'][1]['value'], 
    'semester_start_date': course['content']['achievementDto']['semesterLibDto']['startOfAcademicSemester']['value'], 
    'semester_end_date': course['content']['achievementDto']['semesterLibDto']['endOfAcademicSemester']['value'], 
    'grade_date': course['content']['achievementDto']['achievementDate']['value'], 
    'grade_name_de': course['content']['achievementDto']['gradeDto']['name']['value'], 
    'grade_name_en': course['content']['achievementDto']['gradeDto']['name']['translations']['translation'][1]['value'], 
    'grade': course['content']['achievementDto']['gradeDto']['value'], 
}


# Creating a list of dicts, each dict containing the info for one course.

# In[3]:


dicts = [build_dict(course) for course in data['resource']]


# For each course, parse the grades out of its html file, and add to its dict:

# In[4]:


from bs4 import BeautifulSoup

possible_grades = ['1.0', '1.3', '1.4', '1.7', '2.0', '2.3', '2.4', '2.7', '3.0', '3.3', '3.4', '3.7', '4.0', '4.3', '4.7', '5.0']
standard_possible_grades = ['1.0', '1.3', '1.7', '2.0', '2.3', '2.7', '3.0', '3.3', '3.7', '4.0', '4.3', '4.7', '5.0']
all_possible_grades = possible_grades + ['did_not_show_up']

for d in reversed(dicts): # iterating in reverse order so we can remove elements while iterating.
    # University regulation: written exams from first semester are weighted half the points.
    d['grade_weight'] = d['ects']
    if ('Discrete Structures' in d['course_name_en'] 
        or 'Introduction to Informatics' in d['course_name_en']
        or 'Computer Organization' in d['course_name_en']
       ):
        d['grade_weight'] >>= 1 # divide by 2 but leave as int (known to all be devisable by 2)
    # read the html file to a string
    try:
        with open('stats/{}.html'.format(d['id']), 'rb') as f:
            html_doc = f.read()    
        soup = BeautifulSoup(html_doc, 'html.parser')
        # the data can be found in the titles of div objects with the class "kandcountbox"
        divs = soup.find_all('div', 'kandcountbox')
        titles = [div['title'] for div in divs]
        # A list of tuples (<grade>, <number of students>) e.g. ('1.0', 3)
        nums = [(ts[-1].split()[0], int(ts[-2].split()[0])) for t in titles if (ts := t.split(','))]
        d.update((grade, 0) for grade in all_possible_grades) # All courses get all grades, also if 0 students that grade.
        for i, t in enumerate(titles):
            if 'Nicht erschienen' in t: # Students who did not show up
                d['did_not_show_up'] = nums[i][1]
            elif '5.0' in t: # add up fails and cheats together.
                d['5.0'] += nums[i][1]
        # We already counted all the 5.0s and added them, so don't add again.
        d.update((tup for tup in nums if tup[0] != '5.0'))
    except FileNotFoundError:
        print("No statistics file for ", d['course_name_en'])
        dicts.remove(d)


# Create a pandas dataframe with the data:

# In[5]:


import pandas as pd

df = pd.DataFrame(dicts)
df['did_show_up'] = df[possible_grades].sum(axis=1)
df['numeric_grade'] = pd.to_numeric(df['grade'])
df['int_grade_X10'] = df['grade'].apply(lambda x: int((x.replace('.', '') + '0')[:2]))
df['5.0_with_noshows'] = df['5.0'] + df['did_not_show_up']
df['total_students'] = df['did_show_up'] + df['did_not_show_up']
df['grade'] = df['grade'].apply(lambda s: (s + '.0')[:3])
grades_with_noshows = possible_grades + ['5.0_with_noshows']
grades_with_noshows.remove('5.0')
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    display(df)


# In[6]:


int_grades = list(map(lambda x: int(x.replace('.', '')), possible_grades)) # '1.3' -> 13
df['mean'] = ((df[possible_grades] * int_grades).sum(axis=1) / df['did_show_up']) / 10
df['mean_with_noshows'] = ((df[grades_with_noshows] * int_grades).sum(axis=1) / df['total_students']) / 10
df


# In[7]:


import numpy as np


# We want to calculate the Z-Score of each grade. For a single course, where I got the grade $x$, the mean grade is $\mu$ and the standard deviation is $\sigma$, then $Z = \frac{x - \mu}{\sigma}$. We now calculate that simulataneously for each course.

# We already have the mean and the grade of each course, so now we calculate the standard deviation. For a single course we used the (biased) standard deviation $$\sigma = \sqrt{\frac{\sum_{x \in X}(x-\mu)^2}{N}}$$ where $X$ is the the set of all grades in this one exam and $N$ is the total number of students.
# Our data looks a bit different however. What we have is for every possible grade, the number of students with that grade, so our calculation will look like this: 
# $$\sigma = \sqrt{\frac{\sum_{g \in G}n_g(g-\mu)^2}{N}}$$
# Where $G$ is the set of possible grades ($1.0$, $1.3$, ...) and for a grade $g \in G$, $n_g$ is the number of students with that grade in this exam.

# First, we create a matrix which has for each exam the row vector $(\ \ldots \ (g - \mu)^2 \   \ldots\ )_{g \in G}$ which contain the squared difference of every possible grade and the mean:

# In[8]:


# The (x - \mu)^2 part of the calculation for the sd.
squared_differences = np.square(np.array([np.array(int_grades)/10,]*len(df)) - np.array([df['mean'],] * len(int_grades)).transpose())


# We now multiply this matrix element-wise with our data, and get the matrix 
# $(n_{g,i}(g-\mu)^2)_{g \in G, i \in E}$ where $E$ is the set of exams and $n_{g,i}$ is the number of students who get the grade $g$ in exam $i$. We then sum each row, and divide it by the total number of students who took that exam, which gives us a vector where every element is the complete term inside the squre root above, for one exam. We then just take the square root element-wise, and get a vector of the standard deviations of all exams, which we add to our DataFrame.

# In[9]:


df['standard_deviation'] = np.sqrt(np.multiply(df[possible_grades], squared_differences).sum(axis=1) / df['did_show_up'])


# In[10]:


df


# Once we have all that, we just do the $\frac{x-\mu}{\sigma}$ calculation for each exam.
# 
# Of course we do it with numpy's vectorized operations.

# In[11]:


df['z'] = (df['numeric_grade'] - df['mean']) / df['standard_deviation']
df


# In[12]:


# Now compute Z-score with noshows:
squared_differences = np.square(np.array([np.array(int_grades)/10,]*len(df)) - np.array([df['mean_with_noshows'],] * len(int_grades)).transpose())
df['standard_deviation_with_noshows'] = np.sqrt(np.multiply(df[grades_with_noshows], squared_differences).sum(axis=1) / df['total_students'])
df['z_with_noshows'] = (df['numeric_grade'] - df['mean_with_noshows']) / df['standard_deviation_with_noshows']
df


# In[13]:


# inclusive definition of percentile
df['percentile'] = (np.multiply(np.array([np.array(int_grades),]*len(df)) < np.array([df['int_grade_X10'],] * len(int_grades)).transpose(), df[possible_grades]).sum(axis=1) / df['did_show_up']) * 100


# In[14]:


# calculate percentile including noshows
df['percentile_with_noshows'] = (np.multiply(np.array([np.array(int_grades),]*len(df)) < np.array([df['int_grade_X10'],] * len(int_grades)).transpose(), df[grades_with_noshows]).sum(axis=1) / df['total_students']) * 100
df


# In[15]:


# mean Z score
mean_z_score = np.multiply(df['z'], df['grade_weight']).sum() / df['grade_weight'].sum()
print(mean_z_score)
mean_z_score_with_noshows = np.multiply(df['z_with_noshows'], df['grade_weight']).sum() / df['grade_weight'].sum()
print(mean_z_score_with_noshows)


# In[16]:


avg_grade = np.multiply(df['numeric_grade'], df['grade_weight']).sum() / df['grade_weight'].sum()
print(avg_grade)


# In[17]:


# Percentile is weighted by the grade weight and by the number of students in the course.
weights = np.multiply(df['did_show_up'], df['grade_weight'])
avg_percentile = np.multiply(df['percentile'], weights).sum() / weights.sum()
print(avg_percentile)
weights = np.multiply(df['total_students'], df['grade_weight'])
avg_percentile_with_noshows = np.multiply(df['percentile_with_noshows'], weights).sum() / weights.sum()
print(avg_percentile_with_noshows)


# In[18]:


total_ects = df['ects'].sum()


# In[19]:


df.sort_values(by=['grade','ects', 'percentile', 'z', 'semester_start_date', 'course_name_en'], 
               ascending=[True, False, True, True, True, True], inplace=True, )
df


# Save the DataFrame data to a json:

# In[20]:


df.to_json(path_or_buf='web/js/grade_data.json', orient='records')


# In[21]:


df[possible_grades + ['grade_weight']]


# In[22]:


# multiply the number of students that got each grade, with the weight of that exam.
weighted_nums = (df[possible_grades].transpose() * df['grade_weight']).transpose()
weighted_nums


# In[23]:


sums = weighted_nums.sum()
sums


# In[24]:


denominator = sums.sum()
denominator


# In[25]:


mean = (sums * int_grades).sum() / (denominator * 10)
mean


# In[26]:


grades_array = np.array(int_grades)/10
squared_diffs = np.square(grades_array - mean)
squared_diffs


# In[27]:


# element wise multiplication, to weight each diff with its grade weight, and count it for every student with that grade
weighted_squared_diffs = np.multiply(sums, squared_diffs)
weighted_squared_diffs


# In[28]:


from math import sqrt
sd = sqrt(weighted_squared_diffs.sum() / denominator)
sd


# In[29]:


total_z = (avg_grade - mean) / sd
total_z


# This "total Z-Score" is calculated to take into account the number of students in each course, unlike when just taking an average (weighted for credits but not for students) of the Z-Scores of all courses. This result is less affected by courses with a small amount of participants. This might make sense if you are trying to compare me to the total population of computer science students. A course with a small number of participants could be like a study with a small number of participants. It is less likely to provide a selection representative of the entire population. In the "Mean Z-Score" we only weight courses by their ECTS, here we also take the number of participants into account.

# In[30]:


# Calculate total Z again with noshows:
weighted_nums_noshows = (df[grades_with_noshows].transpose() * df['grade_weight']).transpose()
sums_noshows = weighted_nums_noshows.sum()
denominator_noshows = sums_noshows.sum()
mean_noshows = (sums_noshows * int_grades).sum() / (denominator_noshows * 10)
grades_array = np.array(int_grades)/10
squared_diffs_noshows = np.square(grades_array - mean_noshows)
weighted_squared_diffs_noshows = np.multiply(sums_noshows, squared_diffs_noshows)
sd_noshows = sqrt(weighted_squared_diffs_noshows.sum() / denominator_noshows)
total_z_with_noshows = (avg_grade - mean_noshows) / sd_noshows
total_z_with_noshows


# In[31]:


with open('web/js/agg_data.json', 'w') as agg_f:
    json.dump({
        'mean_z_score': total_z,
        'mean_z_score_with_noshows': total_z_with_noshows,
        'avg_grade': avg_grade,
        'avg_percentile': avg_percentile,
        'avg_percentile_with_noshows': avg_percentile_with_noshows,
        'total_ects': int(total_ects),
    }, agg_f)


# In[32]:


def aggregate_semester(group_frame):
    d = {}
    d['Number of Courses'] = len(group_frame.index)
    d['Total ECTS'] = group_frame['ects'].sum()
    d['My Mean Grade'] = np.average(group_frame.numeric_grade, weights=group_frame.grade_weight)
    d['My Mean Z-Score'] = np.average(group_frame.z, weights=np.multiply(group_frame.grade_weight, group_frame.did_show_up))
    d['My Mean Percentile'] = np.average(group_frame.percentile, weights=np.multiply(group_frame.grade_weight, group_frame.did_show_up))
    # Using dtype object to prevent int to float conversion. 
    # It's not that bad because no calculation will be mad on the series in that state,
    # And once back in the dataframe, each column gets a specific type
    return pd.Series(d, dtype=object)


semester_data = df.groupby(['semester_start_date', 'semester_code'] # include code for display, date for sort
                          ).apply(aggregate_semester
                                 ).sort_values('semester_start_date' # probably already sorted, but to be safe.
                                              ).reset_index().drop('semester_start_date', axis=1)
semester_data


# In[33]:


# Check that the types make sense:
semester_data.dtypes


# In[34]:


with open('web/js/semester_data.json', 'w') as semester_f:
    json.dump(semester_data.to_dict('list'), semester_f)


# In[35]:


my_grade_distribution = df[['grade', 'grade_weight']].groupby('grade').sum()
my_grade_distribution['grade_weight'] = my_grade_distribution['grade_weight'] / my_grade_distribution['grade_weight'].sum()
empty_frame = pd.DataFrame(0, index=standard_possible_grades, columns=['grade_weight'], dtype=my_grade_distribution.dtypes[0])
complete_distribution = pd.merge(my_grade_distribution, empty_frame, left_index=True, right_index=True, how='outer', sort=True).fillna(0)['grade_weight_x']
complete_distribution


# In[36]:


with open('web/js/personal_distribution.json', 'w') as dist_f:
    json.dump(list(complete_distribution), dist_f)


# In[ ]:





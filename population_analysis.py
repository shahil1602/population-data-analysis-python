"""
CITS 1401: Computational Thinking with Python
Student Name: PATHAN SHAHIL
Student No.: 24868896
Project 1 Semester 1 2025:

Task: You are required to write a Python 3 program that will read two CSV files. After
reading the files, your program is required to complete the following tasks. More details
are given in the Output specification section.

1. Find the age group that contains a specific input age.
2. Calculate population statistics for two specific SA3 areas.
3. Find the SA3 area with the largest population in the age group, for each unique state,
and its percentage.
4. Calculate the correlation between the age structure of two specific SA2 areas.
"""

# Code for main function that runs the entire program with required inputs
def main(csvfile_1, csvfile_2, age, sa2_1, sa2_2):
# Read the area and population CSV files into lists    
    area_info = parse_csv(csvfile_1)
    population_info = parse_csv(csvfile_2)

# This part identifies the age group that includes the input age
    age_limits = find_age_band(population_info[0], age)

# This part determines SA3 code corresponding to the given SA2 code (sa2_1 and sa2_2)
    group_code_a = locate_sa3(area_info, sa2_1)
    group_code_b = locate_sa3(area_info, sa2_2)

# This part is used to calculate the both mean & Standard deviation for both SA3's in specified age
    result_a = calc_group_stats(area_info, population_info, group_code_a, age_limits)
    result_b = calc_group_stats(area_info, population_info, group_code_b, age_limits)

# This finds the SA3 with the highest average population in each state for the age group
    top_sa3s = highest_group_by_state(area_info, population_info, age_limits)

# It measures how similar the two SA2's are by age population structure
    similarity_score = compute_similarity(population_info, sa2_1, sa2_2)

    return age_limits, [result_a, result_b], top_sa3s, round(similarity_score, 4)

# Reads CSV files and stores each line as a list of values
def parse_csv(filename):
    contents = []
    with open(filename, 'r') as file:
        for entry in file:
            contents.append(entry.strip().split(','))
    return contents

# Function to find the age group for the given input age
def find_age_band(header_row, age_input):
    index = 0
    while index < len(header_row):
        label = header_row[index].strip().lower()
        if label.startswith("age"):
            segment = label[4:].strip()
            if '-' in segment:
                parts = segment.split('-')
                min_age = int(parts[0])
                max_age = int(parts[1])
                if min_age <= age_input <= max_age:
                    return [min_age, max_age]
            elif 'and over' in segment:
                lower_bound = int(segment.split()[0])
                if age_input >= lower_bound:
                    return [lower_bound, None]
        index += 1
    return []

# This function finds the SA3 code for a given/specific SA2 code
def locate_sa3(area_lines, sa2_target):
    title_row = area_lines[0]
    sa2_idx = -1
    sa3_idx = -1

    for i in range(len(title_row)):
        cleaned = title_row[i].strip().lower().replace(" ", "")
        if cleaned == "sa2code":
            sa2_idx = i
        if cleaned == "sa3code":
            sa3_idx = i

    for record in area_lines[1:]:
        if record[sa2_idx] == sa2_target:
            return record[sa3_idx]
    return None

# Finds all SA2 codes that are part of a given SA3 code
def extract_all_sa2(area_lines, target_code):
    header = area_lines[0]
    pos_sa2 = -1
    pos_sa3 = -1

    for idx in range(len(header)):
        item = header[idx].strip().lower().replace(" ", "")
        if item == "sa2code":
            pos_sa2 = idx
        if item == "sa3code":
            pos_sa3 = idx

    gathered = []
    for r in area_lines[1:]:
        if r[pos_sa3] == target_code:
            gathered.append(r[pos_sa2])
    return gathered

# Identifies which columns matches the given age group
def locate_age_indexes(header_row, bounds):
    lower, upper = bounds
    age_columns = []

    for idx in range(len(header_row)):
        column = header_row[idx].strip().lower()
        if column.startswith("age"):
            age_label = column[4:]
            if '-' in age_label:
                range_vals = age_label.split('-')
                from_age = int(range_vals[0])
                to_age = int(range_vals[1])
                if from_age == lower and to_age == upper:
                    age_columns.append(idx)
            elif "and over" in age_label and upper is None and str(lower) in age_label:
                age_columns.append(idx)
    return age_columns

# Calculates the average and Standard Deviation of population values for one SA3 group
def calc_group_stats(area_info, pop_info, sa3code, age_bounds):
    if sa3code is None:
        return []

    related_sa2 = extract_all_sa2(area_info, sa3code)
    header = pop_info[0]
    age_fields = locate_age_indexes(header, age_bounds)

    code_col = -1
    for i in range(len(header)):
        if header[i].strip().lower() == "area_code_level2":
            code_col = i
            break

    values = []
    for row in pop_info[1:]:
        if row[code_col] in related_sa2:
            acc = 0
            for idx in age_fields:
                if row[idx].isdigit():
                    acc += int(row[idx])
            values.append(acc)

    if len(values) <= 1:
        return []

    average = sum(values) / len(values)
    variance = sum((val - average) ** 2 for val in values)
    standard_dev = (variance / (len(values) - 1)) ** 0.5

    return [sa3code, round(average, 4), round(standard_dev, 4)]


# Identifies the most popular SA3 for the target age group in each state
# Returns the state name, sa3 name, and percentage of population
def highest_group_by_state(area_info, pop_info, age_bounds):
    header_row = area_info[0]
    st_idx = sa3_idx = name_idx = sa2_idx = -1

    for i in range(len(header_row)):
        entry = header_row[i].lower().replace(" ", "")
        if entry == "s_tname":
            st_idx = i
        elif entry == "sa3code":
            sa3_idx = i
        elif entry == "sa3name":
            name_idx = i
        elif entry == "sa2code":
            sa2_idx = i

    states = []
    for row in area_info[1:]:
        current = row[st_idx].strip().lower()
        found = False
        for s in states:
            if s == current:
                found = True
        if not found:
            states.append(current)

    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            if states[i] > states[j]:
                temp = states[i]
                states[i] = states[j]
                states[j] = temp

    final_output = []

    for state in states:
        unique_sa3 = []
        for line in area_info[1:]:
            if line[st_idx].strip().lower() == state:
                already = False
                for s in unique_sa3:
                    if s[0] == line[sa3_idx]:
                        already = True
                if not already:
                    unique_sa3.append([line[sa3_idx], line[name_idx]])

        max_count = -1
        best_group = ""
        total_state_pop = 0
        best_code = ""
        
        for s in unique_sa3:
            matching_sa2 = []
            for entry in area_info[1:]:
                if entry[sa3_idx] == s[0]:
                    matching_sa2.append(entry[sa2_idx])

            pop_header = pop_info[0]
            col_age = locate_age_indexes(pop_header, age_bounds)
            level_col = -1
            for i in range(len(pop_header)):
                if pop_header[i].lower() == "area_code_level2":
                    level_col = i
                    break

            partial = 0
            complete = 0
            for row in pop_info[1:]:
                if row[level_col] in matching_sa2:
                    for i in range(len(row)):
                        if pop_header[i].lower().startswith("age") and row[i].isdigit():
                            complete += int(row[i])
                    for idx in col_age:
                        if row[idx].isdigit():
                            partial += int(row[idx])

            if partial > max_count:
                max_count = partial
                best_group = s[1]
                best_code = s[0]
                total_state_pop = complete
            elif partial == max_count:
                if s[0] < best_code:
                    best_group = s[1]
                    best_code = s[0]
                    total_state_pop = complete

        ratio = round(max_count / total_state_pop, 4) if total_state_pop > 0 else 0.0
        final_output.append([state, best_group.lower(), ratio])

    return final_output

# Calculates the correlation coefficient between two SA2 areas based on age distributions
def compute_similarity(popdata, code_x, code_y):
    header = popdata[0]
    index_code = -1

    for i in range(len(header)):
        if header[i].strip().lower() == "area_code_level2":
            index_code = i
            break

    list1 = []
    list2 = []

    for r in popdata[1:]:
        if r[index_code] == code_x:
            list1 = r
        if r[index_code] == code_y:
            list2 = r

    #checks if both rows were found
    if not list1 or not list2:
        return 0.0

    xs = []
    ys = []

    for i in range(len(header)):
        if header[i].lower().startswith("age"):
            if i < len(list1) and i < len(list2):
                if list1[i].isdigit() and list2[i].isdigit():
                    xs.append(int(list1[i]))
                    ys.append(int(list2[i]))

    n = len(xs)
    if n == 0:
        return 0.0

    mean1 = sum(xs) / n
    mean2 = sum(ys) / n

    num = sum((xs[i] - mean1) * (ys[i] - mean2) for i in range(n))
    denom1 = sum((xs[i] - mean1) ** 2 for i in range(n))
    denom2 = sum((ys[i] - mean2) ** 2 for i in range(n))

    if denom1 == 0 or denom2 == 0:
        return 0.0

    return num / ((denom1 * denom2) ** 0.5)





"""
Debugging Documentation:

Issue 1:      (Date 2025 April 11)
Error Description:
Unexpected: Correlation coefficient returned 0 even when two SA2s had highly similar distribtioons

Erroneous Code Snippet:
if denom1 == 0 or denom2 == 0:
    return 0.0
    
Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 25, '401011001', '401021003')

Reflection:
It looked like the correlation was broken. After checking, I realized that when all values are the same, variance is 0, and Pearson correlation becomes undefined. I updated the logic to skip such inputs gracefully. It taught me that sometimes math is technically correct but practically misleading.


Issue 2:      (Date 2025 April 11)
Error Description:
Unexpected OP3 output - duplicate state entries showing up

Erroneous Code Snippet:
if not found:
    states.append(current)
    
Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 20, '401011001', '401021003')

Reflection:
Realized that "South Australia" and "south australia" were treated as different. Standardized everything with '.lower().strip()'. A good reminder that data normalization is not optional - it's the difference between 1 bug and 1,000.


Issue 3:      (Date 2025 April 13)
Error Description:
ZeroDivisionError: float division by zero

Erroneous Code Snippet:
percent = round(max_age / best_total, 4)

Test Case:
main('SampleData_Areas.csv', 'SampleData_Populations.csv', 90, '401011001', '401021003')

Reflection:
In some cases with no population across all age groups, division by zero occured. So then, I added a condition to skip that part or set ratio to 0 when best_total == 0.
"""



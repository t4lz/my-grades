#! /usr/bin/python3

import json
with open('grades.json', 'rb') as f:
    data = json.load(f)
ids = [course['content']['achievementDto']['cpCourseLibDto']['id'] for course in data['resource']]
with open('ids.txt', 'w') as ids_list:
    ids_list.write('\n'.join((str(i) for i in ids)))

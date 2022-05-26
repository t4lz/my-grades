#! /usr/bin/python3

import json
with open('grades.json', 'rb') as f:
    data = json.load(f)
ids = [c['id'] for course in data['resource'] if 'id' in (c := course['content']['achievementDto']['cpCourseLibDto'])]
with open('ids.txt', 'w') as ids_list:
    ids_list.write('\n'.join((str(i) for i in ids)))

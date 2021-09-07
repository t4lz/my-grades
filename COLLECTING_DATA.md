Collecting the Data
===================

Since I am only going to do the data collection about once (let's say O(1) times), I decided to go with an interactive approach, since this would be the fastest way to get the data. Automating and streamlining the process would be prettier, but is actually not important.
This document will describe the quick process I went threw to collect and prepare the data.

Getting My Grades
-----------------

Surfed with my browser with the developer tools open to [the "My achievements" page on TUM-Online](https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/#/slc.xm.ac/achievements?$ctx=design=ca;lang=en&orgId=none). In the `Network` tab I saw the request: `https://campus.tum.de/tumonline/ee/rest/slc.xm.ac/achievements?$orderBy=acDate=descnf` that returned a json with the data of my courses and grades. I saved that json in grades.json.

Getting The Exam Statistics
---------------------------

For the Exam Statistics I did not find a request that returns a json, so I will parse the html. A request that returns an html with all the data I want for one exam is: `https://campus.tum.de/tumonline/pl/ui/$ctx;design=ca2;header=max;lang=de/WBEXAMSTATISTICS.wbStart?pOrgNr=&pStpSpNr=950552753`. I copied that request as curl from the developer tools, to use in little script. I figured the number at the end must be some kind of course/exam id, and looked for it in the json I download in the last section. It was indeed there, so with python I created a file with just a list of all the ids of my exams:
```
import json
with open('grades.json', 'rb') as f: 
    data = json.load(f)
ids = [course['content']['achievementDto']['cpCourseLibDto']['id'] for course in data['resource']]  
with open('ids.txt', 'w') as ids_list: 
    ids_list.write('\n'.join((str(i) for i in ids)))
```
Then in a bash script (`fetch_stats.sh`) I called the curl command for each of the IDs in the list, saving all the html files in the directory `stats`.

Analysing The Exam Statistics
---------------------------

In the Jupyther Notebook ExamStats.ipynb you can see the parsing and the analysis of the data.

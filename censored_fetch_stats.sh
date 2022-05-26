#!/bin/bash


# In this file the authentication tokens where censored from the requests.


curl 'https://campus.tum.de/tumonline/ee/rest/slc.xm.ac/achievements?$orderBy=acDate=descnf' \
  -H 'Connection: keep-alive' \
  -H 'Accept: application/json' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
  -H 'Accept-Language: de' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'Authorization: Bearer <CENSORED>=' \
  -H 'Content-Type: application/json' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/' \
  -H 'Cookie: <CENSORED!>' \
  --compressed  > grades.json;

python3 extract_ids.py; # Extract a list of ids and write it to ids.txt.

# For every course, fetch the statistics html page.
for id in $(cat ids.txt); 
do 
# OLD "API":
# curl "https://campus.tum.de/tumonline/pl/ui/\$ctx;design=ca2;header=max;lang=de/WBEXAMSTATISTICS.wbStart?pOrgNr=&pStpSpNr=$id" \
#   -H 'Connection: keep-alive' \
#   -H 'sec-ch-ua: "Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'Upgrade-Insecure-Requests: 1' \
#   -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
#   -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
#   -H 'Sec-Fetch-Site: same-origin' \
#   -H 'Sec-Fetch-Mode: navigate' \
#   -H 'Sec-Fetch-Dest: iframe' \
#   -H 'Referer: https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/' \
#   -H 'Cookie: <CENSORED!>' \
#   --compressed  > stats/$id.html;
curl "https://campus.tum.de/tumonline/ee/rest/slc.xm.exs/examStatistics/$id" \
  -H 'authority: campus.tum.de' \
  -H 'accept: application/json' \
  -H 'accept-language: de' \
  -H 'authorization: Bearer <CENSORED!>' \
  -H 'content-type: application/json' \
  -H 'cookie: <CENSORED!>' \
  -H 'referer: https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: <CENSORED!>' \
  --compressed  > json_stats/$id.json;
done

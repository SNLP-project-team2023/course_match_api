# course_match_api
Course match api

The project is build with ``apiflask``
```
https://apiflask.com/
```

Python version: 3.11

Install all deps
```bash
pip install -U pip wheel
pip install -r requirements.txt
```

Add vairalbles in *.env*
```
COURSE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
COURSE_API_URL=https://course.api.aalto.fi:443/api/sisu/v1/courseunitrealisations?user_key=
SBERT_MODEL=sentence-transformers/msmarco-distilbert-base-tas-b
SISU_COURSE_PREFIX=https://sisu.aalto.fi/student/courseunit/
MYCOURSE_COURSE_PREFIX=https://mycourses.aalto.fi/course/search.php?search=
```

Start the api
```
python app.py runserver
```


Save deps into requirement.txt
```commandline
pip freeze > requirements.txt
```

The swagger file is at ``API_URL/openapi.yaml`` 
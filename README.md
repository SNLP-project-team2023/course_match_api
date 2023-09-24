# course_match_api
Course match api

The project is build with ``apiflask``
```commandline
https://apiflask.com/
```

Python version: 3.8.0

Install all deps
```
pip install -U pip wheel
pip install -r requirements.txt
```

Start the api
```
python main.py
```

Save deps into requirement.txt
```commandline
pip freeze > requirements.txt
```

The swagger file is at ``API_URL/openapi.yaml``

Generate docker image
```commandline
docker build --target production -t course_match_api .
```

Run docker image
```commandline
docker run -p 8080:8080 course_match_api
```

# [LICENSE: CC BY-NC 4.0](LICENSE)

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

To view a copy of this license, visit <http://creativecommons.org/licenses/by-nc/4.0/>
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

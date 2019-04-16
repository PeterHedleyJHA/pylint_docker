pylint-server
====
[![Build Status](https://travis-ci.org/drivet/pylint-server.svg?branch=master)](https://travis-ci.org/drivet/pylint-server)
[![Coverage Status](https://coveralls.io/repos/drivet/pylint-server/badge.svg?branch=master)](https://coveralls.io/r/drivet/pylint-server?branch=master)
[![Pylint Rating](https://pylint.desmondrivet.com/drivet/pylint-server/rating.svg)](https://pylint.desmondrivet.com/drivet/pylint-server/report.html)

A small Flask application to keep keep track of pylint, coverage reports and ratings.

Modified from [**drivet_pylint**](https://github.com/drivet/pylint-server])

# Requirements

The two main requirements are Flask and Travis.  No other build server ios
supported at the moment.

# Deployment and Usage

## Deployment

1. Start a blank instance using -> AWS -> Launch Templates -> Pylint_Coverage_Server
2. `ssh -i ~/.ssh/<ssh_key> ubuntu@ <IPv4 Public IP>`
3. `sudo apt-get update`
4. `sudo docker install docker.io`
5. `git clone https://github.com/PeterHedleyJHA/pylint_docker.git`
6. `cd pylint_docker`
7. `sudo docker build . -t my_flask_app`
8. `sudo docker run -d --restart=always -p 80:80 --name=peter my_flask_app`
9. **Relax that is it!**

## Usage

In your .travis.yml file for the project you wish to track put the following...

```
language: python

python:

  - "3.6"
  
install:
  - "pip install pylint"
  - "pip install coverage"
  - "pip install nose2"
  - "pip install pylint-json2html"
  
script:
  - coverage run -m nose2

after_success:
  - pylint --output-format=parseable **/*.py > /tmp/pylint.txt
  - pylint --output-format=json **/*.py | pylint-json2html -f json -o /tmp/pylint_html_report.html
  - cat /tmp/pylint.txt
  - coverage report -m > /tmp/coverage.html
  - cat /tmp/coverage.html
  - coverage html -d coverage_html
  - curl -v -m 120 -X POST -F pull-req=$TRAVIS_PULL_REQUEST -F git-slug=$TRAVIS_REPO_SLUG -F git-branch=$TRAVIS_BRANCH -F pylint-html-report=@/tmp/pylint_html_report.html -F pylint-report=@/tmp/pylint.txt http://63.33.197.197:80/pylint-reports
  - curl -v -m 120 -X POST -F pull-req=$TRAVIS_PULL_REQUEST -F git-slug=$TRAVIS_REPO_SLUG -F git-branch=$TRAVIS_BRANCH -F coverage-html-report=@./coverage_html/index.html -F coverage-report=@/tmp/coverage.html http://63.33.197.197:80/coverage-reports
```

Place a .coveragerc file in your repo containing...
```
# .coveragerc to control coverage.py
[run]
branch = True
omit =
        */usr/local/lib*
	*/lib/python*
        */__init__.py
	*setup.py

[report]
omit =
	*/tests/*
        */usr/local/lib*
	*.local/lib*
	*/lib/python*
        */__init__.py
	*setup.py

# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover

    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug

    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError

    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:

ignore_errors = True

[html]


directory = coverage_html_report
```
#### Pylint scores are in the file
```/<repo>/<branch>/pylint_report.html``` \
with badge under... \
```/<repo>/<branch>/pylint.svg```

#### Coverage Scores are under..
```/<repo>/<branch>/cov_rep/coverage_report.html``` \
```/<repo>/<branch>/cov.svg``` 

Put a badge on your README accordingly - e.g. \
```![Build Status](http://<instance ip>/<repo>/<branch>/cov.svg)[http://<instance ip>/<repo>/<branch>/cov_rep/coverage_report.html]```

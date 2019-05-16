## pylint-server

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
4. `sudo apt-get install docker.io`
5. `git clone https://github.com/PeterHedleyJHA/pylint_docker.git`
6. `cd pylint_docker`
7. `sudo docker build . -t my_flask_app`
8. `sudo docker run -d --restart=always -p 80:80 --name=peter my_flask_app`
9. **Relax that is it!**

## Other Useful Docker Commands

`sudo docker exec -it peter bash` load the shell of a docker container named `peter`.
`sudo docker ps` see all running containers.
`sudo docker kill peter` :( stop docker container called `peter` from running.
`sudo docker rm peter` (need to do this too in order to re-run a container called `peter`)

## Usage

In your `.travis.yml` file for the project you wish to track put the following...

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
  - curl -v -m 120 -X POST -F pull-req=$TRAVIS_PULL_REQUEST -F git-slug=$TRAVIS_REPO_SLUG -F git-branch=$TRAVIS_BRANCH -F pylint-html-report=@/tmp/pylint_html_report.html -F pylint-report=@/tmp/pylint.txt http://<IPv4 Public IP>:80/pylint-reports
  - curl -v -m 120 -X POST -F pull-req=$TRAVIS_PULL_REQUEST -F git-slug=$TRAVIS_REPO_SLUG -F git-branch=$TRAVIS_BRANCH -F coverage-html-report=@./coverage_html/index.html -F coverage-report=@/tmp/coverage.html http://<IPv4 Public IP>:80/coverage-reports
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
```/reports/<repo>/<branch>/pylint_report.html``` \
with badge under... \
```/badges/<repo>/<branch>/pylint.svg```

#### Coverage Scores are under..
```/reports/<repo>/<branch>/cov_rep/coverage_report.html``` \
```/badges/<repo>/<branch>/cov.svg``` 

Put a badge on your README accordingly - e.g. \
```![Build Status](http://<instance ip>/badges/<repo>/<branch>/cov.svg)[http://<IPv4 Public IP>/reports/<repo>/<branch>/cov_rep/coverage_report.html]```



### Summary of Files

`.htpasswd`
Password for uploading and reading images from the container. 
See [**link**](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) for more details on creating password files (DO NOT OVERWRITE ANYTHING ON ONE OF OUR EXISTING AWS SERVERS!!!!!)

`nginx.conf`
Used to create the security permissions for the docker image. These define areas that are secured and points to the uwsgi.sock for the flask app.

`Dockerfile`
Build file for the server uses the [**uwsgi_flask_nginx**](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/) docker container as a starter. It then copies relevant files into the image and installs the python pip requirements from `requirements.txt`.


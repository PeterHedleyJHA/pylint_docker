from __future__ import absolute_import

from flask import Flask, request, Blueprint, current_app
import os
import re
from travispy import TravisPy
import logging


LOG_LEVEL = logging.INFO
OUTPUT_FOLDER = '/tmp/pylint-server'
VALID_REPOS = []
BADGE_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" width="85" height="20">
  <linearGradient id="a" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <!-- whole rectangle -->
  <rect rx="3" width="85" height="20" fill="#555"/>
  <!-- rating part -->
  <rect rx="3" x="50" width="35" height="20" fill="#{2}"/>
  <path fill="#{2}" d="M50 0h4v20h-4z"/>
  <!-- whole rectangle -->
  <rect rx="3" width="85" height="20" fill="url(#a)"/>
  <g fill="#fff" text-anchor="middle"
                 font-family="DejaVu Sans,Verdana,Geneva,sans-serif"
                 font-size="11">
    <text x="25" y="15" fill="#010101" fill-opacity=".3">{1}</text>
    <text x="25" y="14">{1}</text>
    <text x="67" y="15" fill="#010101" fill-opacity=".3">{0:.2f}</text>
    <text x="67" y="14">{0:.2f}</text>
  </g>
</svg>
"""    

mainbp = Blueprint('main', __name__)


@mainbp.route('/pylint-reports', methods=['POST'])
def handle_report_post():
    current_app.logger.info('handling POST on /reports')

    git_slug=None
    print(request)
    if 'git-slug' in request.form:
        git_slug = str(request.form['git-slug']).split("/")[-1]
    else:
        raise ValueError('invalid repository slug')

    git_branch=None
    if 'git-branch' in request.form:
        git_branch = request.form['git-branch']
    else:
        raise ValueError('invalid repository branch')
    
    report = None
    if 'pylint-report' in request.files:
        report = request.files['pylint-report'].read()
    else:
        raise ValueError('No Report Specified')
    
    output_folder = current_app.config['OUTPUT_FOLDER']
    output_report = os.path.join(output_folder, git_slug, git_branch, 'report.html')
    current_app.logger.info('saving report to '+output_report)
    save_file(output_report, report)

    (rating, colour) = get_pylint_rating_and_colour(report)
    output_badge = os.path.join(output_folder, git_slug, git_branch, 'rating.svg')
    current_app.logger.info('saving badge to '+output_badge)
    save_file(output_badge, BADGE_TEMPLATE.format(rating,'pylint',colour))
    
    return 'OK\n', 200



@mainbp.route('/coverage-reports', methods=['POST'])
def handle_coverage_report_post():
    current_app.logger.info('handling POST on /reports')

    git_slug=None
    print(request)
    if 'git-slug' in request.form:
        git_slug = str(request.form['git-slug']).split("/")[-1]
    else:
        raise ValueError('invalid repository slug')

    git_branch=None
    if 'git-branch' in request.form:
        git_branch = request.form['git-branch']
    else:
        raise ValueError('invalid repository branch')
    
    report = None
    if 'coverage-report' in request.files:
        report = request.files['coverage-report'].read()
    else:
        raise ValueError('No Report Specified')
    
    output_folder = current_app.config['OUTPUT_FOLDER']
    output_report = os.path.join(output_folder, git_slug, git_branch, 'coverage_report.html')
    current_app.logger.info('saving report to '+output_report)
    save_file(output_report, report)

    (rating, colour) = get_coverage_rating_and_colour(report)
    output_badge = os.path.join(output_folder, git_slug, git_branch, 'coverage_rating.svg')
    current_app.logger.info('saving badge to '+ output_badge)
    save_file(output_badge, BADGE_TEMPLATE.format(rating, "cov", colour))
    
    return 'OK\n', 200


def get_coverage_rating_and_colour(report):
    colour = '9d9d9d'
    rating = 0
    match = re.findall("\d+%",str(report))[-1].replace("%","")
    
    if match:
        rating = float(match)
        if rating >= 90 and rating <= 100:
            colour = '44cc11'
        elif rating < 90 and rating >= 70:
            colour = 'f89406'
        elif rating >= 20 and rating < 70:
            colour = 'b94947'
        else:
            colour = '9d9d9d'
    return (rating, colour)


def get_pylint_rating_and_colour(report):
    colour = '9d9d9d'
    rating = 0
    match = re.search("Your code has been rated at (.+?)/10", str(report))
    if match:
        rating = float(match.group(1))
        if rating >= 6 and rating <= 10:
            colour = '44cc11'
        elif rating < 6 and rating >= 3:
            colour = 'f89406'
        elif rating >= -5 and rating < 3:
            colour = 'b94947'
        else:
            colour = '9d9d9d'
    return (rating, colour)

def save_file(filename, contents):
    """Save a file anywhere"""
    print(filename)
    ensure_path(os.path.dirname(filename))
    with open(filename, 'w') as thefile:
        thefile.write(str(contents))


def ensure_path(path):
    """Make sure the path exists, creating it if need be"""
    if not os.path.exists(path):
        os.makedirs(path)


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.register_blueprint(mainbp)
    return app

app=create_app()

if __name__=="__main__":
    #app = create_app()
    app.run(host='0.0.0.0',port=8787)

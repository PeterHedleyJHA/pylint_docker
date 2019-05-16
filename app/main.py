from __future__ import absolute_import
import os
import re
import logging
import shutil
import zipfile
from flask import Flask, request, Blueprint, current_app

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
    <text x="67" y="15" fill="#010101" fill-opacity=".3">{0}</text>
    <text x="67" y="14">{0}</text>
  </g>
</svg>
"""

mainbp = Blueprint('main', __name__)


@mainbp.route('/pylint-reports', methods=['POST'])
def handle_report_post():
    if request.form['pull-req']=='false':
        report, report_folder, badge_folder = parse_args('pylint-report')
        html_report = get_report('pylint-html-report')
        save_report('pylint_report.html', report_folder, html_report.decode("utf-8"))

        rating = get_match("Your code has been rated at (.+?)/10", report)
        rating_dividers = [-5, 3, 6, 10]
        colour = get_colour(float(rating), rating_dividers)

        save_badge(rating, colour, "pylint", badge_folder)
    return 'OK\n', 200

@mainbp.route('/coverage-reports', methods=['POST'])
def handle_coverage_report_post():
    if request.form['pull-req']=='false':
        report, report_folder, badge_folder = parse_args('coverage-report')
        report = report.decode("utf-8").replace("\n","<br>")

        html_report = request.files['coverage-html-report-zip']
        html_report.save('./cov_report.zip')
        
        unzip_folder('./cov_report.zip', report_folder)
        
        rating = get_match(r"\d+(?=%)", report)
        rating_dividers = [20, 70, 90, 100]
        colour = get_colour(int(rating), rating_dividers)

        save_badge(rating, colour, "cov", badge_folder)
    return 'OK\n', 200

@mainbp.route('/readme-reports', methods=['POST'])
def handle_readme_report_post():
    if request.form['pull-req']=='false':
        report, report_folder, badge_folder = parse_args('readme-report')        
        save_report('readme_score.html', report_folder, report.decode("utf-8"))

        rating = get_match(r"(?<=README Coverage: )\d+(?=%)", report)
        rating_dividers = [10, 35, 60, 100]
        colour = get_colour(int(rating), rating_dividers)

        save_badge(rating, colour, "readme", badge_folder)
    return 'OK\n', 200

def parse_args(report_arg):
    current_app.logger.info('handling POST on /reports')
    git_slug = get_slug()
    git_branch = get_branch()
    output_folder = current_app.config['OUTPUT_FOLDER']
    report_folder = os.path.join(output_folder, "reports", git_slug, git_branch)
    badge_folder = os.path.join(output_folder, "badges", git_slug, git_branch)

    report = get_report(report_arg)
    return report, report_folder, badge_folder

def save_badge(rating, colour, badge_name, output_folder):
    output_badge = os.path.join(output_folder, badge_name + '.svg')
    current_app.logger.info('saving badge to '+ output_badge)
    save_file(output_badge, BADGE_TEMPLATE.format(rating, badge_name, colour))

def get_slug():
    if 'git-slug' in request.form:
        git_slug = str(request.form['git-slug']).split("/")[-1]
    else:
        raise ValueError('invalid repository slug')
    return git_slug

def get_branch():
    if 'git-branch' in request.form:
        git_branch = request.form['git-branch']
    else:
        raise ValueError('invalid repository branch')
    return git_branch

def get_report(report_name):
    if report_name in request.files:
        report = request.files[report_name].read()
    else:
        raise ValueError('No Report Specified')
    return report

def save_report(report_name, output_folder, report):
    output_report = os.path.join(output_folder, report_name)
    current_app.logger.info('saving report to '+output_report)
    save_file(output_report, report)

def unzip_folder(path_to, dir_to):
    zip_ref = zipfile.ZipFile(path_to, 'r')
    zip_ref.extractall(dir_to)
    zip_ref.close()
        
def get_match(pattern, report):
    match = re.findall(pattern, str(report))[-1]
    if not match:
        raise ValueError('could not find match in report')
    return match

def get_colour(rating, divs):
    if rating < divs[0]:
        return 'b94947'
    if rating < divs[1]:
        return 'f89406'
    if rating < divs[2]:
        return '76af34'
    return '44cc11'

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

app = create_app()

if __name__ == "__main__":
    #app = create_app()
    app.run(host='0.0.0.0', port=8787)

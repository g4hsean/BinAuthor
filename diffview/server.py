import os

import argparse
from flask import Flask, render_template, request

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=dir_path, template_folder=dir_path)
print dir_path


@app.route("/diffview")
def diffview():
    l_file = request.args.get('left')
    r_file = request.args.get('right')
    l_lines = [line.rstrip('\n') for line in open(os.path.join(dir_path, l_file))]
    r_lines = [line.rstrip('\n') for line in open(os.path.join(dir_path, r_file))]

    return render_template("templ.html",
                           left_lines=l_lines,
                           right_lines=r_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="echo server port", type=int, default=5000)
    args = parser.parse_args()
    app.run(port=args.port)

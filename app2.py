# !//usr/bin/env/python
# -*- coding:utf-8 -*-
from flask import Flask, render_template, redirect, request
from os.path import join, dirname, abspath, exists

import personalityinsights2 as personalityinsights2

#Flaskの起動
app = Flask(__name__, static_folder='app/static')
@app.route("/")
def show_toppage():
    return render_template('generic.html')

@app.route('/result', methods=['POST'])
def add_user():
    title = "分析結果"
    content = request.form['content']
    if not content:
        return redirect('/')
    result, result_img = personalityinsights2.main(content)
    return render_template('generic.html', title=title, result=result, result_img=result_img)

# # if __name__ == "__main__":
# app.run(host="localhost")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import bs4


def get_jobs_list(jobs_URL):
    result = []
    page_number = 1
    ses = requests.Session()
    while True:
        resp = ses.get('{}?page={}'.format(jobs_URL, page_number)).json()
        if len(resp) == 0:
            break
        else:
            for job in resp:
                result.append(
                    (job['number'], job['title'], job['html_url']))
            page_number += 1
    return result


def get_jobs_details(url):
    ses = requests.Session()
    resp = ses.get(url)
    tree = bs4.BeautifulSoup(resp.text, 'lxml')
    description = tree.find_all('tr', attrs={'class': 'd-block'})[0].text
    return description


def get_posts_list(url):
    posts = []
    ses = requests.Session()
    resp = ses.get(url)
    tree = bs4.BeautifulSoup(resp.text, 'lxml')
    data = tree.select('h3 > a')
    for item in data:
        title = item.text
        post_url = item.get('href')
        posts.append((title, post_url))
    for title, post_url in posts:
        if not post_url.startswith('https://www.familug.org'):
            posts.remove((title, post_url))
    return posts


app = Flask(__name__)

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database_jobs&posts.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Job(db.Model):
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(250), primary_key=True)
    url = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Job {self.title}>'


class Post_python(db.Model):
    label = db.Column(db.String(250))
    title = db.Column(db.String(250), primary_key=True)
    url = db.Column(db.String(250))

    def __repr__(self):
        return f'<Post_python {self.title}>'


class Post_command(db.Model):
    label = db.Column(db.String(250))
    title = db.Column(db.String(250), primary_key=True)
    url = db.Column(db.String(250))

    def __repr__(self):
        return f'<Post_command {self.title}>'


class Post_sysadmin(db.Model):
    label = db.Column(db.String(250))
    title = db.Column(db.String(250), primary_key=True)
    url = db.Column(db.String(250))

    def __repr__(self):
        return f'<Post_sysadmin {self.title}>'


class Post_latest(db.Model):
    label = db.Column(db.String(250))
    title = db.Column(db.String(250), primary_key=True)
    url = db.Column(db.String(250))

    def __repr__(self):
        return f'<Post_latest {self.title}>'


@app.route("/")
def index():
    jobs_URL = 'https://api.github.com/repos/awesome-jobs/vietnam/issues'
    data = get_jobs_list(jobs_URL)
    for number, title, html_url in data:
        description = get_jobs_details(html_url)
        newjob = Job(number=number, title=title,
                     url=html_url, description=description)
        db.session.add(newjob)
        db.session.commit()

    python_posts_URL = [
        ('Python', 'https://www.familug.org/search/label/Python?max-results=1000')
    ]
    for label, url in python_posts_URL:
        posts_list = get_posts_list(url)
        for title, post_url in posts_list:
            python_posts = Post_python(label=label, title=title, url=post_url)
            db.session.add(python_posts)
            db.session.commit()

    command_posts_URL = [
        ('Command', 'https://www.familug.org/search/label/Command?max-results=1000')
    ]
    for label, url in command_posts_URL:
        posts_list = get_posts_list(url)
        for title, post_url in posts_list:
            command_posts = Post_command(
                label=label, title=title, url=post_url)
            db.session.add(command_posts)
            db.session.commit()

    sysadmin_posts_URL = [
        ('Sysadmin', 'https://www.familug.org/search/label/sysadmin?max-results=1000'),
    ]
    for label, url in sysadmin_posts_URL:
        posts_list = get_posts_list(url)
        for title, post_url in posts_list:
            sysadmin_posts = Post_sysadmin(
                label=label, title=title, url=post_url)
            db.session.add(sysadmin_posts)
            db.session.commit()

    latest_posts_URL = [
        ('Latest', 'https://www.familug.org/search?max-results=10')]
    for label, url in latest_posts_URL:
        posts_list = get_posts_list(url)
        for title, post_url in posts_list:
            latest_posts = Post_latest(
                label=label, title=title, url=post_url)
            db.session.add(latest_posts)
            db.session.commit()

    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/movies")
def movies():
    return render_template("movies.html")


@app.route("/chinese")
def chinese():
    return render_template("chinese.html")


@app.route("/awesomejobs")
def awesome():
    all_jobs = db.session.query(Job).all()
    return render_template("awesomejobs.html", jobs=all_jobs)


@app.route("/familug-latest")
def latest():
    latest_posts = db.session.query(Post_latest).all()
    return render_template("latest.html", all_latest_posts=latest_posts)


@app.route("/familug-python")
def python():
    python_posts = db.session.query(Post_python).all()
    return render_template("python.html", all_python_posts=python_posts)


@app.route("/familug-sysadmin")
def sysadmin():
    sysadmin_posts = db.session.query(Post_sysadmin).all()
    return render_template("sysadmin.html", all_sysadmin_posts=sysadmin_posts)


@app.route("/familug-command")
def command():
    command_posts = db.session.query(Post_command).all()
    return render_template("command.html", all_command_posts=command_posts)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

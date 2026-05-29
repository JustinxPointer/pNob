from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from mysql_util import MysqlUti
from passlib.hash import sha256_crypt
from functools import wraps
from forms import ArticleForm, RegisterForm
import time

app = Flask(__name__)
#首页
@app.route('/')
def index():
    return render_template('home.html')
# 关于
@app.route('/about')
def about():
    return render_template('about.html')
# 笔记列表
@app.route('/articles')
def articles():
    database=MysqlUti()
    sql = 'SELECT * FROM articles ORDER BY create_date LIMIT 5'
    articles = database.fetchall(sql)
    if articles:
        return render_template('articles.html',
                               articles=articles)
    else:
        msg = '暂无笔记'
        return render_template('articles.html', msg=msg)
# 笔记详情
@app.route('/article/<string:id>')
def article(id):
    database = MysqlUti()
    sql = "SELECT * FROM articles WHERE id='s'" %id
    article = database.fetchone(sql)
    return render_template('article.html', article=article)
# 用户注册
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))

        with MysqlUti() as database:
            sql = 'INSERT INTO users(email, username, password) VALUES ("%s", "%s", "%s")' %(email, username, password)
            database.insert(sql)
            flash('您已注册成功，请先登录', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)
# 用户登陆
@app.route('/login', methods=['GET', 'POST'])
def login():
    if "logged_in" in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        sql = "SELECT * FROM users WHERE USERNAME='%s'" %username
        with MysqlUti() as database:
            result = database.fetchone(sql)
            if result:
                password = result['password']
                if sha256_crypt.verify(password_candidate, password):
                    session['logged_in'] = True
                    session['username'] = username
                    flash('登录成功！', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = '用户名和密码不匹配'
                    return render_template('login.html', error=error)
            else:
                error = '用户不存在'
                return render_template('login.html', error=error)
    return render_template('login.html')
# 如果用户已经登录
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('无权访问，请重新登录', 'danger')
            return render_template('login.html')
    return wrap
# 退出
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('您已成功退出', 'success')
    return redirect(url_for('login'))
# 控制台
@app.route('/dashboard')
@is_logged_in
def dashboard():
    with MysqlUti() as database:
        sql = "SELECT * FROM articles WHERE author = '%s' ORDER BY create_date DESC" %session['username']
        result = database.fetchall(sql)
        if result:
            return render_template('dashboard.html', articles=result)
        else:
            msg = '暂无笔记信息'
            return render_template('dashboard.html', msg=msg)
# 添加笔记
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['username']
        create_date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        with MysqlUti() as database:
            sql = "INSERT INTO articles (title, content, author, create_date)\
         VALUES('%s', '%s', '%s', '%s')" %(title, content, author, create_date)
            database.insert(sql)
            flash('创建成功', 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)
# 编辑笔记
@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    with MysqlUti() as database:
        fetch_sql = "SELECT * FROM articles WHERE id = '%s' and author = '%s'"%(id, session['username'])
        article = database.fetchone(fetch_sql)
        if not article:
            flash('ID错误', 'danger')
            return redirect(url_for('dashboard'))
        form = ArticleForm(request.form)
        if request.method == 'POST' and form.validate():
            title = request.form['title']
            content = request.form['content']
            update_sql = "UPDATE articles SET title='%s' , content='%s'\
         WHERE id='%s' and author='%s'"%(title, content, id, session['username'])
            database.update(update_sql)
            flash('更改成功', 'success')
            return redirect(url_for('dashboard'))
    form.title.data = article['title']
    form.content.data = article['content']
    return render_template('edit_article.html', form=form)
# 删除笔记
@app.route('/delete_article/<string:id>', methods = ['POST'])
@is_logged_in
def delete_article(id):
    with MysqlUti() as database:
        sql = "DELETE FROM articles WHERE id='%s' and author='%s'"%(id, session['username'])
        database.delete(sql)
        flash('删除成功', 'success')
        return redirect(url_for('dashboard'))
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)






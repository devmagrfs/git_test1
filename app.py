from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.dessert

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sign_up/check_id_dup', methods=['POST'])
def check_id_dup():
        username_receive = request.form['username_give']
        exists = bool(db.users.find_one({"username": username_receive}))
        return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_email_dup', methods=['POST'])
def check_email_dup():
    useremail_receive = request.form['useremail_give']
    exists = bool(db.users.find_one({"useremail": useremail_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    useremail_receive = request.form['email_give']
    # 패스워드 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "useremail": useremail_receive                              # 이메일

    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # print(username_receive, password_receive)

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 매칭되는 id와 pw값이 있는지 확인
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    # 만약 result가 있다면
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        ## decode 방법이 jwt.decode(token, secret key, algorithms으로 바뀜)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        dessert_name_receive = request.form["dessert_name_give"]
        action_receive = request.form["action_give"]

        # 이름 같은 사람 구분은 어떻게?
        doc = {
            "dessert_name": dessert_name_receive,
            "username": user_info["username"],
        }

        if action_receive == "like":
            db.likes.insert_one(doc)
            db.dessert.update_one({'dessert_name': dessert_name_receive}, {'$inc': {'count_like': 1}})
        else:
            db.likes.delete_one(doc)
            db.dessert.update_one({'dessert_name': dessert_name_receive}, {'$inc': {'count_like': -1}})

        count = db.dessert.count_documents({"dessert_name": dessert_name_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/', methods=['GET'])
def home():
    dessert_list = list(db.dessert.find({}, {'_id': False}))
    return render_template("index.html", dessert_list=dessert_list)

if __name__ == '__main__':
    app.run('0.0.0.0', port=4444, debug=True)
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId

# 비밀번호 암호화에 이용되는 패키지
import jwt, datetime, hashlib

SECRET_KEY='WETUBE'

app = Flask(__name__)
client = MongoClient('mongodb+srv://chunws:test@chunws.w8zkw9b.mongodb.net/?retryWrites=true&w=majority')
db = client.chunws

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    
    elif request.method == "POST":
        user_id = request.form['user_id']
        password = request.form['password']
        
        # 비밀번호 암호화
        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # 아이디와 비밀번호로 유저 찾기
        result_user = db.wetube_user.find_one({"user_id" : user_id, "password" : pw_hash})
 
        # 등록된 유저가 맞는 경우, find_one 함수로 인해 아이디 / 비밀번호 일치 여부 모두 확인됨
        if result_user is not None:
            # payload : 유저 정보와 만료 시간을 담고 있는 정보 
            # 시크릿키 : payload 값을 알기 위한 키
            # JWt = payload + 시크릿키 ?
            payload = {
                'id' : user_id,
                # 만료 시간, UTC 기준 로그인한 시간 + 500초간 유효함
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=500)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            print('여기까지옴')
            return render_template('/index.html', token = token, user_id = user_id)
        # 등록된 유저가 아닌 경우
        else:
            return render_template('login.html', message = "아이디 / 비밀번호를 확인하세요")
    
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # register.html 파일에서 보내온 회원가입 정보 수신
        userid_receive = request.form['user_id']
        nickname_receive = request.form['nick_name']
        password1_receive = request.form['password1']
        password2_receive = request.form['password2']
        
        # 비밀번호 암호화 
        pw1_hash = hashlib.sha256(password1_receive.encode('utf-8')).hexdigest()
        
        # db에서 동일한 id 존재 여부 확인
        userid_duplication = db.wetube_user.find_one({"user_id" : userid_receive})
                
        # 동일 id 존재할 때
        if userid_duplication is not None:
            msg = "이미 존재하는 아이디 입니다."
            return render_template('register.html', message = msg)
        
        # 비밀번호, 확인용 비밀번호가 일치하지 않을때
        elif password1_receive != password2_receive:
            msg = "비밀번호가 서로 일치하지 않습니다."
            return render_template('register.html', message = msg)
        
        # 모든 조건을 만족할 때
        else:
            create_user = {
                "user_id" : userid_receive,
                "nick_name" : nickname_receive,
                "password" : pw1_hash
            }
            
            db.wetube_user.insert_one(create_user)
            msg = "회원가입 성공!"
            
            return redirect(url_for('/login.html', message=msg))
    
    # GET 요청시 회원가입 페이지로 유도
    else:
        return render_template('register.html')
if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='web/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


# 사용자 데이터베이스 모델
class User_DB(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    number = db.Column(db.Integer)  # HTML 폼의 number 필드에 대응
    # join_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # channel_names = db.Column(db.String, default='[]', nullable=False)
    # fixes_keyword = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.telegram_id}>'


# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()


@app.route('/channel')
def channel():
    return render_template('channel.html')


@app.route('/recommend_channel')
def recommend_channel():
    return render_template('recommend_channel.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        telegram_id = request.form['content']  # HTML의 name="content"가 telegram_id에 해당
        number = request.form['number']  # number 필드 추가

        # 새 사용자 객체 생성 (올바른 필드명 사용)
        new_user = User_DB(telegram_id=telegram_id, number=number)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            # 오류 발생 시 자세한 오류 메시지 표시
            return f"저장 실패: {str(e)}"
    else:
        # GET 요청 처리
        users = User_DB.query.all()  # 모든 사용자 목록 가져오기
        return render_template('index.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
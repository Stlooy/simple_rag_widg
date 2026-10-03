from flask import Flask, jsonify ,render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rag_pipeline import answer_question

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

db = SQLAlchemy(app)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    # Process the question and generate an answer
    
    data = request.get_json(silent=True) or {}
    
    question = str(data.get("question", "")).strip()
    
    
    if not question:
            return jsonify(error="Please type a message."), 400
        
    
    answer = answer_question(question)
    db.session.add(Message(role='user', content=question))
    db.session.add(Message(role='assistant', content=answer))    
    db.session.commit()

    return jsonify({'answer': answer})




if __name__ == '__main__':
    app.run(debug=True)


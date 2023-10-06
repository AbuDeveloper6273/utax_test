from flask import Flask, request, jsonify
from models import *
#
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)  # Используйте Flask-Ngrok с вашим приложением


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ----------------------------------------------------------------------------------------->

# main page
@app.route('/')
def index():
    return "hello"


# get all data
@app.route('/data')
def data():
    users = Users.query.all()
    user_list = []

    for user in users:
        user_dict = {
            "name": user.name,
            "surname": user.surname,
            "phone": user.phone
        }
        user_list.append(user_dict)

    return jsonify(user_list)


# add user
@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']

        user = Users(name=name, surname=surname, phone=phone)

        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "Пользователь успешно добавлен"})
        except:
            return jsonify({"message": "Ошибка"})
    else:
        return "user"


# delete user
@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get(user_id)  # Найдите пользователя по его идентификатору

    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Пользователь успешно удален"}), 200  # 200 OK


#add test
# Создание нового теста и вопросов с ответами и вариантами
@app.route('/create_test_with_questions', methods=['POST'])
def create_test_with_questions():
    try:
        data = request.get_json()
        test_title = data.get('test_title')  # Заголовок теста из JSON-данных
        questions = data.get('questions')  # Список вопросов из JSON-данных

        # Создайте новый тест
        new_test = Test(title=test_title)

        db.session.add(new_test)
        db.session.commit()

        for question_data in questions:
            question_text = question_data.get('question_text')  # Текст вопроса из JSON-данных
            options_data = question_data.get('options')  # Список вариантов ответов из JSON-данных
            correct_option_text = question_data.get('correct_option')  # Текст правильного ответа из JSON-данных

            # Создайте новый вопрос и свяжите его с тестом
            new_question = Question(text=question_text, test_id=new_test.id)

            db.session.add(new_question)
            db.session.commit()

            for option_text in options_data:
                # Создайте новый вариант ответа для вопроса
                new_option = Option(text=option_text, question_id=new_question.id)

                # Установите, является ли этот вариант ответа правильным
                if option_text == correct_option_text:
                    new_option.is_correct = True

                db.session.add(new_option)

        db.session.commit()

        return jsonify({"message": "Новый тест с вопросами и ответами успешно создан"}), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Внутренняя ошибка сервера

#add question ->id
@app.route('/add_questions_with_answers_to_test/<int:test_id>', methods=['POST'])
def add_questions_with_answers_to_test(test_id):
    try:
        data = request.get_json()
        questions = data.get('questions')  # Список вопросов из JSON-данных

        # Предполагается, что у вас есть модель Test и Question, и они связаны отношением
        test = Test.query.get(test_id)

        if test is not None:
            for question_data in questions:
                question_text = question_data.get('question_text')  # Текст вопроса из JSON-данных
                options_data = question_data.get('options')  # Список вариантов ответов из JSON-данных
                correct_option_text = question_data.get('correct_option')  # Текст правильного ответа из JSON-данных

                # Создайте новый вопрос и свяжите его с тестом
                new_question = Question(text=question_text, test_id=test_id)

                db.session.add(new_question)
                db.session.commit()

                for option_text in options_data:
                    # Создайте новый вариант ответа для вопроса
                    new_option = Option(text=option_text, question_id=new_question.id)

                    # Установите, является ли этот вариант ответа правильным
                    if option_text == correct_option_text:
                        new_option.is_correct = True

                    db.session.add(new_option)

            db.session.commit()

            return jsonify({"message": "Новые вопросы с ответами успешно добавлены к тесту"}), 201  # 201 Created
        else:
            return jsonify({"message": "Тест не найден"}), 404  # 404 Тест не найден

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Внутренняя ошибка сервера


#get all test from id
@app.route('/get_test/<int:test_id>', methods=['GET'])
def get_test(test_id):
    try:
        test = Test.query.get(test_id)  # Предполагается, что у вас есть модель Test

        if test is not None:
            # Преобразуем данные теста и связанные с ним данные в словарь
            test_data = {
                "id": test.id,
                "title": test.title,
                "questions": []
            }

            for question in test.questions:
                question_data = {
                    "id": question.id,
                    "text": question.text,
                    "options": []
                }

                for option in question.options:
                    option_data = {
                        "id": option.id,
                        "text": option.text,
                        "is_correct": option.is_correct
                    }
                    question_data["options"].append(option_data)

                test_data["questions"].append(question_data)

            return jsonify(test_data)
        else:
            return jsonify({"message": "Тест не найден"}), 404  # 404 Тест не найден

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Внутренняя ошибка сервера


#get all tests
@app.route('/get_all_tests', methods=['GET'])
def get_all_tests():
    try:
        tests = Test.query.all()  # Assuming you have a Test model

        if tests:
            test_data_list = []

            for test in tests:
                test_data = {
                    "id": test.id,
                    "title": test.title,
                    "questions": []
                }

                for question in test.questions:
                    question_data = {
                        "id": question.id,
                        "text": question.text,
                        "options": []
                    }

                    for option in question.options:
                        option_data = {
                            "id": option.id,
                            "text": option.text,
                            "is_correct": option.is_correct
                        }
                        question_data["options"].append(option_data)

                    test_data["questions"].append(question_data)

                test_data_list.append(test_data)

            return jsonify(test_data_list)
        else:
            return jsonify({"message": "Тесты не найдены"}), 404  # 404 Тесты не найдены

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Внутренняя ошибка сервера



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)

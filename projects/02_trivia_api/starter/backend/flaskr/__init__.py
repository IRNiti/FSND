# Note: implementation follows format provided by Caryn McCarthy
# in API Development and Documentation course

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# method to format questions by page numbers
# if a page number is given that would require more items than available
# in the database in order to display something, throw a 404 error
# questions are formatted as a dictionary
# to make them easily convertible to JSON to send as a response
def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    if(len(questions) < start):
        abort(404)
    else:
        requested_questions = questions[start:end]
        formatted_questions = [question.format() for question in requested_questions]
        return formatted_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # get all questions
    # returns paginated questions,
    # all categories formatted as a dictionary with id: type as key-value pairs,
    # number of total questions,
    # if there are any questions in the database,
    # return the category of the first question as the current category
    @app.route('/questions')
    def get_questions():

        questions = Question.query.all()
        categories = Category.query.all()
        formatted_questions = paginate_questions(request, questions)
        formatted_categories = {}
        current_category = None

        if (len(questions) > 0):
            current_category = Category.query.get(questions[0].category).format()

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': formatted_categories,
            'currentCategory': current_category
        })

    # get all categories
    # returns all categories formatted as a dictionary with id: type as key-value pairs
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    # get all questions for a given category
    # return paginated questions,
    # number of total questions,
    # the given category formatted as a dictionary as defined in models.py
    #
    # in Github requirements and rubric this is specified as POST request,
    # but in the frontend it is defined as GET, so following the frontend
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(422)
        else:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(questions),
                'currentCategory': category.format()
              })

    # delete a given question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(422)
            else:
                question.delete()
                return jsonify({
                    'success': True
                })
        except:
            abort(422)

    # method to search questions or to create a new question
    #
    # the arguments passed in the request body will determine which operation is executed
    # if a searchTerm is given, then all questions that contain it as a case insensitive substring will be returned
    # returns paginated questions, number of questions and category of first question if any are found
    #
    # otherwise, the method expects the following arguments: question, answer, difficulty, category
    # both question and answer arguments are required in this case
    # if they are missing or empty, a 400 error will be thrown
    # return id of created question
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term is not None:
            search_term = '%'+search_term+'%'
            questions = Question.query.filter(Question.question.ilike(search_term)).all()
            formatted_questions = paginate_questions(request, questions)
            current_category = None

            if (len(questions) > 0):
                current_category = Category.query.get(questions[0].category).format()

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(questions),
                'currentCategory': current_category
            })
        else:
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            if(answer == '' or question == '' or answer is None or question is None):
                abort(400)

            try:
                new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                new_question.insert()

                return jsonify({
                    'success': True,
                    'question_id': new_question.id
                })
            except:
                abort(422)

    # get question to play quiz
    # expects previous_questions as a list of ids and an optional quiz_category as a dictionary as defined in models.py
    # returns a question that is not in the previous_questions list
    # if no category is provided, returns a question for any category
    # if no previous_questions are provided, will throw a 422 error so at least an empty list of questions is expected
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)
            next_question = None

            if (category is None or category['id'] == 0):
                next_question = Question.query.filter(~Question.id.in_(previous_questions)).first()
            else:
                next_question = Question.query.filter_by(category=category['id']).filter(~Question.id.in_(previous_questions)).first()
            if next_question is not None:
                next_question = next_question.format()

            return jsonify({
                'success': True,
                'question': next_question
            })
        except:
            abort(422)

    # Error Handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Could not process request'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(500)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    return app

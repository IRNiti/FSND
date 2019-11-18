import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  #CORS(app)
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
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

  #TODO: error handling for missing categories
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

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    if question is None:
      abort(422)
    else:
      question.delete()
      return jsonify({
        'success': True
        })

  #TODO: error handling for search
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

      if(answer == '' or question == ''):
        abort(422)

      try:
        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        new_question.insert()

        return jsonify({
          'success': True,
          'question_id': new_question.id
          })
      except:
        abort(422)


  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions', None)
      category = body.get('quiz_category', None)
      next_question = None
      print(category)

      if (category['id'] == 0 ):
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



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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
  
  return app

    
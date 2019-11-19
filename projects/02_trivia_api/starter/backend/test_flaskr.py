# Note: implementation follows format provided by Caryn McCarthy
# in API Development and Documentation course

import os
import unittest
import json
import datetime
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # test for GET /questions
    def test_succesful_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])

    # test for GET /questions
    def test_failed_get_questions_nonexistent_page(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # test for GET /categories
    def test_succesful_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    # test for GET /categories
    def test_get_categories_with_wrong_method(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    # test for GET /categories/<int:category_id>/questions
    def test_succesful_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    # test for GET /categories/<int:category_id>/questions
    def test_get_questions_by_category_nonexistent_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Could not process request')

    # test for GET /categories/<int:category_id>/questions
    def test_get_questions_by_category_nonexistent_page(self):
        res = self.client().get('/categories/1/questions?page=10')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # test for DELETE /questions
    def test_succesful_delete_question(self):
        to_delete = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete('/questions/'+str(to_delete.id))
        data = json.loads(res.data)
        question = Question.query.filter_by(id=to_delete.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    # test for DELETE /questions
    def test_delete_nonexistent_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Could not process request')

    # test for POST /questions
    def test_succesful_create_question(self):
        new_question = 'Test Question'+str(datetime.datetime.now())
        body = {
            'question': new_question,
            'answer': 'Test Answer',
            'difficulty': 4,
            'category': 1
        }
        res = self.client().post('/questions', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        inserted_question = Question.query.filter_by(question=new_question).first()
        self.assertEqual(data['question_id'], inserted_question.id)

    # test for POST /questions
    def test_create_question_without_answer(self):
        new_question = 'Test Question'+str(datetime.datetime.now())
        body = {
            'question': new_question,
            'answer': '',
            'difficulty': 4,
            'category': 1
        }
        res = self.client().post('/questions', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    # test for POST /questions
    def test_succesful_search_question(self):
        search_term = 'world cup'
        body = {
            'searchTerm': search_term
        }
        res = self.client().post('/questions', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['currentCategory'])
        self.assertEqual(data['totalQuestions'], 2)
        self.assertEqual(len(data['questions']), 2)

    # test for POST /questions
    def test_search_question_without_results(self):
        search_term = 'salesforce'
        body = {
            'searchTerm': search_term
        }
        res = self.client().post('/questions', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['questions'])
        self.assertEqual(data['currentCategory'], None)
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(len(data['questions']), 0)

    # test for POST /questions
    def test_search_questions_nonexistent_page(self):
        search_term = 'world cup'
        body = {
            'searchTerm': search_term
        }
        res = self.client().post('/questions?page=100', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    # test for POST /quizzes
    def test_succesful_return_quiz_question(self):
        category = Category.query.first()
        input_category = {
            'type': category.type,
            'id': category.id
        }
        questions = Question.query.filter_by(category=category.id).all()
        previous_questions = [question.id for question in questions[1:]]
        body = {
            'previous_questions': previous_questions,
            'quiz_category': input_category
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question'], questions[0].format())

    # test for POST /quizzes
    def test_failed_return_quiz_question_wrong_format_input_category(self):
        category = Category.query.first()
        input_category = category.id
        questions = Question.query.filter_by(category=category.id).all()
        previous_questions = [question.id for question in questions[1:]]
        body = {
            'previous_questions': previous_questions,
            'quiz_category': input_category
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Could not process request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_succesful_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])

    def test_failed_get_questions_nonexistent_page(self):
        res = self.client().get('/questions?page=100')
        self.assertEqual(res.status_code, 404)

    def test_succesful_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    #TODO: write failed test for get categories
    def test_failed_get_categories(self):
        res = self.client().get('/categories')

    def test_succesful_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_get_questions_by_category_nonexistent_category(self):
        res = self.client().get('/categories/100/questions')
        self.assertEqual(res.status_code, 422)

    def test_succesful_delete_question(self):
        to_delete = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete('/questions/'+str(to_delete.id))
        self.assertEqual(res.status_code, 200)

    def test_delete_nonexistent_question(self):
        res = self.client().delete('/questions/100')
        self.assertEqual(res.status_code, 422)

    def test_succesful_create_question(self):
        new_question = 'Test Question'+str(datetime.datetime.now())
        res = self.client().post('/questions', json={'question': new_question, 'answer': 'Test Answer', 'difficulty': 4, 'category': 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        inserted_question = Question.query.filter_by(question=new_question).first()
        self.assertEqual(data['question_id'], inserted_question.id)

    #TODO write error test for create question



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
# Full Stack API Final Project

## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a  webpage to manage the trivia app and play the game. The API built here helps users interact with the database which stores the trivia questions as well as their associated categories giving them the ability to retrieve, create, delete, as well as search questions based on key words.

## Getting Started

### Pre-requisites and Local Development

This project uses Python3 and Flask for the backend and Node for the frontend. See the README files in the [backend](./backend) and [frontend](./frontend) directories respectively for instructions on how to install dependencies and how to run the application. As a general note, run the backend server first and then start the frontend. 

## API Reference

### Getting Started

- Base URL: The application is currently only running locally, so navigate to [http://127.0.0.1:3000](http://127.0.0.1:3000) to view it in the browser. As a side note, the backend is hosted at [http://127.0.0.1:5000](http://127.0.0.1:5000) and this is the URL that should be used when testing endpoints with either Postman or curl.

- Authentication: There is no need to authenticate and API keys are not necessary in order to make requests to the server in this version of the application.

### Error Handling

Errors are returned as JSON objects in the following format

```
{
    'success': False,
    'error': 404,
    'message': 'Not found'
}
```

The following error codes can be returned by the application along with the associated error message

- 400: Bad request
- 404: Not found
- 422: Could not process request
- 405: Method not allowed
- 500: Internal Server Error

### Endpoints

#### GET /questions

Returns a list of trivia questions, the success value (True or False), the total number of questions, a dictionary containing all the categories organized as key-value pairs of id-type, as well as the current category. The result is paginated with 10 questions displayed per page and an optional argument for the page number can be passed in the request (ex: GET /questions?page=3). If a page number that exceeds the number of available entries is provided, a 404 error will be thrown.

##### Example

curl http://127.0.0.1:5000/questions

```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "currentCategory": {
    "id": 4, 
    "type": "History"
  }, 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 3, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 3, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }, 
    {
      "answer": "Agra", 
      "category": 3, 
      "difficulty": 2, 
      "id": 15, 
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ], 
  "success": true, 
  "total_questions": 21
}
```

curl http://127.0.0.1:5000/questions?page=100

```
{
  "error": 404, 
  "message": "Not found", 
  "success": false
}
```

#### POST /questions

This endpoint will have different behaviour depending on the body that is sent with the request. 

- Search questions: When providing a search term, the response will return a list of questions that contain the search term as a substring, as well as the success value (True or False), the total number of questions matching the search term and the current category. The list of questions is also paginated with 10 entries displayed per page and an optional page number can be provided as an argument in the request (ex POST /questions?page=2). If a page number that exceeds the number of available entries is provided, a 404 error will be thrown. The search term is case insensitive. Arguments to be provided in the request body: searchTerm.


##### Example

curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"world cup"}' http://127.0.0.1:5000/questions

```
{
  "currentCategory": {
    "id": 6, 
    "type": "Sports"
  }, 
  "questions": [
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ], 
  "success": true, 
  "totalQuestions": 2
}

```

curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"world cup"}' http://127.0.0.1:5000/questions?page=10

```
{
  "error": 404, 
  "message": "Not found", 
  "success": false
}
```

- Create question: When providing a question, answer, category and difficulty in the request body, a new question will be inserted into the database with the entered values. If the operation is succesful, the success value (True or False) as well as the id of the new question will be returned. As a note, the question and answer fields are mandatory so leaving one blank will throw a 400 error. Arguments to be provided in the request body: question, answer, difficulty, category.

##### Example

curl -X POST -H "Content-Type: application/json" -d '{"question":"Who wrote Harry Potter", "answer":"J K Rowling", "difficulty":1, "category":5}' http://127.0.0.1:5000/questions

```
{
  "question_id": 30, 
  "success": true
}
```

curl -X POST -H "Content-Type: application/json" -d '{"question":"Who wrote Harry Potter", "difficulty":1, "category":5}' http://127.0.0.1:5000/questions

```
{
  "error": 400, 
  "message": "Bad request", 
  "success": false
}
```

#### DELETE /questions/<int:question_id>

Deletes the question with the id passed in as an argument. If the given id does not correspond to a question that exists in the database, a 422 error will be thrown. On the other hand, if the operation is succesful, the success value will be returned in the response.

##### Example

curl -X DELETE http://127.0.0.1:5000/questions/31

```
{
  "success": true
}
```

curl -X DELETE http://127.0.0.1:5000/questions/100

```
{
  "error": 422, 
  "message": "Could not process request", 
  "success": false
}
```

#### GET /categories

Returns a dictionary with all the categories structured with the ids as the keys and the category type as the values. Also returns the success value.

##### Example

curl http://127.0.0.1:5000/categories

```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true
}
```

#### GET /categories/<int:category_id>/questions

Returns a list of questions associated to the category id given as the argument, as well as the total number of questions in the given category, the success value (True or False) and the current category. The questions will be paginated with 10 entries per page and an optional page number can be provided as an argument in the request (ex GET /categories/1/questions?page=2). If the provided category id does not correspond to a value existing in the database, a 422 error will be thrown. If a page number that exceeds the number of available entries is provided, a 404 error will be thrown.

##### Example

curl http://127.0.0.1:5000/categories/4/questions

```
{
  "currentCategory": {
    "id": 4, 
    "type": "History"
  }, 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Scarab", 
      "category": 4, 
      "difficulty": 4, 
      "id": 23, 
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ], 
  "success": true, 
  "totalQuestions": 3
}
```

curl http://127.0.0.1:5000/categories/20/questions

```
{
  "error": 422, 
  "message": "Could not process request", 
  "success": false
}
```

curl http://127.0.0.1:5000/categories/4/questions?page=5

```
{
  "error": 404, 
  "message": "Not found", 
  "success": false
}
```

#### POST /quizzes

Returns the next question that a user will need to play a quiz. This endpoint expects a request body which will provide a list of ids for previous questions already answered as well as an optional category. If the category is provided, only questions for that category are returned. Otherwise, questions from any category will be returned. The response will contain the success value as well as the next question to be played. If a previous question argument is not provided, a 422 error will be thrown. In order to avoid this behaviour, at least an empty list should be provided as an argument (see examples). Arguments to be provided in the request body: previous_questions, quiz_category.

##### Example

curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[16,17], "quiz_category":{"type":"Art", "id":2}}' http://127.0.0.1:5000/quizzes

```
{
  "question": {
    "answer": "One", 
    "category": 2, 
    "difficulty": 4, 
    "id": 18, 
    "question": "How many paintings did Van Gogh sell in his lifetime?"
  }, 
  "success": true
}
```

curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[16,17]}' http://127.0.0.1:5000/quizzes

```
{
  "question": {
    "answer": "Muhammad Ali", 
    "category": 4, 
    "difficulty": 1, 
    "id": 9, 
    "question": "What boxer's original name is Cassius Clay?"
  }, 
  "success": true
}
```

curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[]}' http://127.0.0.1:5000/quizzes

```
{
  "question": {
    "answer": "Muhammad Ali", 
    "category": 4, 
    "difficulty": 1, 
    "id": 9, 
    "question": "What boxer's original name is Cassius Clay?"
  }, 
  "success": true
}
```

curl -X POST http://127.0.0.1:5000/quizzes

```
{
  "error": 422, 
  "message": "Could not process request", 
  "success": false
}
```


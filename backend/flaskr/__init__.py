import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * 10
  end = start + 10
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    
    result = {
      'success': True,
      'categories': {category.id: category.type for category in categories},
    }
    return jsonify(result)


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

  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection) 
    
    if len(current_questions) == 0:
      abort(404)
    
    categories = Category.query.order_by(Category.type).all()

    return jsonify({
      'success':True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': {category.id: category.type for category in categories},
      'current_category': None,
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_questions(id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        })

    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_questions():
    
    # get request body
    body = request.get_json()

    # get question info
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
      })

    except:
      abort(422)


 # '''
 # @TODO: 
 # Create a POST endpoint to get questions based on a search term. 
 # It should return any questions for whom the search term 
 # is a substring of the question. 

 # TEST: Search by any phrase. The questions list will update to include 
 # only question that include that string within their question. 
 # Try using the word "title" to start. 
 # '''

  @app.route('/questions/search', methods=['POST']) 
  def search_questions():
    
    # get request body
    body = request.get_json

    #see if search text is there
    if (body.get('searchText')):
      search_text = body.get('searchText')

      # query the database with search text
      selection = Question.query.filter(Question.question.ilike(f'%(search_text)%').all())

      # error for no result
      if len(selection==0):
        abort(404)

      # return question if successful
      current_questions = paginate_questions(request, selection)

      # return list of questions
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
      })


#'''
#  @TODO: 
#  Create a GET endpoint to get questions based on category. 

#  TEST: In the "List" tab / main screen, clicking on one of the 
#  categories in the left column will cause only questions of that 
#  category to be shown. 
#  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_by_category(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()
    
    #if category not found
    if category is None:
        abort(404)

    # return questions by category
    selection = Question.query.filter_by(category=category.id).all()
    current_questions = paginate_questions(request, selection)

    return jsonify({
      'success': True,
      'category': category.id,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
    })

#  '''
#  @TODO: 
#  Create a POST endpoint to get questions to play the quiz. 
#  This endpoint should take category and previous question parameters 
#  and return a random questions within the given category, 
#  if provided, and that is not one of the previous questions. 

#  TEST: In the "Play" tab, after a user selects "All" or a category,
#  one question at a time is displayed, the user is allowed to answer
#  and shown whether they were correct or not. 
#  '''

  @app.route('/quiz', methods=['POST'])
  def get_random_questions():

    # get request body
    body = request.get_json

    # get previous questions
    previous = body.get('previous_questions')

    # get question category
    category = body.get('category')
 
    # throw error if no category and no previous questions
    if not ('previous_questions' in body and ('category') in body):
      abort(422)

    # get questions on selecting all, all questions or questions by category
    if (category['id'] == 0):
      possible_questions = Question.query.all()

    else:
      questions = Question.query.filter_by([Category.id == category_id]).all()

    # get new question
    def get_new_question():
      if len(questions) > 0:
        return questions[random.randrange(0, len(questions), 1)]
      else:
        None

    # make sure not to include previous questions
    def check_if_previous(question):
      played = False
      for q in previous:
        if (q == question_id):
          played = True
      return played

    # get a question
    question = get_new_question()

    # check if it's been used and find one that hasn't been
    while (check_if_previous(question)):
      question = get_new_question()

    # return result
    return jsonify({
      'success': True,
      'question': question.format(),
    })

#  '''
#  @TODO: 
#  Create error handlers for all expected errors 
#  including 404 and 422. 
#  '''
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request"
      }), 400

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed"
      }), 405


  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Internal server error"
      }), 500

  return app   
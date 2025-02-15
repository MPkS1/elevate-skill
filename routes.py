from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Wing, Quiz, Question, QuizResponse, QuizAnswer, Learning, Notification
from datetime import datetime
from urllib.parse import urlparse

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Input validation
        if not username or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('login'))
        
        if not username.replace('_', '').replace('-', '').isalnum():
            flash('Invalid username format', 'danger')
            return redirect(url_for('login'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('login'))
        
        app.logger.info(f"Login attempt for username: {username}")
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user is None:
                app.logger.warning(f"No user found with username: {username}")
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))
            
            if not user.check_password(password):
                app.logger.warning(f"Invalid password for username: {username}")
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))
            
            # Successful login
            login_user(user, remember=True)
            app.logger.info(f"Successful login for username: {username}")
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to the page user tried to access or dashboard
            next_page = request.args.get('next')
            if next_page and urlparse(next_page).netloc == '':
                return redirect(next_page)
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    try:
        username = current_user.username
        logout_user()
        app.logger.info(f"User {username} logged out successfully")
        flash('You have been logged out successfully.', 'success')
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
        flash('An error occurred during logout.', 'warning')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        wings = Wing.query.all()
        total_users = User.query.count()
        total_learnings = Learning.query.count()
        total_quizzes = Quiz.query.count()
        wing_stats = []
        for wing in wings:
            stats = {
                'wing': wing,
                'members': User.query.filter_by(wing_id=wing.id).count(),
                'learnings': Learning.query.join(User).filter(User.wing_id==wing.id).count(),
                'quizzes': Quiz.query.filter_by(wing_id=wing.id).count()
            }
            wing_stats.append(stats)
        return render_template('admin_dashboard.html', 
                           wings=wings,
                           total_users=total_users,
                           total_learnings=total_learnings,
                           total_quizzes=total_quizzes,
                           wing_stats=wing_stats)
    
    elif current_user.role == 'wing_head':
        wing = current_user.wing
        members = User.query.filter_by(wing_id=wing.id, role='member').all()
        quizzes = Quiz.query.filter_by(wing_id=wing.id).all()
        member_stats = []
        for member in members:
            learnings = Learning.query.filter_by(user_id=member.id).all()
            quiz_responses = QuizResponse.query.filter_by(user_id=member.id).all()
            stats = {
                'username': member.username,
                'learnings': learnings,
                'quiz_responses': quiz_responses,
                'learning_count': len(learnings),
                'quiz_count': len(quiz_responses),
                'avg_quiz_score': sum([r.score for r in quiz_responses]) / len(quiz_responses) if quiz_responses else 0
            }
            member_stats.append(stats)
        return render_template('wing_head_dashboard.html', 
                           wing=wing,
                           members=members,
                           quizzes=quizzes,
                           member_stats=member_stats)
    
    else:  # member
        wing = Wing.query.get(current_user.wing_id)
        # Get quiz responses for the current user
        user_responses = QuizResponse.query.filter_by(user_id=current_user.id).all()
        taken_quiz_ids = [r.quiz_id for r in user_responses]
        
        # Get available and completed quizzes
        available_quizzes = Quiz.query.filter_by(wing_id=current_user.wing_id).filter(~Quiz.id.in_(taken_quiz_ids if taken_quiz_ids else [-1])).all()
        completed_quizzes = Quiz.query.filter_by(wing_id=current_user.wing_id).filter(Quiz.id.in_(taken_quiz_ids if taken_quiz_ids else [-1])).all()
        
        # Get today's learnings
        today = datetime.utcnow().date()
        learnings = Learning.query.filter_by(user_id=current_user.id)\
            .filter(db.func.date(Learning.created_at) == today)\
            .order_by(Learning.created_at.desc()).all()
            
        # Get recent notifications
        notifications = Notification.query.filter_by(wing_id=current_user.wing_id)\
            .order_by(Notification.created_at.desc())\
            .limit(5).all()
            
        return render_template('member_dashboard.html',
                           wing=wing,
                           available_quizzes=available_quizzes,
                           completed_quizzes=completed_quizzes,
                           learnings=learnings,
                           notifications=notifications)

@app.route('/create_wing', methods=['POST'])
@login_required
def create_wing():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    name = request.form.get('name')
    if not name:
        flash('Wing name is required', 'error')
        return redirect(url_for('dashboard'))
    
    wing = Wing(name=name)
    db.session.add(wing)
    db.session.commit()
    
    flash('Wing created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_quiz', methods=['POST'])
@login_required
def create_quiz():
    if current_user.role not in ['admin', 'wing_head']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    title = request.form.get('title')
    questions = request.form.getlist('questions[]')
    answers = request.form.getlist('answers[]')
    
    if not title or not questions or not answers or len(questions) != len(answers):
        flash('Please fill in all fields correctly', 'error')
        return redirect(url_for('dashboard'))
    
    quiz = Quiz(
        title=title,
        wing_id=current_user.wing_id,
        created_at=datetime.utcnow()
    )
    db.session.add(quiz)
    db.session.commit()
    
    for q, a in zip(questions, answers):
        question = Question(
            quiz_id=quiz.id,
            question_text=q,
            correct_answer=a
        )
        db.session.add(question)
    
    db.session.commit()
    flash('Quiz created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/take_quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already taken this quiz
    existing_response = QuizResponse.query.filter_by(
        quiz_id=quiz_id,
        user_id=current_user.id
    ).first()
    
    if existing_response:
        flash('You have already taken this quiz', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('take_quiz.html', quiz=quiz)

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already taken this quiz
    existing_response = QuizResponse.query.filter_by(
        quiz_id=quiz_id,
        user_id=current_user.id
    ).first()
    
    if existing_response:
        flash('You have already taken this quiz', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate score
    total_questions = len(quiz.questions)
    correct_answers = 0
    
    response = QuizResponse(
        quiz_id=quiz_id,
        user_id=current_user.id,
        submitted_at=datetime.utcnow()
    )
    db.session.add(response)
    db.session.commit()
    
    for question in quiz.questions:
        answer_text = request.form.get(f'answer_{question.id}')
        is_correct = answer_text.lower().strip() == question.correct_answer.lower().strip()
        if is_correct:
            correct_answers += 1
        
        answer = QuizAnswer(
            response_id=response.id,
            question_id=question.id,
            answer_text=answer_text,
            is_correct=is_correct
        )
        db.session.add(answer)
    
    score = int((correct_answers / total_questions) * 100)
    response.score = score
    db.session.commit()
    
    flash(f'Quiz submitted successfully! Your score: {score}%', 'success')
    return redirect(url_for('dashboard'))

@app.route('/quiz_stats/<int:quiz_id>')
@login_required
def quiz_stats(quiz_id):
    if current_user.role not in ['admin', 'wing_head']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
        
    quiz = Quiz.query.get_or_404(quiz_id)
    responses = QuizResponse.query.filter_by(quiz_id=quiz_id).all()
    
    stats = {
        'total_responses': len(responses),
        'avg_score': sum([r.score for r in responses]) / len(responses) if responses else 0,
        'responses': []
    }
    
    for response in responses:
        user = User.query.get(response.user_id)
        response_stats = {
            'username': user.username,
            'score': response.score,
            'submitted_at': response.submitted_at,
            'answers': []
        }
        for answer in response.answers:
            question = Question.query.get(answer.question_id)
            response_stats['answers'].append({
                'question': question.question_text,
                'user_answer': answer.answer_text,
                'correct_answer': question.correct_answer,
                'is_correct': answer.is_correct
            })
        stats['responses'].append(response_stats)
    
    return render_template('quiz_stats.html', quiz=quiz, stats=stats)

@app.route('/wing_stats/<int:wing_id>')
@login_required
def wing_stats(wing_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    wing = Wing.query.get_or_404(wing_id)
    members = User.query.filter_by(wing_id=wing_id).all()
    
    member_stats = []
    for member in members:
        if member.role == 'member':
            stats = {
                'username': member.username,
                'learnings': Learning.query.filter_by(user_id=member.id).count(),
                'quiz_responses': QuizResponse.query.filter_by(user_id=member.id).count(),
                'avg_score': db.session.query(db.func.avg(QuizResponse.score)).filter_by(user_id=member.id).scalar() or 0
            }
            member_stats.append(stats)
    
    return render_template('wing_stats.html', 
                         wing=wing,
                         member_stats=member_stats)

@app.route('/share_learning', methods=['POST'])
@login_required
def share_learning():
    content = request.form.get('content')
    if not content:
        flash('Learning content is required', 'error')
        return redirect(url_for('dashboard'))
    
    learning = Learning(
        content=content,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(learning)
    db.session.commit()
    
    flash('Learning shared successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_admin', methods=['POST'])
@login_required
def create_admin():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('dashboard'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('dashboard'))
    
    admin = User(
        username=username,
        role='admin'
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    
    flash('Admin user created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_wing_head', methods=['POST'])
@login_required
def create_wing_head():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    wing_id = request.form.get('wing_id')
    
    if not all([username, password, wing_id]):
        flash('All fields are required', 'error')
        return redirect(url_for('dashboard'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('dashboard'))
    
    wing_head = User(
        username=username,
        role='wing_head',
        wing_id=wing_id
    )
    wing_head.set_password(password)
    db.session.add(wing_head)
    db.session.commit()
    
    flash('Wing Head created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_member', methods=['POST'])
@login_required
def create_member():
    if current_user.role not in ['admin', 'wing_head']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    wing_id = request.form.get('wing_id') if current_user.role == 'admin' else current_user.wing_id
    
    if not all([username, password, wing_id]):
        flash('Username and password are required', 'error')
        return redirect(url_for('dashboard'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('dashboard'))
    
    member = User(
        username=username,
        role='member',
        wing_id=wing_id
    )
    member.set_password(password)
    db.session.add(member)
    db.session.commit()
    
    flash('Member created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/send_notification', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'wing_head':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    content = request.form.get('content')
    if not content:
        flash('Message content is required', 'error')
        return redirect(url_for('dashboard'))
    
    # Store notification in the database
    try:
        notification = Notification(
            content=content,
            wing_id=current_user.wing_id,
            sender_id=current_user.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        flash('Notification sent successfully!', 'success')
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        db.session.rollback()
        flash('Error sending notification', 'error')
    
    return redirect(url_for('dashboard'))

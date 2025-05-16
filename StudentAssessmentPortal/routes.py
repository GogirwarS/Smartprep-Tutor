import json
import os
from flask import render_template, url_for, flash, redirect, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

from app import app, db
from forms import RegistrationForm, LoginForm
from models import User, Assessment, TopicPerformance


@app.route('/')
def index():
    if current_user.is_authenticated:
        # Check if user has completed initial assessment
        initial_assessment = Assessment.query.filter_by(
            user_id=current_user.id, 
            assessment_type='initial'
        ).first()
        
        if initial_assessment and initial_assessment.completed:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('assessment', assessment_type='initial'))
    
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            branch=form.branch.data,
            year_of_passing=form.year_of_passing.data,
            age=form.age.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Check if initial assessment is completed
    initial_assessment = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='initial'
    ).first()
    
    if not initial_assessment or not initial_assessment.completed:
        flash('You need to complete the initial assessment first.', 'warning')
        return redirect(url_for('assessment', assessment_type='initial'))
    
    # Get overall scores for each category
    quant_score = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='quant'
    ).order_by(Assessment.date_taken.desc()).first()
    
    verbal_score = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='verbal'
    ).order_by(Assessment.date_taken.desc()).first()
    
    reasoning_score = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='reasoning'
    ).order_by(Assessment.date_taken.desc()).first()
    
    # Get topic performances
    quant_topics = TopicPerformance.query.filter_by(
        user_id=current_user.id,
        category='quant'
    ).all()
    
    verbal_topics = TopicPerformance.query.filter_by(
        user_id=current_user.id,
        category='verbal'
    ).all()
    
    reasoning_topics = TopicPerformance.query.filter_by(
        user_id=current_user.id,
        category='reasoning'
    ).all()
    
    # Get historical assessments for progress tracking
    assessments_history = Assessment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assessment.date_taken).all()
    
    return render_template(
        'dashboard.html',
        quant_score=quant_score,
        verbal_score=verbal_score,
        reasoning_score=reasoning_score,
        quant_topics=quant_topics,
        verbal_topics=verbal_topics,
        reasoning_topics=reasoning_topics,
        assessments_history=assessments_history
    )


@app.route('/assessment/<assessment_type>')
@login_required
def assessment(assessment_type):
    # If trying to access a specific assessment without completing initial
    if assessment_type != 'initial':
        initial_assessment = Assessment.query.filter_by(
            user_id=current_user.id, 
            assessment_type='initial'
        ).first()
        
        if not initial_assessment or not initial_assessment.completed:
            flash('You need to complete the initial assessment first.', 'warning')
            return redirect(url_for('assessment', assessment_type='initial'))
    
    assessment_title = {
        'initial': 'Initial Assessment',
        'quant': 'Quantitative Assessment',
        'verbal': 'Verbal Assessment',
        'reasoning': 'Reasoning Assessment'
    }
    
    return render_template(
        'assessment.html', 
        assessment_type=assessment_type,
        assessment_title=assessment_title.get(assessment_type, 'Assessment')
    )


@app.route('/api/tab-switch', methods=['POST'])
@login_required
def tab_switch():
    data = request.json
    tab_switch_count = data.get('count', 0)
    session['tab_switch_count'] = tab_switch_count
    
    # Auto-submit after 3 tab switches
    if tab_switch_count >= 3:
        return jsonify({'status': 'exceeded', 'message': 'Tab switch limit exceeded!'})
    
    return jsonify({'status': 'ok', 'count': tab_switch_count})


@app.route('/api/save-assessment-results', methods=['POST'])
@login_required
def save_assessment_results():
    data = request.json
    assessment_type = data.get('assessment_type')
    quantScore = data.get('quantScore', 0)
    verbalScore = data.get('verbalScore', 0)
    reasoningScore = data.get('reasoningScore', 0)
    totalScore = data.get('totalScore', 0)
    
    quantStats = data.get('quantStats', {})
    verbalStats = data.get('verbalStats', {})
    reasoningStats = data.get('reasoningStats', {})
    
    print(f"Saving assessment results - Type: {assessment_type}")
    print(f"Scores - Quant: {quantScore}, Verbal: {verbalScore}, Reasoning: {reasoningScore}, Total: {totalScore}")
    print(f"Quant Topics: {list(quantStats.keys())}")
    print(f"Verbal Topics: {list(verbalStats.keys())}")
    print(f"Reasoning Topics: {list(reasoningStats.keys())}")
    
    # Create or update assessment record
    if assessment_type == 'initial':
        # Store each section's score separately
        quant_assessment = Assessment(
            user_id=current_user.id,
            assessment_type='quant',
            score=quantScore,
            max_score=20,
            topics_data=json.dumps(quantStats),
            completed=True
        )
        
        verbal_assessment = Assessment(
            user_id=current_user.id,
            assessment_type='verbal',
            score=verbalScore,
            max_score=25,
            topics_data=json.dumps(verbalStats),
            completed=True
        )
        
        reasoning_assessment = Assessment(
            user_id=current_user.id,
            assessment_type='reasoning',
            score=reasoningScore,
            max_score=20,
            topics_data=json.dumps(reasoningStats),
            completed=True
        )
        
        # Store combined score as initial assessment
        initial_assessment = Assessment(
            user_id=current_user.id,
            assessment_type='initial',
            score=totalScore,
            max_score=65,
            completed=True
        )
        
        db.session.add(quant_assessment)
        db.session.add(verbal_assessment)
        db.session.add(reasoning_assessment)
        db.session.add(initial_assessment)
    else:
        # Store individual assessment
        score = 0
        max_score = 0
        topics_data = '{}'
        
        if assessment_type == 'quant':
            score = quantScore
            max_score = 20
            topics_data = json.dumps(quantStats)
        elif assessment_type == 'verbal':
            score = verbalScore
            max_score = 25
            topics_data = json.dumps(verbalStats)
        elif assessment_type == 'reasoning':
            score = reasoningScore
            max_score = 20
            topics_data = json.dumps(reasoningStats)
        
        assessment = Assessment(
            user_id=current_user.id,
            assessment_type=assessment_type,
            score=score,
            max_score=max_score,
            topics_data=topics_data,
            completed=True
        )
        
        db.session.add(assessment)
    
    # Update topic performance data
    
    # Process quantitative topics
    for topic, stats in quantStats.items():
        existing_topic = TopicPerformance.query.filter_by(
            user_id=current_user.id,
            category='quant',
            topic=topic
        ).first()
        
        if existing_topic:
            existing_topic.correct = stats['correct']
            existing_topic.total = stats['total']
            existing_topic.last_updated = datetime.utcnow()
        else:
            new_topic = TopicPerformance(
                user_id=current_user.id,
                category='quant',
                topic=topic,
                correct=stats['correct'],
                total=stats['total']
            )
            db.session.add(new_topic)
    
    # Process verbal topics
    for topic, stats in verbalStats.items():
        existing_topic = TopicPerformance.query.filter_by(
            user_id=current_user.id,
            category='verbal',
            topic=topic
        ).first()
        
        if existing_topic:
            existing_topic.correct = stats['correct']
            existing_topic.total = stats['total']
            existing_topic.last_updated = datetime.utcnow()
        else:
            new_topic = TopicPerformance(
                user_id=current_user.id,
                category='verbal',
                topic=topic,
                correct=stats['correct'],
                total=stats['total']
            )
            db.session.add(new_topic)
    
    # Process reasoning topics
    for topic, stats in reasoningStats.items():
        existing_topic = TopicPerformance.query.filter_by(
            user_id=current_user.id,
            category='reasoning',
            topic=topic
        ).first()
        
        if existing_topic:
            existing_topic.correct = stats['correct']
            existing_topic.total = stats['total']
            existing_topic.last_updated = datetime.utcnow()
        else:
            new_topic = TopicPerformance(
                user_id=current_user.id,
                category='reasoning',
                topic=topic,
                correct=stats['correct'],
                total=stats['total']
            )
            db.session.add(new_topic)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Assessment results saved successfully!'
    })


@app.route('/api/get-assessment-data', methods=['GET'])
@login_required
def get_assessment_data():
    assessment_history = {}
    categories = ['quant', 'verbal', 'reasoning']
    
    for category in categories:
        assessments = Assessment.query.filter_by(
            user_id=current_user.id,
            assessment_type=category
        ).order_by(Assessment.date_taken).all()
        
        assessment_history[category] = [
            {
                'date': assessment.date_taken.strftime('%Y-%m-%d'),
                'score': assessment.score,
                'max_score': assessment.max_score
            }
            for assessment in assessments
        ]
    
    # Get topic performance
    topic_performance = {}
    for category in categories:
        topics = TopicPerformance.query.filter_by(
            user_id=current_user.id,
            category=category
        ).all()
        
        topic_performance[category] = [
            {
                'topic': topic.topic,
                'correct': topic.correct,
                'total': topic.total,
                'percentage': round((topic.correct / topic.total) * 100) if topic.total > 0 else 0
            }
            for topic in topics
        ]
    
    return jsonify({
        'history': assessment_history,
        'topics': topic_performance
    })


@app.route('/category/<category>')
@login_required
def category_chapters(category):
    """Display all chapters for a specific category"""
    # Check if initial assessment is completed
    initial_assessment = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='initial'
    ).first()
    
    if not initial_assessment or not initial_assessment.completed:
        flash('You need to complete the initial assessment first.', 'warning')
        return redirect(url_for('assessment', assessment_type='initial'))
    
    category_names = {
        'quant': 'Quantitative',
        'verbal': 'Verbal',
        'reasoning': 'Reasoning'
    }
    
    # Get chapters for the category
    # In a real application, this would come from a database
    chapters = []
    
    if category == 'quant':
        chapters = [
            {'id': 'number-systems', 'name': 'Number Systems', 'level': 'Basic', 'description': 'Learn about integers, decimals, fractions and more'},
            {'id': 'algebra', 'name': 'Algebra', 'level': 'Intermediate', 'description': 'Equations, inequalities, and algebraic expressions'},
            {'id': 'geometry', 'name': 'Geometry', 'level': 'Intermediate', 'description': 'Shapes, angles, areas, volumes and more'}
        ]
    elif category == 'verbal':
        chapters = [
            {'id': 'reading-comprehension', 'name': 'Reading Comprehension', 'level': 'All Levels', 'description': 'Understand and analyze written passages'},
            {'id': 'vocabulary', 'name': 'Vocabulary', 'level': 'All Levels', 'description': 'Word meanings, synonyms, antonyms and more'},
            {'id': 'grammar', 'name': 'Grammar', 'level': 'All Levels', 'description': 'Sentence construction, parts of speech, and more'}
        ]
    elif category == 'reasoning':
        chapters = [
            {'id': 'logical-reasoning', 'name': 'Logical Reasoning', 'level': 'All Levels', 'description': 'Deductive and inductive reasoning'},
            {'id': 'pattern-recognition', 'name': 'Pattern Recognition', 'level': 'All Levels', 'description': 'Identify patterns in sequences and figures'},
            {'id': 'puzzles', 'name': 'Puzzles', 'level': 'All Levels', 'description': 'Brain teasers and logical problems'}
        ]
    
    return render_template(
        'category.html',
        category=category,
        category_name=category_names.get(category, 'Unknown'),
        chapters=chapters
    )


@app.route('/chapter/<category>/<chapter>')
@login_required
def chapter_content(category, chapter):
    """Display content for a specific chapter"""
    # Check if initial assessment is completed
    initial_assessment = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='initial'
    ).first()
    
    if not initial_assessment or not initial_assessment.completed:
        flash('You need to complete the initial assessment first.', 'warning')
        return redirect(url_for('assessment', assessment_type='initial'))
    
    category_names = {
        'quant': 'Quantitative',
        'verbal': 'Verbal',
        'reasoning': 'Reasoning'
    }
    
    # Get chapter information
    chapter_info = None
    
    # In a real application, this would come from a database
    if category == 'quant':
        if chapter == 'number-systems':
            chapter_info = {'name': 'Number Systems', 'level': 'Basic', 'description': 'Learn about integers, decimals, fractions and more'}
        elif chapter == 'algebra':
            chapter_info = {'name': 'Algebra', 'level': 'Intermediate', 'description': 'Equations, inequalities, and algebraic expressions'}
        elif chapter == 'geometry':
            chapter_info = {'name': 'Geometry', 'level': 'Intermediate', 'description': 'Shapes, angles, areas, volumes and more'}
    
    elif category == 'verbal':
        if chapter == 'reading-comprehension':
            chapter_info = {'name': 'Reading Comprehension', 'level': 'All Levels', 'description': 'Understand and analyze written passages'}
        elif chapter == 'vocabulary':
            chapter_info = {'name': 'Vocabulary', 'level': 'All Levels', 'description': 'Word meanings, synonyms, antonyms and more'}
        elif chapter == 'grammar':
            chapter_info = {'name': 'Grammar', 'level': 'All Levels', 'description': 'Sentence construction, parts of speech, and more'}
    
    elif category == 'reasoning':
        if chapter == 'logical-reasoning':
            chapter_info = {'name': 'Logical Reasoning', 'level': 'All Levels', 'description': 'Deductive and inductive reasoning'}
        elif chapter == 'pattern-recognition':
            chapter_info = {'name': 'Pattern Recognition', 'level': 'All Levels', 'description': 'Identify patterns in sequences and figures'}
        elif chapter == 'puzzles':
            chapter_info = {'name': 'Puzzles', 'level': 'All Levels', 'description': 'Brain teasers and logical problems'}
    
    if not chapter_info:
        flash('Chapter not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template(
        'chapter.html',
        category=category,
        category_name=category_names.get(category, 'Unknown'),
        chapter=chapter,
        chapter_info=chapter_info
    )


@app.route('/practice/<category>/<chapter>/<level>')
@login_required
def practice(category, chapter, level):
    """Display practice problems for a specific chapter and level"""
    # Check if initial assessment is completed
    initial_assessment = Assessment.query.filter_by(
        user_id=current_user.id, 
        assessment_type='initial'
    ).first()
    
    if not initial_assessment or not initial_assessment.completed:
        flash('You need to complete the initial assessment first.', 'warning')
        return redirect(url_for('assessment', assessment_type='initial'))
    
    category_names = {
        'quant': 'Quantitative',
        'verbal': 'Verbal',
        'reasoning': 'Reasoning'
    }
    
    level_names = {
        'basic': 'Basic Practice Set',
        'advanced': 'Advanced Practice Set',
        'test': 'Chapter Test'
    }
    
    # Get chapter information
    chapter_info = None
    
    # In a real application, this would come from a database
    if category == 'quant':
        if chapter == 'number-systems':
            chapter_info = {'name': 'Number Systems', 'level': 'Basic', 'description': 'Learn about integers, decimals, fractions and more'}
        elif chapter == 'algebra':
            chapter_info = {'name': 'Algebra', 'level': 'Intermediate', 'description': 'Equations, inequalities, and algebraic expressions'}
        elif chapter == 'geometry':
            chapter_info = {'name': 'Geometry', 'level': 'Intermediate', 'description': 'Shapes, angles, areas, volumes and more'}
    
    elif category == 'verbal':
        if chapter == 'reading-comprehension':
            chapter_info = {'name': 'Reading Comprehension', 'level': 'All Levels', 'description': 'Understand and analyze written passages'}
        elif chapter == 'vocabulary':
            chapter_info = {'name': 'Vocabulary', 'level': 'All Levels', 'description': 'Word meanings, synonyms, antonyms and more'}
        elif chapter == 'grammar':
            chapter_info = {'name': 'Grammar', 'level': 'All Levels', 'description': 'Sentence construction, parts of speech, and more'}
    
    elif category == 'reasoning':
        if chapter == 'logical-reasoning':
            chapter_info = {'name': 'Logical Reasoning', 'level': 'All Levels', 'description': 'Deductive and inductive reasoning'}
        elif chapter == 'pattern-recognition':
            chapter_info = {'name': 'Pattern Recognition', 'level': 'All Levels', 'description': 'Identify patterns in sequences and figures'}
        elif chapter == 'puzzles':
            chapter_info = {'name': 'Puzzles', 'level': 'All Levels', 'description': 'Brain teasers and logical problems'}
    
    if not chapter_info:
        flash('Chapter not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template(
        'practice.html',
        category=category,
        category_name=category_names.get(category, 'Unknown'),
        chapter=chapter,
        chapter_info=chapter_info,
        level=level,
        level_name=level_names.get(level, 'Practice')
    )

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
import os
import tempfile
import subprocess
import json
from datetime import datetime
import secrets
import re
import sys
import latex_generator

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklists.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy(app)

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    phases_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChecklistForm(FlaskForm):
    title = StringField('Checklist Title', default='CHECKLIST')
    subtitle = StringField('Subtitle', default='(Print and laminate for use)')
    submit = SubmitField('Generate PDF')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ChecklistForm()
    if form.validate_on_submit():
        try:
            # Get JSON data from the form
            phases_data = json.loads(request.form.get('phases_data', '[]'))
            app.logger.debug(f"Phases data: {phases_data}")
            
            if not phases_data:
                app.logger.warning("No phases data provided")
                return jsonify({'error': 'No checklist items provided'}), 400
            
            # Generate LaTeX content
            try:
                latex_content = latex_generator.generate_latex(
                    form.title.data,
                    form.subtitle.data,
                    phases_data
                )
                app.logger.debug("LaTeX content generated successfully")
            except Exception as e:
                app.logger.error(f"Error generating LaTeX content: {str(e)}")
                return jsonify({'error': 'Failed to generate LaTeX content'}), 500
            
            # Create temporary directory and generate PDF
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Verify xelatex is installed
                    try:
                        subprocess.run(['xelatex', '--version'], 
                                     check=True, capture_output=True)
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        app.logger.error("XeLaTeX not found or not working")
                        return jsonify({'error': 'XeLaTeX is not installed or not working properly'}), 500
                    
                    # Compile PDF
                    pdf_file = latex_generator.compile_pdf(latex_content, temp_dir)
                    app.logger.debug(f"PDF compiled successfully at {pdf_file}")
                    
                    if not os.path.exists(pdf_file):
                        app.logger.error(f"PDF file not found at {pdf_file}")
                        return jsonify({'error': 'PDF file was not generated'}), 500
                    
                    # Format filename from title
                    filename = form.title.data.strip().lower()
                    filename = re.sub(r'[^a-z0-9]+', '_', filename)
                    filename = re.sub(r'^_+|_+$', '', filename)
                    if not filename:
                        filename = 'checklist'
                    filename = filename[:50] + '.pdf'
                    
                    # Return the PDF
                    try:
                        return send_file(
                            pdf_file,
                            as_attachment=True,
                            download_name=filename,
                            mimetype='application/pdf'
                        )
                    except Exception as e:
                        app.logger.error(f"Error sending file: {str(e)}")
                        return jsonify({'error': 'Failed to send PDF file'}), 500
                        
                except subprocess.CalledProcessError as e:
                    app.logger.error(f"PDF generation failed: {str(e)}")
                    app.logger.error(f"LaTeX output: {e.stdout.decode() if e.stdout else ''}")
                    app.logger.error(f"LaTeX errors: {e.stderr.decode() if e.stderr else ''}")
                    return jsonify({'error': 'Failed to generate PDF. Please check if XeLaTeX is installed correctly.'}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error in PDF generation: {str(e)}")
            app.logger.error(f"Traceback: {sys.exc_info()}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    
    return render_template('index.html', form=form)

@app.route('/save', methods=['POST'])
def save_checklist():
    data = request.get_json()
    
    # Create new checklist
    checklist = Checklist(
        title=data['title'],
        subtitle=data['subtitle'],
        phases_data=json.dumps(data['phases'])
    )
    
    db.session.add(checklist)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'share_url': url_for('view_checklist', checklist_id=checklist.id, _external=True)
    })

@app.route('/checklist/<int:checklist_id>')
def view_checklist(checklist_id):
    checklist = Checklist.query.get_or_404(checklist_id)
    phases = json.loads(checklist.phases_data)
    return render_template('view_checklist.html', checklist=checklist, phases=phases)

@app.route('/checklist/<int:checklist_id>/pdf')
def download_pdf(checklist_id):
    try:
        checklist = Checklist.query.get_or_404(checklist_id)
        
        # Generate LaTeX content
        latex_content = latex_generator.generate_latex(
            checklist.title,
            checklist.subtitle,
            json.loads(checklist.phases_data)
        )
        
        # Create temporary directory and generate PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Compile PDF
                pdf_file = latex_generator.compile_pdf(latex_content, temp_dir)
                
                # Format filename from title
                filename = checklist.title.strip().lower()
                filename = re.sub(r'[^a-z0-9]+', '_', filename)
                filename = re.sub(r'^_+|_+$', '', filename)
                if not filename:
                    filename = 'checklist'
                filename = filename[:50] + '.pdf'
                
                # Return the PDF
                return send_file(pdf_file, as_attachment=True, 
                               download_name=filename)
            except subprocess.CalledProcessError as e:
                app.logger.error(f"PDF generation failed: {str(e)}")
                return jsonify({'error': 'Failed to generate PDF. Please check if XeLaTeX is installed correctly.'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in PDF generation: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 
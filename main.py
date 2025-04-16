import os
import datetime
import argparse
import json
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import questionary
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS






# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Load environment variables for API key
load_dotenv()

# Set up the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# API Endpoints
@app.route('/api/generate-study-plan', methods=['POST'])
def api_create_study_plan():
    data = request.json
    plan = create_study_plan(
        data.get('subject'),
        data.get('exam_date'),
        data.get('knowledge_level'),
        data.get('hours_per_day'),
        data.get('learning_style')
    )
    return jsonify(plan)

@app.route('/api/generate-quiz', methods=['POST'])
def api_generate_quiz():
    data = request.json
    quiz = generate_quiz(
        data.get('subject'),
        data.get('topic'),
        data.get('difficulty')
    )
    return jsonify(quiz)

@app.route('/api/get-feedback', methods=['POST'])
def api_get_feedback():
    data = request.json
    feedback = get_learning_feedback(
        data.get('subject'),
        data.get('topic'),
        data.get('understanding_level')
    )
    return jsonify(feedback)
                                                        



# Load environment variables for API key

# Set up the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

console = Console()

def create_study_plan(subject, exam_date, current_knowledge, time_available, learning_style):
    """
    Generate a customized study plan using Gemini API
    """
    days_until_exam = (datetime.datetime.strptime(exam_date, "%Y-%m-%d") - 
                      datetime.datetime.now()).days
    
    prompt = f"""
    Create a detailed study plan for a student preparing for a {subject} exam on {exam_date} 
    (which is {days_until_exam} days from now).
    
    Student profile:
    - Current knowledge level: {current_knowledge}
    - Available study time: {time_available} hours per day
    - Preferred learning style: {learning_style}
    
    The study plan should include:
    1. A breakdown of key topics to study with priority levels
    2. A daily schedule showing what to study each day
    3. Recommended study resources (books, websites, videos)
    4. Practice test recommendations
    5. Study techniques particularly suited to this subject and the student's learning style
    
    Format the response as a structured JSON with the following keys:
    - "topics": list of topic objects with "name", "priority" (1-5), and "estimated_hours"
    - "daily_schedule": list of day objects with "day", "focus_areas", "tasks", and "duration"
    - "resources": list of resource objects with "name", "type", "url" (if applicable)
    - "practice_tests": list of recommended practice exams
    - "techniques": list of study techniques with descriptions
    
    Make the plan realistic and achievable given the time constraints.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            try:
                plan = json.loads(json_text)
                return plan
            except json.JSONDecodeError:
                # If the API didn't return valid JSON, try to fix common issues
                json_text = json_text.replace("```json", "").replace("```", "")
                try:
                    plan = json.loads(json_text)
                    return plan
                except:
                    console.print("[bold red]Error parsing the study plan. Returning raw response.[/bold red]")
                    return {"raw_response": response_text}
        else:
            return {"raw_response": response_text}
            
    except Exception as e:
        console.print(f"[bold red]Error generating study plan: {str(e)}[/bold red]")
        return None

def generate_quiz(subject, topic, difficulty):
    """
    Generate a quiz on a specific topic using Gemini API
    """
    prompt = f"""
    Create a quiz on the topic "{topic}" for a student studying {subject}.
    
    Quiz details:
    - Difficulty: {difficulty}
    - Format: Multiple choice questions
    - Number of questions: 5
    
    For each question, provide:
    1. The question
    2. 4 possible answers (labeled A, B, C, D)
    3. The correct answer
    4. A brief explanation of why the answer is correct
    
    Format the response as a structured JSON with the following keys:
    - "questions": list of question objects with "question", "options" (list of 4 strings), 
      "correct_answer" (A, B, C, or D), and "explanation"
    
    Ensure the questions test understanding rather than just memorization.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            try:
                quiz = json.loads(json_text)
                return quiz
            except json.JSONDecodeError:
                # If the API didn't return valid JSON, try to fix common issues
                json_text = json_text.replace("```json", "").replace("```", "")
                try:
                    quiz = json.loads(json_text)
                    return quiz
                except:
                    console.print("[bold red]Error parsing the quiz. Returning raw response.[/bold red]")
                    return {"raw_response": response_text}
        else:
            return {"raw_response": response_text}
            
    except Exception as e:
        console.print(f"[bold red]Error generating quiz: {str(e)}[/bold red]")
        return None

def get_learning_feedback(subject, topic, understanding_level):
    """
    Get personalized feedback and additional resources based on understanding level
    """
    prompt = f"""
    Provide personalized learning feedback and recommendations for a student studying {subject}, 
    specifically the topic "{topic}".
    
    Student's self-reported understanding: {understanding_level}/10
    
    Please provide:
    1. An assessment of what concepts the student might be struggling with given their understanding level
    2. 3-5 targeted resources (videos, articles, practice problems) to improve understanding
    3. A suggested approach to review this topic
    4. 2-3 specific exercises that would help reinforce the material
    
    Format the response as a structured JSON with the following keys:
    - "potential_gaps": list of concepts the student might need to focus on
    - "resources": list of resource objects with "name", "type", "description", and "url" (if applicable)
    - "review_strategy": string with suggested review approach
    - "exercises": list of specific exercises with descriptions
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            try:
                feedback = json.loads(json_text)
                return feedback
            except json.JSONDecodeError:
                # If the API didn't return valid JSON, try to fix common issues
                json_text = json_text.replace("```json", "").replace("```", "")
                try:
                    feedback = json.loads(json_text)
                    return feedback
                except:
                    console.print("[bold red]Error parsing the feedback. Returning raw response.[/bold red]")
                    return {"raw_response": response_text}
        else:
            return {"raw_response": response_text}
            
    except Exception as e:
        console.print(f"[bold red]Error generating feedback: {str(e)}[/bold red]")
        return None

def display_study_plan(plan):
    """Display the study plan in a nice format"""
    if "raw_response" in plan:
        console.print(Panel(plan["raw_response"], title="Study Plan (Raw Response)"))
        return

    # Display topics
    console.print(Panel("[bold cyan]Study Plan Generated[/bold cyan]"))
    
    console.print("\n[bold green]Key Topics to Study:[/bold green]")
    topics_table = Table(show_header=True)
    topics_table.add_column("Topic")
    topics_table.add_column("Priority (1-5)")
    topics_table.add_column("Est. Hours")
    
    for topic in plan.get("topics", []):
        topics_table.add_row(
            topic.get("name", ""),
            str(topic.get("priority", "")),
            str(topic.get("estimated_hours", ""))
        )
    
    console.print(topics_table)
    
    # Display daily schedule
    console.print("\n[bold green]Daily Schedule:[/bold green]")
    for day_plan in plan.get("daily_schedule", [])[:7]:  # Show first 7 days
        day = day_plan.get("day", "")
        focus = day_plan.get("focus_areas", "")
        if isinstance(focus, list):
            focus = ", ".join(focus)
        
        tasks = day_plan.get("tasks", [])
        if isinstance(tasks, list):
            tasks = "\n".join([f"• {task}" for task in tasks])
        
        console.print(Panel(
            f"[bold]Focus:[/bold] {focus}\n\n[bold]Tasks:[/bold]\n{tasks}",
            title=f"Day {day} ({day_plan.get('duration', '')} hrs)"
        ))
    
    # Display resources
    console.print("\n[bold green]Recommended Resources:[/bold green]")
    resources_table = Table(show_header=True)
    resources_table.add_column("Name")
    resources_table.add_column("Type")
    resources_table.add_column("URL")
    
    for resource in plan.get("resources", []):
        resources_table.add_row(
            resource.get("name", ""),
            resource.get("type", ""),
            resource.get("url", "N/A")
        )
    
    console.print(resources_table)
    
    # Display study techniques
    console.print("\n[bold green]Recommended Study Techniques:[/bold green]")
    for i, technique in enumerate(plan.get("techniques", []), 1):
        if isinstance(technique, dict) and "name" in technique and "description" in technique:
            console.print(f"[bold]{i}. {technique['name']}[/bold]")
            console.print(f"   {technique['description']}")
        elif isinstance(technique, str):
            console.print(f"[bold]{i}.[/bold] {technique}")

def display_quiz(quiz):
    """Display a quiz in a nice format"""
    if "raw_response" in quiz:
        console.print(Panel(quiz["raw_response"], title="Quiz (Raw Response)"))
        return

    console.print(Panel("[bold cyan]Study Quiz[/bold cyan]"))
    
    correct_answers = []
    user_answers = []
    
    for i, q in enumerate(quiz.get("questions", []), 1):
        console.print(f"\n[bold cyan]Question {i}:[/bold cyan] {q.get('question', '')}\n")
        
        options = q.get("options", [])
        if not options and "A" in q:  # Handle different possible formats
            options = [q.get("A", ""), q.get("B", ""), q.get("C", ""), q.get("D", "")]
        
        for j, option in enumerate(options[:4]):
            letter = chr(65 + j)  # A, B, C, D
            console.print(f"{letter}. {option}")
        
        correct = q.get("correct_answer", "")
        correct_answers.append(correct)
        
        answer = questionary.select(
            "Your answer:",
            choices=["A", "B", "C", "D"]
        ).ask()
        
        user_answers.append(answer)
        
        if answer == correct:
            console.print("[bold green]Correct![/bold green]")
        else:
            console.print(f"[bold red]Incorrect. The correct answer is {correct}.[/bold red]")
        
        console.print(f"[italic]{q.get('explanation', '')}[/italic]\n")
    
    # Calculate score
    score = sum(1 for ua, ca in zip(user_answers, correct_answers) if ua == ca)
    console.print(f"\n[bold]Your score: {score}/{len(correct_answers)}[/bold]")

def display_feedback(feedback):
    """Display learning feedback in a nice format"""
    if "raw_response" in feedback:
        console.print(Panel(feedback["raw_response"], title="Feedback (Raw Response)"))
        return

    console.print(Panel("[bold cyan]Personalized Learning Feedback[/bold cyan]"))
    
    # Display potential knowledge gaps
    console.print("\n[bold yellow]Potential Knowledge Gaps:[/bold yellow]")
    for i, gap in enumerate(feedback.get("potential_gaps", []), 1):
        console.print(f"{i}. {gap}")
    
    # Display resources
    console.print("\n[bold yellow]Recommended Resources:[/bold yellow]")
    for i, resource in enumerate(feedback.get("resources", []), 1):
        if isinstance(resource, dict):
            console.print(f"[bold]{i}. {resource.get('name', '')}[/bold] ({resource.get('type', '')})")
            console.print(f"   {resource.get('description', '')}")
            if resource.get('url'):
                console.print(f"   URL: {resource.get('url')}")
        else:
            console.print(f"{i}. {resource}")
    
    # Display review strategy
    if "review_strategy" in feedback:
        console.print("\n[bold yellow]Suggested Review Strategy:[/bold yellow]")
        console.print(feedback["review_strategy"])
    
    # Display exercises
    console.print("\n[bold yellow]Recommended Exercises:[/bold yellow]")
    for i, exercise in enumerate(feedback.get("exercises", []), 1):
        if isinstance(exercise, dict) and "description" in exercise:
            console.print(f"{i}. {exercise['description']}")
        else:
            console.print(f"{i}. {exercise}")

def save_study_plan(plan, filename="study_plan.json"):
    """Save the study plan to a file"""
    with open(filename, "w") as f:
        json.dump(plan, f, indent=2)
    console.print(f"[bold green]Study plan saved to {filename}[/bold green]")

def interactive_mode():
    """Run the exam preparation trainer in interactive mode"""
    console.print(Panel.fit(
        "[bold cyan]Virtual Exam Preparation Trainer[/bold cyan]\n"
        "Powered by Gemini AI",
        title="Welcome"
    ))
    
    # Collect user information
    subject = questionary.text("What subject are you preparing for?").ask()
    
    exam_date_str = questionary.text(
        "When is your exam? (YYYY-MM-DD)",
        validate=lambda text: True if len(text.split("-")) == 3 else "Please use format YYYY-MM-DD"
    ).ask()
    
    knowledge_level = questionary.select(
        "What is your current knowledge level?",
        choices=["Beginner", "Intermediate", "Advanced"]
    ).ask()
    
    hours_per_day = questionary.text(
        "How many hours can you study per day?",
        validate=lambda text: text.isdigit() and 0 < int(text) < 24
    ).ask()
    
    learning_style = questionary.select(
        "What is your preferred learning style?",
        choices=["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"]
    ).ask()
    
    console.print("[bold]Generating your personalized study plan...[/bold]")
    plan = create_study_plan(subject, exam_date_str, knowledge_level, hours_per_day, learning_style)
    
    if plan:
        display_study_plan(plan)
        
        if questionary.confirm("Would you like to save this study plan to a file?").ask():
            filename = questionary.text("Enter filename (study_plan.json):", default="study_plan.json").ask()
            save_study_plan(plan, filename)
    
    # Offer additional features
    while True:
        action = questionary.select(
            "What would you like to do next?",
            choices=[
                "Generate a practice quiz",
                "Get personalized feedback on a topic",
                "View study plan again",
                "Exit"
            ]
        ).ask()
        
        if action == "Generate a practice quiz":
            topic = questionary.text("Enter the specific topic for the quiz:").ask()
            difficulty = questionary.select(
                "Select difficulty level:",
                choices=["Easy", "Medium", "Hard"]
            ).ask()
            
            console.print("[bold]Generating quiz...[/bold]")
            quiz = generate_quiz(subject, topic, difficulty)
            
            if quiz:
                display_quiz(quiz)
        
        elif action == "Get personalized feedback on a topic":
            topic = questionary.text("Enter the specific topic you want feedback on:").ask()
            understanding = questionary.text(
                "Rate your understanding of this topic (1-10):",
                validate=lambda text: text.isdigit() and 1 <= int(text) <= 10
            ).ask()
            
            console.print("[bold]Generating personalized feedback...[/bold]")
            feedback = get_learning_feedback(subject, topic, understanding)
            
            if feedback:
                display_feedback(feedback)
        
        elif action == "View study plan again":
            display_study_plan(plan)
        
        else:  # Exit
            break
    
    console.print("[bold cyan]Thank you for using the Virtual Exam Preparation Trainer![/bold cyan]")

def main():
    parser = argparse.ArgumentParser(description="Virtual Exam Preparation Trainer")
    parser.add_argument("--subject", help="The subject you are studying")
    parser.add_argument("--exam-date", help="Exam date in YYYY-MM-DD format")
    parser.add_argument("--knowledge", help="Current knowledge level (Beginner/Intermediate/Advanced)")
    parser.add_argument("--hours", help="Hours available for study per day")
    parser.add_argument("--style", help="Preferred learning style")
    parser.add_argument("--save", help="Save study plan to the specified file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive or not (args.subject and args.exam_date):
        interactive_mode()
    else:
        plan = create_study_plan(
            args.subject,
            args.exam_date,
            args.knowledge or "Intermediate",
            args.hours or "2",
            args.style or "Mixed"
        )
        
        if plan:
            display_study_plan(plan)
            
            if args.save:
                save_study_plan(plan, args.save)

if __name__ == '__main__':
    app.run(debug=True)


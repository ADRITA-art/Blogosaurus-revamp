from flask import Blueprint, request, jsonify
from app import db
from app.models.blog import Blog
from app.utils.auth import get_current_user
from flask_jwt_extended import jwt_required
from openai import OpenAI
import os
client = OpenAI()

ai_bp = Blueprint('ai', __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@ai_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_blog():
    topic = request.json.get('topic')
    if not topic:
        return jsonify({"msg": "Topic required"}), 400

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Write a blog on: {topic}"}
        ]
    )
    content = response.choices[0].message.content


    return jsonify({
        "success": True,
        "content": content,
        "title": topic
    })
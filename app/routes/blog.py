from flask import Blueprint, request, jsonify
from app import db
from app.models.blog import Blog
from app.models.tag import Tag
from app.models.user import User
from app.utils.auth import get_current_user
from flask_jwt_extended import jwt_required

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/', methods=['POST'])
@jwt_required()
def create_blog():
    data = request.json
    user = get_current_user()
    tags = []
    for tag_name in data.get('tags', []):
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
        tags.append(tag)
    blog = Blog(title=data['title'], content=data['content'], author=user, tags=tags)
    db.session.add(blog)
    db.session.commit()
    return jsonify({"msg": "Blog created"}), 201

@blog_bp.route('/my', methods=['GET'])
@jwt_required()
def my_blogs():
    user = get_current_user()
    blogs = Blog.query.filter_by(user_id=user.id).all()
    return jsonify([{
        "id": b.id,
        "title": b.title,
        "content": b.content,
        "user_id": b.user_id
    } for b in blogs])

@blog_bp.route('/all', methods=['GET'])
def all_blogs():
    tag = request.args.get('tag')
    if tag:
        tag_obj = Tag.query.filter_by(name=tag).first()
        blogs = tag_obj.blogs if tag_obj else []
    else:
        blogs = Blog.query.all()
    return jsonify([{
        "id": b.id,
        "title": b.title,
        "content": b.content,
        "user_id": b.user_id,
        "author": b.user
    } for b in blogs])

@blog_bp.route('/<int:blog_id>', methods=['GET'])
def get_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return jsonify({
        "id": blog.id,
        "title": blog.title,
        "content": blog.content,
        "user_id": blog.user_id,
        "author": blog.author.username,  # Using the author relationship
        "tags": [tag.name for tag in blog.tags],
        "created_at": blog.created_at.isoformat()
    })

@blog_bp.route('/<int:blog_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_or_delete_blog(blog_id):
    user = get_current_user()
    blog = Blog.query.get_or_404(blog_id)
    if blog.user_id != user.id:
        return jsonify({"msg": "Unauthorized"}), 403

    if request.method == 'PUT':
        data = request.json
        blog.title = data.get('title', blog.title)
        blog.content = data.get('content', blog.content)
        db.session.commit()
        return jsonify({
            "msg": "Blog updated",
            "blog": {
                "id": blog.id,
                "title": blog.title,
                "content": blog.content,
                "user_id": blog.user_id
            }
        })

    db.session.delete(blog)
    db.session.commit()
    return jsonify({"msg": "Blog deleted"})

from flask import render_template, request, Blueprint
from inventory.models import Post

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
    return render_template("posts/post_list.html", posts=posts)

@main.route("/about")
def about():
    return render_template("main/about.html", title="about")
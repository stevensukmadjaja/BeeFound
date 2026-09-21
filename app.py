import json
import os
import uuid

from flask_sqlalchemy import SQLAlchemy

from datetime import (
    datetime,
    timedelta
)

from werkzeug.utils import secure_filename

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask import (

    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    flash

)

app = Flask(__name__)

# ================= SECURITY CONFIG =================

app.config[
    "MAX_CONTENT_LENGTH"
] = 5 * 1024 * 1024

# ================= DATABASE =================

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///beefound.db"
)

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

db = SQLAlchemy(app)

# ================= SECRET KEY =================

app.secret_key = os.urandom(24)

app.permanent_session_lifetime = (
    timedelta(hours=12)
)

# ================= CONFIG =================

UPLOAD_FOLDER = "static/uploads"

ALLOWED_EXTENSIONS = {

    "png",
    "jpg",
    "jpeg",
    "webp"

}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)

# ================= USER MODEL =================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user"
    )

# ================= ITEM MODEL =================

class Item(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False
    )

    contact = db.Column(
        db.String(200),
        nullable=False
    )

    image = db.Column(
        db.String(300)
    )

    owner = db.Column(
        db.String(100),
        nullable=False
    )

    resolved = db.Column(
        db.Boolean,
        default=False
    )

    resolved_time = db.Column(
        db.String(100)
    )

    claimed_by = db.Column(
        db.String(100)
    )

    nim = db.Column(
        db.String(100)
    )

    pickup_time = db.Column(
        db.String(100)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    comments = db.relationship(

    "Comment",

    backref="item",

    lazy=True,

    cascade="all, delete"

)

    # ================= COMMENT MODEL =================

class Comment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("item.id"),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ================= FILE VALIDATION =================

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS

    )

# ================= LOGIN =================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form[
            "username"
        ].strip()

        password = request.form[
            "password"
        ].strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if (

            user

            and

            check_password_hash(
                user.password,
                password
            )

        ):

            session.permanent = True

            session["username"] = (
                user.username
            )

            session["role"] = (
                user.role
            )

            flash(
                "Login successful",
                "success"
            )

            return redirect("/")

        flash(
            "Invalid username or password",
            "error"
        )

        return redirect("/login")

    return render_template("login.html")

# ================= REGISTER =================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        # ================= EMPTY VALIDATION =================

        if not username or not password:

            flash(

                "Username and password are required",

                "error"

            )

            return redirect("/register")

        # ================= USERNAME VALIDATION =================

        if len(username) < 3:

            flash(

                "Username must be at least 3 characters",

                "error"

            )

            return redirect("/register")

        if len(username) > 20:

            flash(

                "Username cannot exceed 20 characters",

                "error"

            )

            return redirect("/register")

        if not username.replace(
            "_",
            ""
        ).isalnum():

            flash(

                "Username can only contain letters, numbers, and underscore",

                "error"

            )

            return redirect("/register")

        # ================= STRONG PASSWORD VALIDATION =================

        if len(password) < 8:

            flash(

                "Password must be at least 8 characters",

                "error"

            )

            return redirect("/register")

        if not any(
            char.isupper()
            for char in password
        ):

            flash(

                "Password must contain uppercase letter",

                "error"

            )

            return redirect("/register")

        if not any(
            char.islower()
            for char in password
        ):

            flash(

                "Password must contain lowercase letter",

                "error"

            )

            return redirect("/register")

        if not any(
            char.isdigit()
            for char in password
        ):

            flash(

                "Password must contain a number",

                "error"

            )

            return redirect("/register")

        special_characters = (
            "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        )

        if not any(
            char in special_characters
            for char in password
        ):

            flash(

                "Password must contain special character",

                "error"

            )

            return redirect("/register")

        # ================= CHECK EXISTING USER =================

        existing_user = (
            User.query.filter_by(
                username=username
            ).first()
        )

        if existing_user:

            flash(

                "Username already exists",

                "error"

            )

            return redirect("/register")

        # ================= HASH PASSWORD =================

        hashed_password = (
            generate_password_hash(
                password
            )
        )

        # ================= CREATE USER =================

        new_user = User(

            username=username,

            password=hashed_password,

            role="user"

        )

        db.session.add(new_user)

        db.session.commit()

        # ================= SUCCESS =================

        flash(

            "Registration successful. Please login.",

            "success"

        )

        return redirect("/login")

    return render_template(
        "register.html"
    )

# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully",
        "success"
    )

    return redirect("/login")

# ================= HOME =================

@app.route("/")
def home():

    if "username" not in session:

        return redirect("/login")

    items = Item.query.order_by(
        Item.created_at.desc()
    ).all()

    active_items = []

    past_24 = []

    now = datetime.now()

    for item in items:

        if (

            item.resolved

            and

            item.resolved_time

        ):

            try:

                resolved_time = (
                    datetime.fromisoformat(
                        item.resolved_time
                    )
                )

                diff = now - resolved_time

                if diff.total_seconds() <= 86400:

                    past_24.append(item)

            except:
                pass

        else:

            active_items.append(item)

    return render_template(

        "index.html",

        items=active_items,

        past_24=past_24,

        role=session.get("role"),

        username=session.get("username")

    )

# ================= ADD ITEM =================

@app.route(
    "/add",
    methods=["POST"]
)
def add_item():

    if "username" not in session:

        return redirect("/login")

    role = session.get("role")

    status = request.form.get(
        "status",
        "Lost"
    )

    if role == "user":

        status = "Lost"

    image_file = request.files.get(
        "image"
    )

    image_filename = ""

    # ================= IMAGE VALIDATION =================

    if (

        image_file

        and

        image_file.filename != ""

    ):

        if not allowed_file(
            image_file.filename
        ):

            flash(

                "Only PNG, JPG, JPEG, and WEBP files are allowed",

                "error"

            )

            return redirect("/")

        filename = secure_filename(
            image_file.filename
        )

        unique_filename = (
            f"{uuid.uuid4()}_{filename}"
        )

        image_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            unique_filename

        )

        image_file.save(image_path)

        image_filename = unique_filename

    # ================= CREATE ITEM =================

    new_item = Item(

        title=request.form.get(
            "title",
            ""
        ),

        description=request.form.get(
            "description",
            ""
        ),

        category=request.form.get(
            "category",
            ""
        ),

        location=request.form.get(
            "location",
            ""
        ),

        status=status,

        contact=request.form.get(
            "contact",
            ""
        ),

        image=image_filename,

        owner=session["username"],

        resolved=False

    )

    db.session.add(new_item)

    db.session.commit()

    flash(

        "Item report submitted successfully",

        "success"

    )

    return redirect("/")

# ================= EDIT ITEM =================

@app.route(
    "/edit/<int:item_id>",
    methods=["POST"]
)
def edit_item(item_id):

    if "username" not in session:

        return redirect("/login")

    item = Item.query.get_or_404(
        item_id
    )

    current_user = session.get(
        "username"
    )

    current_role = session.get(
        "role"
    )

    if (

        item.owner != current_user

        and

        current_role != "admin"

    ):

        flash(
            "Unauthorized action",
            "error"
        )

        return redirect("/")

    item.title = request.form[
        "title"
    ]

    item.description = request.form[
        "description"
    ]

    item.category = request.form[
        "category"
    ]

    item.location = request.form[
        "location"
    ]

    item.contact = request.form[
        "contact"
    ]

    image_file = request.files.get(
        "image"
    )

    if (

        image_file

        and

        image_file.filename != ""

        and

        allowed_file(
            image_file.filename
        )

    ):

        filename = secure_filename(
            image_file.filename
        )

        unique_filename = (
            f"{uuid.uuid4()}_{filename}"
        )

        image_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            unique_filename

        )

        image_file.save(image_path)

        item.image = unique_filename

    db.session.commit()

    flash(
        "Item updated successfully",
        "success"
    )

    return redirect("/")

# ================= ADD COMMENT =================

@app.route(
    "/comment/<int:item_id>",
    methods=["POST"]
)
def add_comment(item_id):

    if "username" not in session:

        return jsonify({
            "success": False
        })

    comment_text = request.form[
        "comment"
    ].strip()

    if comment_text == "":

        return jsonify({
            "success": False
        })

    item = Item.query.get_or_404(
        item_id
    )

    new_comment = Comment(

        item_id=item.id,

        username=session["username"],

        text=comment_text

    )

    db.session.add(new_comment)

    db.session.commit()

    return jsonify({

        "success": True,

        "comment": {

            "user": new_comment.username,

            "text": new_comment.text,

            "time": new_comment.created_at.strftime(
                "%Y-%m-%d %H:%M"
            )

        }

    })

# ================= RESOLVE ITEM =================

@app.route(
    "/resolve/<int:item_id>",
    methods=["POST"]
)
def resolve_item(item_id):

    if session.get("role") != "admin":

        return redirect("/")

    item = Item.query.get_or_404(
        item_id
    )

    item.resolved = True

    item.resolved_time = (
        datetime.now().isoformat()
    )

    item.claimed_by = (
        "Resolved by Admin"
    )

    item.pickup_time = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    )

    db.session.commit()

    flash(
        "Item resolved successfully",
        "success"
    )

    return redirect("/")

# ================= DELETE ITEM =================

@app.route(
    "/delete/<int:item_id>",
    methods=["POST"]
)
def delete_item(item_id):

    if session.get("role") != "admin":

        return redirect("/")

    item = Item.query.get_or_404(
        item_id
    )

    db.session.delete(item)

    db.session.commit()

    flash(
        "Item deleted successfully",
        "success"
    )

    return redirect("/")

# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "admin":

        return redirect("/")

    total_users = User.query.count()

    total_items = Item.query.count()

    total_lost = Item.query.filter_by(
        status="Lost"
    ).count()

    total_found = Item.query.filter_by(
        status="Found"
    ).count()

    total_resolved = Item.query.filter_by(
        resolved=True
    ).count()

    total_comments = Comment.query.count()

    recent_items = Item.query.order_by(
        Item.created_at.desc()
    ).limit(5).all()

    recent_comments = Comment.query.order_by(
        Comment.created_at.desc()
    ).limit(5).all()

    # ================= TOTAL COUNTS =================

    total_users = User.query.count()

    total_items = Item.query.count()

    total_lost = Item.query.filter_by(
        status="Lost"
    ).count()

    total_found = Item.query.filter_by(
        status="Found"
    ).count()

    total_resolved = Item.query.filter_by(
        resolved=True
    ).count()

    total_comments = Comment.query.count()

    # ================= RECENT DATA =================

    recent_items = Item.query.order_by(
        Item.created_at.desc()
    ).limit(5).all()

    recent_comments = Comment.query.order_by(
        Comment.created_at.desc()
    ).limit(5).all()

    # ================= CATEGORY ANALYTICS =================

    categories = [

        "Electronics",
        "Documents",
        "Clothing",
        "Accessories",
        "Stationery",
        "Other"

    ]

    category_counts = []

    for category in categories:

        count = Item.query.filter_by(
            category=category
        ).count()

        category_counts.append(count)

    # ================= REPORT TREND =================

    trend_labels = []

    trend_counts = []

    for i in range(6, -1, -1):

        day = (
            datetime.now() - timedelta(days=i)
        )

        start_day = datetime(

            day.year,
            day.month,
            day.day

        )

        end_day = (
            start_day + timedelta(days=1)
        )

        count = Item.query.filter(

            Item.created_at >= start_day,

            Item.created_at < end_day

        ).count()

        trend_labels.append(
            day.strftime("%a")
        )

        trend_counts.append(count)

    # ================= RENDER DASHBOARD =================

    return render_template(

        "admin.html",

        total_users=total_users,

        total_items=total_items,

        total_lost=total_lost,

        total_found=total_found,

        total_resolved=total_resolved,

        total_comments=total_comments,

        recent_items=recent_items,

        recent_comments=recent_comments,

        categories=categories,

        category_counts=category_counts,

        trend_labels=trend_labels,

        trend_counts=trend_counts

    )

# ================= FILE TOO LARGE =================

@app.errorhandler(413)
def file_too_large(error):

    flash(

        "Image size exceeds 5MB limit",

        "error"

    )

    return redirect("/")

# ================= RUN =================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        admin_exists = User.query.filter_by(
            username="admin"
        ).first()

        if not admin_exists:

            admin_user = User(

                username="admin",

                password=generate_password_hash(
                    "admin123"
                ),

                role="admin"

            )

            db.session.add(admin_user)

            db.session.commit()

    app.run(debug=True)
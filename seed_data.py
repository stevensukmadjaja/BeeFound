from app import app, db, Item, Comment

from datetime import datetime

import random

users = [
    "alex",
    "john",
    "sarah",
    "michael",
    "david",
    "emma",
    "jessica",
    "kevin",
    "olivia",
    "ethan"
]

categories = [
    "Electronics",
    "Documents",
    "Accessories",
    "Clothing",
    "Stationery",
    "Other"
]

locations = [
    "Library",
    "Student Lounge",
    "Canteen",
    "Parking Area",
    "Building A",
    "Building B",
    "Auditorium"
]

lost_titles = [
    "AirPods Pro",
    "Laptop Charger",
    "Student ID Card",
    "Wallet",
    "Power Bank",
    "Calculator",
    "USB Flash Drive",
    "Notebook",
    "Jacket",
    "Water Bottle"
]

found_titles = [
    "Found AirPods",
    "Found Wallet",
    "Found Student Card",
    "Found Charger",
    "Found Backpack",
    "Found Umbrella",
    "Found Notebook",
    "Found Watch"
]

comments_pool = [
    "I think I saw this near the library.",
    "Is this still available?",
    "Please contact me.",
    "Looks familiar.",
    "I found a similar item yesterday.",
    "Can you provide more details?",
    "Thank you for reporting this.",
    "I might know the owner.",
    "Check the security office.",
    "I sent you a message."
]

with app.app_context():

    print("=" * 50)
    print("DATABASE:", app.config["SQLALCHEMY_DATABASE_URI"])
    print("=" * 50)

    print(
        "Items before:",
        Item.query.count()
    )

    print(
        "Comments before:",
        Comment.query.count()
    )

    try:

        created_items = []

        # ================= LOST =================

        for i in range(70):

            item = Item(

                title=random.choice(
                    lost_titles
                ),

                description=f"Dummy lost item #{i+1}",

                category=random.choice(
                    categories
                ),

                location=random.choice(
                    locations
                ),

                status="Lost",

                contact="dummy@student.com",

                image="",

                owner=random.choice(
                    users
                ),

                resolved=random.random() < 0.20,

                created_at=datetime.utcnow()

            )

            db.session.add(item)

            created_items.append(item)

        # ================= FOUND =================

        for i in range(30):

            item = Item(

                title=random.choice(
                    found_titles
                ),

                description=f"Dummy found item #{i+1}",

                category=random.choice(
                    categories
                ),

                location=random.choice(
                    locations
                ),

                status="Found",

                contact="dummy@student.com",

                image="",

                owner=random.choice(
                    users
                ),

                resolved=random.random() < 0.50,

                created_at=datetime.utcnow()

            )

            db.session.add(item)

            created_items.append(item)

        db.session.commit()

        print("100 reports committed")

        all_items = Item.query.order_by(
            Item.id.desc()
        ).limit(100).all()

        print(
            "Reports in database:",
            len(all_items)
        )

        # ================= COMMENTS =================

        for _ in range(200):

            item = random.choice(
                all_items
            )

            comment = Comment(

                item_id=item.id,

                username=random.choice(
                    users
                ),

                text=random.choice(
                    comments_pool
                )

            )

            db.session.add(comment)

        db.session.commit()

        print("200 comments committed")

        print(
            "Items after:",
            Item.query.count()
        )

        print(
            "Comments after:",
            Comment.query.count()
        )

        print("Seeder finished successfully")

    except Exception as error:

        db.session.rollback()

        print("\nERROR OCCURRED:")
        print(error)

        raise
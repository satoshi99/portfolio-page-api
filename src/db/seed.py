from database import SessionLocal
from models import Admin, Post, Tag, TagPostMapTable

db = SessionLocal()


def seed():
    admin = Admin(email="guest@gmail.com",
                  hashed_password="19211D487CD5C1907F5892435E5A1A382960D4E7B335E65CDCE5A2FA0598B19D")
    tags = [
        Tag(title="Python", slug="python"),
        Tag(title="React.js", slug="reactjs"),
        ]

    post = Post(
        title="post title",
        thumbnail="thumbnail.jpg",
        description="description post ---------",
        content="content -------------",
        is_public=True,
        author_id=admin.id,
    )

    post.tags = tags

    db.add(admin)
    db.add(tags)
    db.add(post)
    db.commit()


if __name__ == "__main__":
    BOS = '\033[92m'
    EOS = '\033[0m'

    print(f"{BOS}Seeding data...{EOS}")
    seed()

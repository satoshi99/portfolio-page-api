from database import SessionLocal
from models import Admin, Post, Tag

db = SessionLocal()


def seed():
    new_admin = Admin(email="guest@gmail.com", hashed_password="secrethashedpassword")
    db.add(new_admin)
    db.commit()

    new_tag = Tag(title="Python", slug="python")
    db.add(new_tag)
    new_tag = Tag(title="React.js", slug="reactjs")
    db.add(new_tag)
    db.commit()

    post = Post(
        title="post title",
        thumbnail="thumbnail.jpg",
        description="description post ---------",
        content="content -------------",
        is_public=True,
        author_id="13534c723c044e10a4a8eb342180965e"
    )
    db.add(post)
    db.commit()

    post = db.query(Post).filter(Post.title == "post title").first()
    tag = db.query(Tag).filter(Tag.title == "React.js").first()
    post.tags.append(tag)
    db.add(post)
    db.commit()


if __name__ == "__main__":
    BOS = '\033[92m'
    EOS = '\033[0m'

    print(f"{BOS}Seeding data...{EOS}")
    seed()

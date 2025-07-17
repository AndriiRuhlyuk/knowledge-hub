# knowledge-hub

A Django-based knowledge base platform that allows employees to create, manage, and search through categorized knowledge bases, publish articles, rate and comment on them.

**Features:**

- Employee model extending Django's AbstractUser
- Thematic Knowledge Bases
- Categorized Articles
- Article Ratings (1–5)
- Commenting System
- Full admin support with custom actions
- Author statistics (published articles, average rating)
- Auto-calculated article reading time

**Technologies:**

- Python 3.11+
- Django 4.x
- SQLite (dev) 
- Django Select2
- Bootstrap 5

🚀 Quick Start

1. Clone the Repository
git clone https://github.com/AndriiRuhlyuk/knowledge-hub
cd knowledge-hub

2. Set Up Virtual Environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Apply Migrations
python manage.py migrate

4. Create Superuser
python manage.py createsuperuser

5. Run the Server
python manage.py runserver
Admin Access

Visit: http://127.0.0.1:8000/admin/
Use the superuser credentials you created

**Application Overview:**

**_Models:_**

- Employee — Custom user with position, project, level
- KnowledgeBase — High-level knowledge container
- Category — Topics within a knowledge base
- Article — Written content by authors, published or draft
- Rating — 1-5 scores per employee per article
- Comment — Reviews and discussions under articles

**Views:**

* Home + Statistics
* CRUD for all models with permission checks
* Search and filtering by form inputs

**Forms:**

* Search forms (for KB, Category, Article, Employee)
* Model forms (Article, Category, Rating, Comment)
* Custom user registration and update forms

**Development Notes**

* Property-based fields in Employee model provide:
* full_name
* published_articles_count
* author_rating
* Reading time calculated from article content
* Admin panel includes custom filters, counters, and batch actions
* Uses django_select2 for author search in articles

**ER Diagram**

https://drive.google.com/file/d/1FncH5pgTXce1yAfYgXhIJdqS0gBKghb4/view?usp=sharing

**Search Support**

* Search Knowledge Bases by title
* Filter Categories by topic
* Filter Articles by title
* Filter Employees by name or author status

**Testing**
python manage.py test

**Deployed resource**
https://knowledge-hub-ucmq.onrender.com
test login: user
test password: user12345

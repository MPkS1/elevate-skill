# Community Learning Platform

A web-based platform for community learning with different user roles (Admin, Wing Head, Member) and various features for sharing knowledge and managing wings.

## Features

### Admin Features
- Create and manage wings
- Add users with different roles (Wing Head, Member)
- Send instructions and forms to specific wings
- View wing members and their activities

### Wing Head Features
- Share personal learnings
- Create quizzes for wing members
- Send notifications to wing members
- View all wing members' learnings

### Member Features
- Share learnings (anonymously or with attribution)
- View wing learnings (anonymous)
- Take quizzes
- View notifications and instructions

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the application at `http://localhost:5000`

## Default Admin Credentials
- Username: admin
- Password: admin123

## Technologies Used
- Backend: Flask
- Database: SQLAlchemy with SQLite
- Frontend: Bootstrap 5, jQuery
- Icons: Font Awesome
- Animations: CSS3

## Security Features
- Password hashing
- User authentication
- Role-based access control
- CSRF protection

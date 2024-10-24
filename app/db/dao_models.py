from app.db.database import async_session_maker
from app.db.models import User, Student, NonStudent
from app.db.dao.base import BaseDAO

class UserDAO(BaseDAO):
    model = User

class StudentDAO(BaseDAO):
    model = Student

class NonStudentDAO(BaseDAO):
    model = NonStudent
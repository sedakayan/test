from datetime import date, datetime
from models import Task, Note
from database import DatabaseManager


class TaskService:
    """
    Implements business logic for Task management.
    Every method works scoped to a specific username so that each
    logged-in user only ever sees and modifies their own tasks.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_task(self, task: Task, username: str) -> bool:
        """
        Validates and adds a new task to the database for the given user.
        """
        if not task.title.strip():
            raise ValueError("Görev başlığı boş olamaz.")
        
        query = """
        INSERT INTO tasks (username, title, description, category, due_date, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            username,
            task.title.strip(),
            task.description.strip(),
            task.category,
            str(task.due_date) if task.due_date else None,
            task.priority,
            task.status
        )
        
        last_id = self.db.execute_non_query(query, params)
        if last_id:
            task.id = last_id
            return True
        return False

    def get_all_tasks(self, username: str) -> list:
        """
        Retrieves all tasks belonging to the given user.
        """
        query = "SELECT id, title, description, category, due_date, priority, status FROM tasks WHERE username = ? ORDER BY id DESC"
        rows = self.db.fetch_all(query, (username,))
        return [Task.from_row(row) for row in rows]

    def get_pending_tasks(self, username: str) -> list:
        """
        Retrieves pending tasks belonging to the given user.
        """
        query = "SELECT id, title, description, category, due_date, priority, status FROM tasks WHERE username = ? AND status = 'Bekliyor' ORDER BY due_date ASC"
        rows = self.db.fetch_all(query, (username,))
        return [Task.from_row(row) for row in rows]

    def get_completed_tasks(self, username: str) -> list:
        """
        Retrieves completed tasks belonging to the given user.
        """
        query = "SELECT id, title, description, category, due_date, priority, status FROM tasks WHERE username = ? AND status = 'Tamamlandı' ORDER BY id DESC"
        rows = self.db.fetch_all(query, (username,))
        return [Task.from_row(row) for row in rows]

    def complete_task(self, task_id: int, username: str) -> bool:
        """
        Marks task status as Completed ('Tamamlandı').
        Scoped by username so a user cannot complete another user's task.
        """
        query = "UPDATE tasks SET status = 'Tamamlandı' WHERE id = ? AND username = ?"
        return bool(self.db.execute_non_query(query, (task_id, username)))

    def delete_task(self, task_id: int, username: str) -> bool:
        """
        Deletes task by id. Scoped by username for the same reason as above.
        """
        query = "DELETE FROM tasks WHERE id = ? AND username = ?"
        return bool(self.db.execute_non_query(query, (task_id, username)))

    def get_tasks_due_today(self, username: str) -> list:
        """
        Fetches pending tasks that are due today for the given user.
        """
        today_str = str(date.today())
        query = """
        SELECT id, title, description, category, due_date, priority, status 
        FROM tasks 
        WHERE username = ? AND status = 'Bekliyor' AND due_date = ?
        """
        rows = self.db.fetch_all(query, (username, today_str))
        return [Task.from_row(row) for row in rows]

    def get_tasks_due_tomorrow(self, username: str) -> list:
        """
        Fetches pending tasks that are due tomorrow for the given user.
        """
        from datetime import timedelta
        tomorrow_str = str(date.today() + timedelta(days=1))
        query = """
        SELECT id, title, description, category, due_date, priority, status 
        FROM tasks 
        WHERE username = ? AND status = 'Bekliyor' AND due_date = ?
        """
        rows = self.db.fetch_all(query, (username, tomorrow_str))
        return [Task.from_row(row) for row in rows]


class NoteService:
    """
    Implements business logic for Note management.
    Every method works scoped to a specific username so that each
    logged-in user only ever sees and modifies their own notes.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_note(self, note: Note, username: str) -> bool:
        """
        Validates and adds a new note for the given user.
        """
        if not note.title.strip():
            raise ValueError("Not başlığı boş olamaz.")
        
        created_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
        INSERT INTO notes (username, title, content, category, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            username,
            note.title.strip(),
            note.content.strip(),
            note.category,
            created_at_str
        )
        
        last_id = self.db.execute_non_query(query, params)
        if last_id:
            note.id = last_id
            note.created_at = created_at_str
            return True
        return False

    def get_all_notes(self, username: str) -> list:
        """
        Retrieves all notes belonging to the given user.
        """
        query = "SELECT id, title, content, category, created_at FROM notes WHERE username = ? ORDER BY id DESC"
        rows = self.db.fetch_all(query, (username,))
        return [Note.from_row(row) for row in rows]

    def delete_note(self, note_id: int, username: str) -> bool:
        """
        Deletes a note by id. Scoped by username so a user cannot
        delete another user's note.
        """
        query = "DELETE FROM notes WHERE id = ? AND username = ?"
        return bool(self.db.execute_non_query(query, (note_id, username)))


class AuthService:
    """
    Implements very simple username/password authentication.
    NOTE: passwords are stored in plain text in the database. This is
    acceptable for a school project but should never be done in a
    real production application — normally a salted hash (e.g. bcrypt)
    would be used instead.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def register(self, username: str, password: str) -> bool:
        """
        Creates a new user account. Returns False if the username
        already exists or the inputs are invalid.
        """
        username = username.strip()
        if not username or not password:
            raise ValueError("Kullanıcı adı ve şifre boş olamaz.")

        existing = self.db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return False

        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        last_id = self.db.execute_non_query(query, (username, password))
        return bool(last_id)

    def login(self, username: str, password: str) -> bool:
        """
        Verifies username/password combination. Returns True on success.
        """
        username = username.strip()
        row = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return row is not None

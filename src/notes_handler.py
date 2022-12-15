import mysql.connector as connector
import time

import assets.globals as globals
import assets.network_info as network_info


class Notes:
  """Class containing notes of a user"""

  notes = dict()

  def __init__(self):
    """Connects to database"""
    try:
      self.database = connector.connect(
        user=network_info.database_username,
        password=network_info.database_password,
        host=network_info.database_host,
        port=network_info.database_port,
        database=network_info.database_title
      )
    except connector.ProgrammingError as e:
      print(e.errno)
      if (e.errno == globals.no_database_error_code):
        self.CreateDatabase(network_info.database_title)
    self.CreateTables()

  def __del__(self):
    """Commits changes to database and closes connection"""

    self.database.commit()
    self.database.close()

  def Command(self, string, args):
    """
      Returns formatted output by placing strings from args container in place
      of question marks in string
    """

    parts = string.split("?")
    command = parts[0]
    for i in range(len(parts) - 1):
      if i < len(args):
        command += args[i]
      else:
        command += '?'
      command += parts[i + 1]
    print(command)
    return command

  def CreateDatabase(self, name):
    """Creates database"""

    session = connector.connect(
      user=network_info.database_username,
      password=network_info.database_password,
      host=network_info.database_host,
      port=network_info.database_port,
    )
    cur = session.cursor()
    cur.execute(self.Command("CREATE DATABASE ?",
                             (network_info.database_title,)))
    session.close()
    self.database = connector.connect(
      user=network_info.database_username,
      password=network_info.database_password,
      host=network_info.database_host,
      port=network_info.database_port,
      database=network_info.database_title
    )

  def CreateTables(self):
    """Creates required tables in the database"""

    cur = self.database.cursor()
    cur.execute(self.Command(
        "CREATE TABLE IF NOT EXISTS ?(?, ?, ?)",
        (
          globals.users_table_title,
          "user_id INT PRIMARY KEY AUTO_INCREMENT",
          "username VARCHAR(30)",
          "password VARCHAR(30)"
        )
      )
    )
    cur.execute(self.Command(
        "CREATE TABLE IF NOT EXISTS ?(?, ?, ?, ?, ?, ?);",
        (
          globals.notes_table_title,
          "note_id INT PRIMARY KEY AUTO_INCREMENT",
          "user_id INT NOT NULL",
          "title VARCHAR(50)",
          "content TEXT",
          ("update_date DATETIME "
           "DEFAULT CURRENT_TIMESTAMP "
           "ON UPDATE CURRENT_TIMESTAMP"),
          "FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE",
        )
      )
    )

  def GetUserId(self, name):
    """Returns id of user with given name"""

    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("SELECT ? "
         "FROM ? "
         "WHERE ? = %s"),
        (
          "user_id",
          globals.users_table_title,
          "username",
        )
      ),
      (
        name,
      )
    )
    users = tuple(cur)
    if len(users) == 0:
      return 0
    return users[0][0]

  def ExistsUser(self, name, password):
    """
      Returns true if entry with given username and password
      exists in the user table
    """

    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("SELECT ? "
         "FROM ? "
         "WHERE ? = %s AND ? = %s"),
        (
          "user_id",
          globals.users_table_title,
          "username",
          "password",
        )
      ),
      (
        name,
        password
      )
    )
    return len(tuple(cur)) != 0

  def RegisterUser(self, name, password):
    """
      Tries to add user with given info to the database.
      Returns True if successful or False if user already existed in database.
    """

    cur = self.database.cursor()
    if self.GetUserId(name) != 0:
      return False
    cur.execute(
      self.Command(
        ("INSERT INTO ?(?, ?) "
         "VALUES (%s, %s)"),
        (
          globals.users_table_title,
          "username",
          "password",
        )
      ),
      (
        name,
        password
      )
    )
    self.database.commit()

    return True

  def SaveNote(self, name, title, content):
    """
      Tries to save given note to the database.
      Returns True if successful or false if note by the same user
      with the same title already existed in database.
    """

    cur = self.database.cursor()
    if title in self.GetUserNotes(name):
      return False
    cur.execute(
      self.Command(
        ("INSERT INTO ?(?, ?, ?) "
         "VALUES (%s, %s, %s);"),
        (
          globals.notes_table_title,
          "user_id",
          "title",
          "content",
        )
      ),
      (
        self.GetUserId(name),
        title,
        content,
      )
    )
    self.database.commit()

    return True

  def RemoveNote(self, name, title):
    """
      Tries to remove given note from the database.
      Returns True if successful or False if given note was not in database.
    """

    cur = self.database.cursor()
    if self.GetNote(name, title) is None:
      return False
    cur.execute(
      self.Command(
        ("DELETE FROM ? "
         "WHERE ? = %s AND ? = %s"),
        (
          globals.notes_table_title,
          "user_id",
          "title",
        )
      ),
      (
        self.GetUserId(name),
        title,
      )
    )
    self.database.commit()
    return True

  def RemoveUser(self, name, password):
    """
      Tries to remove user from database.
      Returns True if successful or False if user wwas not in the database
    """

    if not self.ExistsUser(name, password):
      return False
    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("DELETE FROM ? "
         "WHERE ? = %s;"),
        (
          globals.users_table_title,
          "user_id",
        )
      ),
      (
        self.GetUserId(name),
      )
    )
    self.database.commit()
    return True

  def GetUserNotes(self, name):
    """
      Returns dict(title: (content, update_date)) of notes of the given user.
    """

    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("SELECT ?, ?, ? "
         "FROM ? INNER JOIN ? USING(?) "
         "WHERE ? = %s;"),
        (
          "title",
          "update_date",
          "content",
          globals.notes_table_title,
          globals.users_table_title,
          "user_id",
          "username",
        )
      ),
      (
        name,
      )
    )
    ret = dict(((i[0], (i[1], i[2])) for i in cur))
    return ret

  def UpdateNote(self, name, title, content):
    """
      Updates content of a given note. Returns True if successful or False if
      the note does not exist
    """

    if (self.GetNote(name, title) is None):
      return False
    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("UPDATE ? "
         "SET ? = %s "
         "WHERE ? = %s AND ? = %s;"),
        (
          globals.notes_table_title,
          "content",
          "user_id",
          "title",
        )
      ),
      (
        content,
        self.GetUserId(name),
        title,
      )
    )

  def GetNote(self, name, title):
    """
      Returns info on the given note in a tuple (update_date, cotent)
      or None if such note is not found.
    """

    cur = self.database.cursor()
    cur.execute(
      self.Command(
        ("SELECT ?, ? "
         "FROM ? INNER JOIN ? USING(?) "
         "WHERE ? = %s AND ? = %s;"),
        (
          "update_date",
          "content",
          globals.notes_table_title,
          globals.users_table_title,
          "user_id",
          "username",
          "title",
        )
      ),
      (
        name,
        title,
      )
    )
    ret = tuple(cur)
    if len(ret) == 0:
      return None
    return ret[0]

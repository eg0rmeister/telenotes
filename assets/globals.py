with open("assets/token.txt", "r") as f:
  token = f.readline().strip()
# Of course I trust you, but... you know.

database_username = "eg0rmeister"
database_password = "SA8IL7qI"
database_host = "127.0.0.1"
database_port = 3306
database_title = "telegram_bot"

no_database_error_code = 1049

notes_table_title = "note"
users_table_title = "user"


start_commands = ["start", "help"]
start_message = "Welcome to notes, please login with /login or register with /register"

login_commands = ["login"]
login_message = "log"

register_commands = ["register"]
register_message = "reg"


with open("assets/private.txt", "r") as f:
  token = f.readline().strip()
  database_host = f.readline().strip()
  database_username = f.readline().strip()
  database_password = f.readline().strip()
database_port = 3306
database_title = "telegram_bot"

no_database_error_code = 1049

notes_table_title = "note"
users_table_title = "user"

unavailable_command = "You can't use that command right now"

start_state_id = 0
start_command_id = 0
start_commands = ["start"]
start_message = "Welcome to notes, please login with /login or register with /register"


login_name_state_id = 1
login_command_id = 1
login_commands = ["login"]
login_button_text = "Login"
login_name_message = "Enter username"

login_password_state_id = 2
login_password_message = "Enter password"

login_unsuccessful_message = "Wrong username or password"
login_successful_message = "Login successful. Welcome, %s"

help_command_id = 3
help_commands = ["help"]
help_message = "Use one of the buttons below to interact with me"


register_command_id = 2
register_commands = ["register"]
register_button_text = "Register"
register_message = "reg"
register_name_state_id = 3
msg_register_name_message = "Enter your username"
msg_register_name_taken = "This username is already taken, pick another one"

register_password_state_id = 4
register_password_message = "Enter your password"

msg_registration_successful = "Registration successful. Welcome, %s"

main_state_id = 5

delete_user_state_id = 6
delete_user_command_id = 4
delete_user_commands = ["delete_user"]
delete_user_button_text = "Delete User"
delete_user_message = "Enter username to delete. Warning: It will delete ALL of this user's notes"

delete_password_state_id = 7
delete_password_message = "Enter password of that user"
user_delete_successful_message = "User %s was successfully deleted"
user_delete_unsuccessful_message = "Invalid username or password"

create_note_title_state_id = 8
create_note_command_id = 5
create_note_commands = ["create_note"]
create_note_button_text = "Create Note"
create_note_title_message = "Enter note title"
create_note_failure_message = "You already have note with that title"


create_note_content_state_id = 9
create_note_content_message = "Enter note content"
create_note_success_message = "Note %s created successfully"



delete_note_state_id = 10
delete_note_command_id = 6
delete_note_commands = ["delete_note"]
delete_note_button_text = "Delete Note"
delete_note_message = "Enter title of note to be deleted"
delete_note_successful = "Note %s was deleted"
delete_note_unsuccessful = "This note does not exist"

redact_note_title_state_id = 11
redact_note_command_id = 7
redact_note_commands = ["redact_note"]
redact_note_button_text = "Redact Note"
redact_note_title_message = "Enter title of note to be redacted"
redact_note_title_unsuccessful_message = "Note with that name does not exist"

redact_note_content_state_id = 12
redact_note_content_message = "Enter new content for this note"

redact_note_successful_message = "Note %s was successfully redacted"

show_note_command_id = 8
show_note_state_id = 13
show_note_commands = ["show"]
show_note_button_text = "Show Note"
show_note_message = "Enter title of note to be shown"
show_note_unsuccessful_message = "You don't have note with that title"

list_note_command_id = 9
list_note_commands = ["list"]
list_note_button_text = "List Notes"
list_note_message = "Your notes:"

logout_command_id = 9
logout_commands = ["logout"]
logout_button_text = "Logout"
logout_message = "You are no longer logged in"

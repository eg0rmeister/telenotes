import telebot

import assets.globals as globals
import assets.network_info as network_info
import src.notes_handler as nh

bot = telebot.TeleBot(network_info.token, parse_mode=None)

class StateMachine:
  """Class for handling events in different states"""
  
  def _GetAvailable(self):
    """Getter for set of available commands"""
    
    ret = set()
    if self.state == globals.start_state_id:
      ret.add(globals.register_command_id)
      ret.add(globals.login_command_id)
    elif self.state == globals.main_state_id:
      ret.add(globals.create_note_command_id)
      ret.add(globals.delete_note_command_id)
      ret.add(globals.delete_user_command_id)
      ret.add(globals.list_note_command_id)
      ret.add(globals.logout_command_id)
      ret.add(globals.redact_note_command_id)
      ret.add(globals.show_note_command_id)
    return ret
    
  available = property(_GetAvailable)
  state = globals.start_state_id
  username = None
  password = None
  
  username_to_delete = None
  password_to_delete = None
  
  note_title = None
  
  def Available(self, id):
    return id in self.available
  
  def __init__(self, message):
    """Sets the state to start"""

    self.StateToStart(message)

  def Handle(self, message, notes):
    """Handles non-command messages"""

    print(f"new message from {message.chat.id}: {message.text}")
    print(f"current state id: {self.state}")
    if self.state == globals.start_state_id:
      self.StateToStart(message)
    elif self.state == globals.register_name_state_id:
      self.HandleRegisterName(message, notes)
    elif self.state == globals.register_password_state_id:
      self.HandleRegisterPassword(message, notes)
    elif self.state == globals.main_state_id:
      self.HandleMain(message)
    elif self.state == globals.delete_user_state_id:
      self.HandleDeleteName(message)
    elif self.state == globals.delete_password_state_id:
      self.HandleDeletePassword(message, notes)
    elif self.state == globals.login_name_state_id:
      self.HandleLoginName(message)
    elif self.state == globals.login_password_state_id:
      self.HandleLoginPassword(message, notes)
    elif self.state == globals.create_note_title_state_id:
      self.HandleCreateNoteTitle(message, notes)
    elif self.state == globals.create_note_content_state_id:
      self.HandleCreateNoteContent(message, notes)
    elif self.state == globals.delete_note_state_id:
      self.HandleDeleteNote(message, notes)
    elif self.state == globals.show_note_state_id:
      self.HandleShowNote(message, notes)
    elif self.state == globals.redact_note_title_state_id:
      self.HandleRedactNoteTitle(message, notes)
    elif self.state == globals.redact_note_content_state_id:
      self.HandleRedactNoteContent(message, notes)
  
  def HandleQuery(self, call, notes):
    """Handles button presses"""
    
    if (call.data in globals.register_commands and
          self.Available(globals.register_command_id)):
      self.StateToRegister(call.message)
    elif (call.data in globals.login_commands and
          self.Available(globals.login_command_id)):
      self.StateToLogin(call.message)
    elif (call.data in globals.logout_commands and
          self.Available(globals.logout_command_id)):
      self.HandleLogout(call.message)
    elif (call.data in globals.delete_user_commands and
          self.Available(globals.delete_user_command_id)):
      self.StateToDeleteUser(call.message)
    elif (call.data in globals.create_note_commands and
          self.Available(globals.create_note_command_id)):
      self.StateToCreateNote(call.message)
    elif (call.data in globals.redact_note_commands and
          self.Available(globals.redact_note_command_id)):
      self.StateToRedactNote(call.message)
    elif (call.data in globals.delete_note_commands and
          self.Available(globals.delete_note_command_id)):
      self.StateToDeleteNote(call.message)
    elif (call.data in globals.show_note_commands and
          self.Available(globals.show_note_command_id)):
      self.StateToShowNote(call.message)
    elif (call.data in globals.list_note_commands and
          self.Available(globals.list_note_command_id)):
      self.ListNotes(call.message, notes)
  
  def StateToRedactNote(self, message):
    """Changes the state to redact note title"""
    
    self.state = globals.redact_note_title_state_id
    bot.send_message(message.chat.id, globals.redact_note_title_message)
    
  def HandleRedactNoteTitle(self, message, notes):
    """
      Tries to display note's contents before changing the state
      to redact note content
    """
    note = notes.GetNote(self.username, message.text)
    if note == None:
      bot.send_message(message.chat.id,
                       globals.redact_note_title_unsuccessful_message)
      self.StateToMain(message)
      return
    bot.send_message(message.chat.id,
                     f"{message.text}\n\t{note[0]}\n\n{note[1]}")
    bot.send_message(message.chat.id, globals.redact_note_content_message)
    self.state = globals.redact_note_content_state_id
    self.note_title = message.text
  
  def HandleRedactNoteContent(self, message, notes):
    """Changes note's content"""
    
    notes.UpdateNote(self.username, self.note_title, message.text)
    bot.send_message(message.chat.id,
                     globals.redact_note_successful_message % self.note_title)
    self.StateToMain(message)
  
  def StateToShowNote(self, message):
    """Changes state to show note"""

    self.state = globals.show_note_state_id
    bot.send_message(message.chat.id, globals.show_note_message)
  
  def HandleShowNote(self, message, notes):
    """Tries to show note with given title"""
    
    note = notes.GetNote(self.username, message.text)
    if note == None:
      bot.send_message(message.chat.id, globals.show_note_unsuccessful_message)
      self.StateToMain(message)
      return
    bot.send_message(message.chat.id,
                     f"{message.text}\n\t{note[0]}\n\n{note[1]}")
    self.StateToMain(message)
  
  def StateToDeleteNote(self, message):
    """Sets state to delete note"""
    
    bot.send_message(message.chat.id, globals.delete_note_message)
    self.state = globals.delete_note_state_id

  def HandleDeleteNote(self, message, notes):
    if notes.RemoveNote(self.username, message.text):
      bot.send_message(message.chat.id,
                       globals.delete_note_successful % message.text)
      self.StateToMain(message)
      return
    bot.send_message(message.chat.id, globals.delete_note_unsuccessful)
    self.StateToMain(message)
  
  def ListNotes(self, message, notes):
    """Sends list of all the notes the user has"""
    
    notes_dict = notes.GetUserNotes(self.username)
    to_send = globals.list_note_message
    for i in notes_dict:
      to_send += f"\n\n{i}\n\t{notes_dict[i][0]}"
    bot.send_message(message.chat.id, to_send)
  
  def StateToCreateNote(self, message):
    """Changes state to note creation"""
  
    bot.send_message(message.chat.id, globals.create_note_title_message)
    self.state = globals.create_note_title_state_id
  
  def HandleCreateNoteTitle(self, message, notes):
    """Handles enter title part of creating note"""

    if (notes.GetNote(self.username, message.text) == None):
      self.note_title = message.text
      bot.send_message(message.chat.id, globals.create_note_content_message)
      self.state = globals.create_note_content_state_id
      return
    bot.send_message(message.chat.id, globals.create_note_failure_message)
    self.StateToMain(message)
  
  def HandleCreateNoteContent(self, message, notes):
    """Handles enter content part of creating note"""
    
    notes.SaveNote(self.username, self.note_title, message.text)
    bot.send_message(message.chat.id,
                     globals.create_note_success_message%self.note_title)
    self.note_title = None
    self.StateToMain(message)
  
  def StateToStart(self, message):
    """Changes the state to start"""
    
    keyboard = telebot.util.quick_markup({
      globals.register_button_text: {
        'callback_data': globals.register_commands[0]},
      globals.login_button_text:{
        'callback_data': globals.login_commands[0]},
    })
    
    bot.send_message(message.chat.id, globals.start_message, reply_markup=keyboard)
    self.state = globals.start_state_id
  
  def StateToRegister(self, message):
    """Changes the state to register name"""
    
    bot.send_message(message.chat.id, globals.msg_register_name_message)
    self.state = globals.register_name_state_id
  
  def HandleRegisterName(self, message, notes):
    """Handles registration enter login part"""
    
    if (notes.GetUserId(message.text) != 0):
      bot.send_message(message.chat.id, globals.msg_register_name_taken)
      self.StateToStart(message)
      return
    self.username = message.text
    bot.send_message(message.chat.id, globals.register_password_message)
    self.state = globals.register_password_state_id

  def HandleRegisterPassword(self, message, notes):
    """Handles registration enter password part"""
    
    self.password = message.text
    notes.RegisterUser(self.username, self.password)
    bot.send_message(
      message.chat.id,
      globals.msg_registration_successful%self.username
    )
    self.StateToMain(message)
  
  def StateToDeleteUser(self, message):
    """Set State to user deletion"""
    
    bot.send_message(message.chat.id, globals.delete_user_message)
    self.state = globals.delete_user_state_id
  
  def SendHelp(self, message):
    """Sends help message"""
    
    keyboard = telebot.util.quick_markup({
      globals.delete_user_button_text: {
        'callback_data': globals.delete_user_commands[0]},
      globals.logout_button_text:{
        'callback_data': globals.logout_commands[0]},
      globals.create_note_button_text:{
        'callback_data': globals.create_note_commands[0]},
      globals.redact_note_button_text:{
        'callback_data': globals.redact_note_commands[0]},
      globals.show_note_button_text:{
        'callback_data': globals.show_note_commands[0]},
      globals.delete_note_button_text:{
        'callback_data': globals.delete_note_commands[0]},
      globals.list_note_button_text:{
        'callback_data': globals.list_note_commands[0]},
    })
    
    bot.send_message(message.chat.id, globals.help_message,
                     reply_markup=keyboard)

  def HandleMain(self, message):
    """Handles main messages"""
    
    self.SendHelp(message)
  
  def StateToMain(self, message):
    """Changes state to main"""
    
    self.state = globals.main_state_id
    self.SendHelp(message)
  
  def HandleLogout(self, message):
    """Handles /logout command"""
    
    bot.send_message(message.chat.id, globals.logout_message)
    self.StateToStart(message)
  
  def HandleDeleteName(self, message):
    """Changes state to user deletion password"""
    
    self.username_to_delete = message.text
    bot.send_message(message.chat.id, globals.delete_password_message)
    self.state = globals.delete_password_state_id
  
  def HandleDeletePassword(self, message, notes):
    """Attempts to delete user"""
    
    if notes.RemoveUser(self.username_to_delete, message.text):
      bot.send_message(
        message.chat.id,
        globals.user_delete_successful_message % self.username_to_delete
      )
      if self.username_to_delete == self.username:
        self.StateToStart(message)
      else:
        self.StateToMain(message)
    else:
      bot.send_message(message.chat.id,
                       globals.user_delete_unsuccessful_message)
      self.StateToMain(message)
  
  def StateToLogin(self, message):
    """Sets state to enter username part of login"""
    
    self.state = globals.login_name_state_id
    bot.send_message(message.chat.id, globals.login_name_message)
  
  def HandleLoginName(self, message):
    """Sets state to enter password part of login and memorizes the username"""
    
    self.username = message.text
    self.state = globals.login_password_state_id
    bot.send_message(message.chat.id, globals.login_password_message)
  
  def HandleLoginPassword(self, message, notes):
    """
      Tries to log in and change state to main.
      Changes state to start if such username was not found
    """
    
    if (notes.ExistsUser(self.username, message.text)):
      bot.send_message(message.chat.id,
                       globals.login_successful_message%self.username)
      self.StateToMain(message)
      return
    bot.send_message(message.chat.id, globals.login_unsuccessful_message)
    self.StateToStart(message)
  
  
def start():
  handlers = dict()
  notes = nh.Notes()

  @bot.callback_query_handler(func=lambda m: True)
  def callback_query(call):
    if (call.message.chat.id not in handlers):
      handlers[call.message.chat.id] = StateMachine(call.message)
    handlers[call.message.chat.id].HandleQuery(call, notes)
  
  @bot.message_handler()
  def handler(message):
    if message.chat.id not in handlers:
      handlers[message.chat.id] = StateMachine(message)
      handlers[message.chat.id].StateToStart(message)
      return
    handlers[message.chat.id].Handle(message, notes)
  
  bot.infinity_polling()
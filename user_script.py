from db import User, reset_users, init_users

reset_users()

User.create("jill","password")
token = User.login("jill","password")
print User.logout("jill",token)

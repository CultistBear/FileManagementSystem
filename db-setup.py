from databaseManagement import DB

db = DB()
db.query("DROP TABLE if exists Users;")
db.query("Drop table if exists Files;")
db.query("CREATE TABLE Users(id INT AUTO_INCREMENT PRIMARY KEY, Username varchar(16), Name varchar(100), Phone varchar(10), Email varchar(100), Password varchar(300), role enum( 'admin', 'user', 'viewer', 'editor'))")
db.query("Create table Files(id INT AUTO_INCREMENT PRIMARY KEY, FileName varchar(100), FileOwner varchar(100), FileType varchar(100), LastEditedUser varchar(100), LastEditedTime timestamp);")
db.close()
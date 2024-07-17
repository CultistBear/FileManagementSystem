from databaseManagement import DB

db = DB()
db.query("DROP TABLE Users;")
db.query("CREATE TABLE Users(id INT AUTO_INCREMENT PRIMARY KEY,Username varchar(16), Name varchar(100), Phone varchar(10), Email varchar(100), Password varchar(300), role enum( 'admin', 'user', 'viewer', 'editor'))")
db.close()
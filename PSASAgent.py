from Database.db_interface import DBInterface

if __name__ == '__main__':
    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    db = DBInterface('res/ssh_db_pw.json')
    rows = db.run_command("SELECT * FROM twitter").fetchall()
    for row in rows:
        for col in row:
            print(col)

    db.close()

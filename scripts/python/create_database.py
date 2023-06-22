from psycopg2 import connect, extensions, sql

connection = connect(user="ntg",
                     password="topsecret",
                     host="127.0.0.1",
                     port="5432",
                     database="access_db")

print('\ntype(connection):', type(connection))

db_name = 'gal_ph1'
autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
print('ISOLATION_LEVEL_AUTOCOMMIT:', extensions.ISOLATION_LEVEL_AUTOCOMMIT)

connection.set_isolation_level(autocommit)

cursor = connection.cursor()
cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(db_name)))
cursor.execute(sql.SQL('DROP SCHEMA IF EXISTS ntg CASCADE'))


cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))

structure_dump = open('../../data/cbgm_structure.sql', 'r')
cursor.execute(structure_dump.read())

books_dump = open('../../data/books.sql', 'r')
cursor.execute(books_dump.read())

cursor.execute(sql.SQL('SELECT * FROM ntg.books'))
print(cursor.fetchall())

# ranges_dump = open('../../data/ranges.dump', 'r')
# cursor.execute(ranges_dump.read())



cursor.close()
connection.close()

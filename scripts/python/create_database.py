from psycopg2 import connect, extensions, sql

connection = connect(user="ntg",
                     password="topsecret",
                     host="127.0.0.1",
                     port="5432",
                     database="access_db")


db_name = 'gal_ph1'
autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT

connection.set_isolation_level(autocommit)

cursor = connection.cursor()
print('Dropping existing dataabase if necessary')
cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(db_name)))
cursor.execute(sql.SQL('DROP SCHEMA IF EXISTS ntg CASCADE'))
print('Done')

print('Creating new database and loading structure')
cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))

structure_dump = open('../../data/cbgm_structure.sql', 'r')
cursor.execute(structure_dump.read())
print('Done')

print('Loading book data')
books_dump = open('../../data/books.sql', 'r')
cursor.execute(books_dump.read())

cursor.execute(sql.SQL('SELECT * FROM ntg.books'))
assert(len(cursor.fetchall()), 28)
print('Done')

print('Loading ranges')
ranges_dump = open('../../data/ranges.sql', 'r')
cursor.execute(ranges_dump.read())
cursor.execute(sql.SQL('SELECT * FROM ntg.ranges'))
assert(len(cursor.fetchall()), 290)
print('Done')


cursor.close()
connection.close()

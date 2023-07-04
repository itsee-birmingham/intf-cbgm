import sys
import argparse
import subprocess
from psycopg2 import connect, extensions, sql
from ITSEEnestle import ItseeBaseTextLoader
from itseeimport import ItseeApparatusLoader


# run 
# python3 create_database.py gal_ph1 9 ../../data/gal_positive 020 049 1 35 398 424 1069 1617 2352 7

def create_database(db_name):

    connection = connect(user="ntg",
                        password="topsecret",
                        host="127.0.0.1",
                        port="5432",
                        database="access_db")

    autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT

    connection.set_isolation_level(autocommit)

    cursor = connection.cursor()
    print('Dropping existing database if necessary')
    cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(db_name)))
    cursor.execute(sql.SQL('DROP SCHEMA IF EXISTS ntg CASCADE'))
    print('Done')

    print('Creating new database and loading structure')
    cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))

    cursor.close()
    connection.close()


def load_structure_and_data(db_name):

    connection = connect(user="ntg",
                        password="topsecret",
                        host="127.0.0.1",
                        port="5432",
                        database=db_name)

    autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
    connection.set_isolation_level(autocommit)
    cursor = connection.cursor()

    structure_dump = open('../../data/cbgm_structure.sql', 'r')
    cursor.execute(structure_dump.read())
    print('Done')

    print('Loading book data')
    books_dump = open('../../data/books.sql', 'r')
    cursor.execute(books_dump.read())

    cursor.execute(sql.SQL('SELECT * FROM ntg.books'))
    assert(len(cursor.fetchall()) == 28)
    print('Done')

    print('Loading ranges')
    ranges_dump = open('../../data/ranges.sql', 'r')
    cursor.execute(ranges_dump.read())
    cursor.execute(sql.SQL('SELECT * FROM ntg.ranges'))
    assert(len(cursor.fetchall()) == 290)
    print('Done')

    cursor.execute(sql.SQL('SELECT * FROM ntg.nestle'))
    assert(len(cursor.fetchall()) == 0)

    cursor.close()
    connection.close()

def dump_database(db_name):
    output_file = open('%s.dump' % db_name, mode='wb')
    subprocess.run('docker exec docker_ntg-db-server_1 bash -c "pg_dump -Fc -U ntg gal_ph1"', shell=True, stdout=output_file)

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('db_name', help='The name of the database to create.')
    parser.add_argument('book_number', type=int, help='The number of the book according to the books.sql list.')
    parser.add_argument('data_dir', help='The path to the directory containing all the data files.')
    parser.add_argument('byz_wits', nargs='*', help='The set of sigla to be treated as MT.')
    parser.add_argument('minimum_byz_for_MT', type=int, help='The minimum number of Byz wits that must agree to be considered MT')
    args = parser.parse_args()

    create_database(args.db_name)

    load_structure_and_data(args.db_name)

    basetext_loader = ItseeBaseTextLoader()
    basetext_loader.load_basetext(args.db_name, args.book_number, args.data_dir)

    apparatus_loader = ItseeApparatusLoader()
    apparatus_loader.load_apparatus(args.db_name, args.book_number, args.data_dir, set(args.byz_wits), args.minimum_byz_for_MT)

    dump_database(args.db_name)

if __name__ == "__main__":
    main(sys.argv[1:])

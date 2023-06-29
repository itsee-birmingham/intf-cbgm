import xml.etree.ElementTree as ET
import psycopg2
from os import path


# data_dir = '../../data/gal_positive'

class ItseeBaseTextLoader(object):

    def load_basetext(self, db_name, book_number, data_dir):
        
        data_file = path.join(data_dir, 'basetext.xml')

        tree = ET.parse(data_file)
        root = tree.getroot()

        connection = psycopg2.connect(user="ntg",
                                    password="topsecret",
                                    host="127.0.0.1",
                                    port="5432",
                                    database=db_name)
        cursor = connection.cursor()

        delete_query = 'DELETE FROM nestle'
        cursor.execute(delete_query)
        connection.commit()

        cursor.execute('ALTER SEQUENCE nestle_id_seq RESTART WITH 1')
        connection.commit()

        insert_query = 'INSERT INTO nestle (begadr, endadr, passage, lemma) VALUES (%s, %s, %s, %s)'

        book = book_number

        index = 2
        for word in root.findall('.//{http://www.tei-c.org/ns/1.0}div[@type="incipit"]//{http://www.tei-c.org/ns/1.0}w'):
            lemma = word.get('lemma').replace('’', '')
            begadr = (book_number*10000000) + index
            endadr = begadr
            passage = '[{},{})'.format(begadr, begadr + 1)
            try:
                cursor.execute(insert_query, (begadr, endadr, passage, lemma))
                connection.commit()
            except psycopg2.errors.UniqueViolation:
                connection.rollback()
                pass
            index += 2

        for ab in root.findall('.//{http://www.tei-c.org/ns/1.0}div[@type="chapter"]/{http://www.tei-c.org/ns/1.0}ab'):
            index = 2
            name, chapter, verse = ab.get('n').split('.')
            for word in ab.findall('.//{http://www.tei-c.org/ns/1.0}w'):
                lemma = word.get('lemma').replace('’', '')
                begadr = (book_number*10000000) + (int(chapter) * 100000) + (int(verse) * 1000) + index
                endadr = begadr
                passage = '[{},{})'.format(begadr, begadr + 1)
                try:
                    cursor.execute(insert_query, (begadr, endadr, passage, lemma))
                    connection.commit()
                except psycopg2.errors.UniqueViolation:
                    connection.rollback()
                    pass
                index += 2

        # this is how the explicit is done for Mark - I don't know if it is correct I am just copying.
        lemma = '&om;'
        begadr = (book_number*10000000) + ((int(chapter) + 1) * 100000) + 2
        endadr = begadr
        passage = '[{},{})'.format(begadr, begadr + 1)
        try:
            cursor.execute(insert_query, (begadr, endadr, passage, lemma))
            connection.commit()
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            pass

        cursor.close()
        connection.close()

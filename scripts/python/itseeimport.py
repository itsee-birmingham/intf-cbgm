import os
import sys
import psycopg2
import xml.etree.ElementTree as ET

data_dir = '../../data/gal_positive'
BYZ_WITS = set(['020', '049', '1', '35', '398', '424', '1069', '1617', '2352'])
db_name = 'gal_ph1'

class ItseeApparatusLoader(object):

    def __init__(self):
        self.connection = psycopg2.connect(user="ntg",
                                    password="topsecret",
                                    host="127.0.0.1",
                                    port="5432",
                                    database=db_name)
        self.cursor = self.connection.cursor()

    def load_apparatus(self, db_name, book_number, data_dir, BYZ_WITS):

        print('byz wits')
        print(BYZ_WITS)

        self.cursor.execute("""ALTER TABLE locstem DISABLE TRIGGER locstem_trigger""")
        self.connection.commit()

        self.cursor.execute('DELETE FROM locstem')
        self.connection.commit()

        self.cursor.execute('SET ntg.user_id = 0; DELETE FROM manuscripts')
        self.connection.commit()

        self.cursor.execute('ALTER SEQUENCE manuscripts_ms_id_seq RESTART WITH 1')
        self.connection.commit()

        self.cursor.execute('SET ntg.user_id = 0; DELETE FROM passages')
        self.connection.commit()

        self.cursor.execute('ALTER SEQUENCE passages_pass_id_seq RESTART WITH 1')
        self.connection.commit()

        self.cursor.execute('DELETE FROM readings')
        self.connection.commit()

        self.cursor.execute('DELETE FROM apparatus')
        self.connection.commit()

        self.cursor.execute('DELETE FROM ms_ranges')
        self.connection.commit()


        self.cursor.execute("""DELETE FROM ms_cliques
                        WHERE ms_id = (select ms_id from manuscripts where hs = %s)""",
                    ('MT',))
        self.cursor.execute("""DELETE FROM ms_cliques_tts
                        WHERE ms_id = (select ms_id from manuscripts where hs = %s)""",
                    ('MT',))
        self.cursor.execute("""DELETE FROM apparatus
                        WHERE ms_id = (select ms_id from manuscripts where hs = %s)""",
                    ('MT',))
        self.connection.commit()

        file_names = [f for f in os.listdir(data_dir)
                    if f[-4:] == '.xml' and f != 'basetext.xml']

        file_names.sort(key=self.get_chapter_number)

        app_insert = """INSERT INTO apparatus (ms_id, pass_id, labez,
                cbgm, labezsuf, certainty, lesart, origin)
                VALUES ((select ms_id from manuscripts where hs = %s),
                (select pass_id from passages where passage = %s), %s, %s, %s, %s, %s, %s)"""
        locstem_insert = """INSERT INTO locstem (pass_id, labez, clique, source_labez, source_clique, user_id_start)
                            VALUES ((select pass_id from passages where passage = %s), %s, %s, %s, %s, %s)"""

        # the order in which verses and variant units are added matters so make
        # sure the chapters are added in the correct order. The xml order takes care of
        # everything else for now but it does means we add overlaps in a different order
        # that that used by the INTF. We prefer this, but we may need to change it.

        MSS_added = False
        for file in file_names:

            tree = ET.parse(os.path.join(data_dir, file))
            root = tree.getroot()

            for app in root.findall('.//{http://www.tei-c.org/ns/1.0}app'):
                if not MSS_added:  # the MSS only need to be added once because they are all listed in every app unit
                    self.add_manuscripts(app)
                    self.add_ms_ranges(book_number)
                    MSS_added = True
                if self.is_variant(app):
                    MT_reading_label = self.get_MT_reading(app)
                    if MT_reading_label is None:
                        raise ValueError('MT reading is not defined')
                    ref = app.get('n')
                    start = int(app.get('from'))
                    end = int(app.get('to'))
                    print('{}/{}-{}'.format(ref, start, end))
                    # passages (once per app)
                    passage_data = self.get_passage_data(book_number, ref, start, end)
                    if passage_data is not None:
                        self.cursor.execute("""INSERT INTO passages (bk_id, begadr, endadr,
                                    passage, variant, spanning, spanned, fehlvers)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                    passage_data)
                        self.connection.commit()
                        # readings (once per main reading) (fehlverse is I think for when there is no a text)
                        for rdg in app.findall('.//{http://www.tei-c.org/ns/1.0}rdg'):
                            if rdg.get('type') != 'subreading':
                                labez = rdg.get('n')
                                if '/' not in labez:
                                    if labez in ['zz', 'zu']:
                                        lesart = None
                                    else:
                                        lesart = rdg.text
                                        if lesart == 'om':
                                            lesart = None
                                    data = (passage_data[3], labez, lesart)
                                    self.cursor.execute("""INSERT INTO readings (pass_id, labez, lesart)
                                                VALUES ((select pass_id from passages where passage = %s), %s, %s)""",
                                                data)
                                    # also add to cliques table (importMatthew does this)
                                    clique_data = (passage_data[3], labez, 1, 0)
                                    self.cursor.execute("""SET ntg.user_id = 0; INSERT INTO cliques (pass_id, labez, clique, user_id_start)
                                                VALUES ((select pass_id from passages where passage = %s), %s, %s, %s)""",
                                                clique_data)
                                    self.connection.commit()
                                    # also add to locstem table if not zu, zz
                                    if labez == 'a':
                                        data = (passage_data[3], labez, '1', '*', '1', 0)
                                        self.cursor.execute(locstem_insert, data)
                                    elif labez not in ['zz', 'zu']:
                                        data = (passage_data[3], labez, '1', 'a', '1', 0)
                                        self.cursor.execute(locstem_insert, data)

                                if labez == MT_reading_label:
                                    data = ('MT', passage_data[3], labez, True, '', 1, lesart, 'BYZ')
                                    self.cursor.execute(app_insert, data)
                                    clique_data = ('MT', passage_data[3], labez, 1, 0)
                                    self.cursor.execute("""SET ntg.user_id = 0; INSERT INTO ms_cliques (ms_id, pass_id, labez, clique, user_id_start)
                                                VALUES ((select ms_id from manuscripts where hs = %s),
                                                        (select pass_id from passages where passage = %s), %s, %s, %s)""",
                                                clique_data)
                                    self.connection.commit()

                            # apparatus (once per witness)
                            for witness in rdg.findall('.//{http://www.tei-c.org/ns/1.0}idno'):
                                hs = witness.text
                                # # rename a manuscript for Galatians
                                # if hs == '2892':
                                #     hs = '2853'
                                type = rdg.get('type')
                                if type != 'subreading':
                                    labez = rdg.get('n')
                                    labezsuf = ''
                                    lesart = rdg.text
                                    if lesart == 'om':
                                        lesart = None
                                else:
                                    labezsuf = rdg.get('n').replace(labez, '', 1)
                                    lesart = rdg.text
                                    if lesart == 'om':
                                        lesart = None
                                if '/' not in labez:
                                    data = (hs, passage_data[3], labez, True, labezsuf, 1, lesart, 'ATT')
                                    self.cursor.execute(app_insert, data)
                                    # also add to ms_cliques table (importMatthew does this)
                                    clique_data = (hs, passage_data[3], labez, 1, 0)
                                    self.cursor.execute("""SET ntg.user_id = 0; INSERT INTO ms_cliques (ms_id, pass_id, labez, clique, user_id_start)
                                                VALUES ((select ms_id from manuscripts where hs = %s),
                                                        (select pass_id from passages where passage = %s), %s, %s, %s)""",
                                                clique_data)
                                    self.connection.commit()
                                else:
                                    labels = labez.split('/')
                                    # these are recorded separately as zw and with cbgm set to false
                                    for label in labels:
                                        if (len(label) > 1):
                                            label = label[0]
                                        data = (hs, passage_data[3], label, False, labezsuf, 1/len(labels), lesart, 'ZW')
                                        self.cursor.execute(app_insert, data)
                                        # also add to ms_cliques table (importMatthew does this)
                                        clique_data = (hs, passage_data[3], label, 1, 0)
                                        self.cursor.execute("""SET ntg.user_id = 0; INSERT INTO ms_cliques (ms_id, pass_id, labez, clique, user_id_start)
                                                    VALUES ((select ms_id from manuscripts where hs = %s),
                                                            (select pass_id from passages where passage = %s), %s, %s, %s)""",
                                                    clique_data)
                                        self.connection.commit()

            # this is taken from the prepare.py script. It seems to do something.
            # We have overlapping overlaps which I am not sure the INTF allow so I'm not
            # sure if it is doing the right thing equally I'm not sure that this is
            # needed at all because I don't know what the booleans are used for
            self.cursor.execute(""" UPDATE passages p
                            SET spanned = EXISTS (
                            SELECT passage FROM passages o
                            WHERE o.passage @> p.passage AND p.pass_id != o.pass_id
                            ),
                            spanning = EXISTS (
                            SELECT passage FROM passages i
                            WHERE i.passage <@ p.passage AND p.pass_id != i.pass_id
                            )""")
            self.connection.commit()

            self.cursor.execute("""ALTER TABLE locstem ENABLE TRIGGER locstem_trigger""")
            self.connection.commit()

        self.cursor.close()
        self.connection.close()

    def get_all_witnesses(self, app):
        witnesses = []
        idnos = app.findall('.//{http://www.tei-c.org/ns/1.0}idno')
        for id in idnos:
            # rename a manuscript for Galatians
            # TODO: REMOVE THIS
            # if id.text == '2892':
            #     witnesses.append('2853')
            # else:
            witnesses.append(id.text)
        return witnesses

    def get_hsnr(self, wit):
        supp = 0
        if wit[-1].lower() == 's':
            supp = 1
            wit = wit[:-1]
        if wit[-2:].lower() == 's1':
            supp = 1
            wit = wit[:-2]
        if wit[-2:].lower() == 's2':
            supp = 2
            wit = wit[:-2]
        if wit[0] == 'P':
            return 100000 + (int(wit[1:]) * 10) + supp
        if wit[0] == 'L':
            return 400000 + (int(wit[1:]) * 10) + supp
        if wit[0] == '0':
            return 200000 + (int(wit[1:]) * 10) + supp
        return 300000 + (int(wit) * 10) + supp

    def add_hsnr(self, witnesses):
        expanded_witnesses = []
        for wit in witnesses:
            expanded_witnesses.append((self.get_hsnr(wit), wit))
        expanded_witnesses.sort(key=lambda x: x[0])
        return expanded_witnesses

    def add_manuscripts(self, app):
        mss_insert_query = "INSERT INTO manuscripts (hsnr, hs) VALUES (%s, %s)"
        witnesses = self.get_all_witnesses(app)
        witnesses = self.add_hsnr(witnesses)
        self.cursor.execute(mss_insert_query, (0, 'A'))
        self.cursor.execute(mss_insert_query, (1, 'MT'))
        for witness in witnesses:
            self.cursor.execute(mss_insert_query, witness)
        self.connection.commit()

    def get_passage_data(self, book_number, ref, start, end):
        try:
            book, chapter, verse = ref.split('.')
        except ValueError:
            return None
        begadr = (book_number*10000000) + (int(chapter) * 100000) + (int(verse) * 1000) + start
        endadr = (book_number*10000000) + (int(chapter) * 100000) + (int(verse) * 1000) + end
        passage = '[{},{})'.format(begadr, endadr + 1)
        return (book_number, begadr, endadr, passage, True, False, False, False)

    def is_variant(self, app):
        labels = []
        for rdg in app.findall('.//{http://www.tei-c.org/ns/1.0}rdg'):
            if rdg.get('type') != 'subreading':
                labels.append(rdg.get('n'))
        real_readings = [x for x in labels if x not in ['zz', 'zu']]
        if len(real_readings) >= 2:
            return True
        return False

    def get_MT_reading(self, app):
        singular = []
        candidate = None
        all_readings = {}
        for rdg in app.findall('./{http://www.tei-c.org/ns/1.0}rdg'):
            if rdg.get('type') != 'subreading':
                label = rdg.get('n')
                all_readings[label] = [x.text for x in rdg.findall('.//{http://www.tei-c.org/ns/1.0}idno')]
            else:
                all_readings[label].extend([x.text for x in rdg.findall('.//{http://www.tei-c.org/ns/1.0}idno')])
        for key in all_readings:
            witness_compare = set(all_readings[key]).intersection(BYZ_WITS)
            if len(witness_compare) >= 8:
                # if we have at least 8 of them (of 9) then this is the MT reading
                return key
            if len(witness_compare) > 1 and len(witness_compare) < 7:
                # then we have no MT and we return a lac 
                # (because if any reading is between 2 and 6 then we won't meet any threshold elsewhere in the app)
                return 'zz'
            if len(witness_compare) == 1:
                singular.append(key)
            if len(witness_compare) == 7:
                candidate = key
        if candidate is not None and len(singular) == 2:
            # if we have 7 reading one thing and the other 2 reading different things then we use the 7 as MT
            return candidate
        return None

    def add_ms_ranges(self, book_number):
        ms_range_insert = """INSERT INTO ms_ranges (rg_id, ms_id, length)
                            VALUES (%s, %s, %s)"""
        self.cursor.execute("""SELECT ms_id FROM manuscripts""")
        ms_ids = [x[0] for x in self.cursor.fetchall()]
        self.cursor.execute("""SELECT rg_id FROM ranges WHERE bk_id = %s""", (book_number,))
        ranges = self.cursor.fetchall()
        for range in ranges:
            range_id = range[0]
            for ms_id in ms_ids:
                self.cursor.execute(ms_range_insert, (range_id, ms_id, 0))
        self.connection.commit()

    def get_chapter_number(self, file_name):
        ch_marker = file_name[:-4].split('_')[-1]
        if ch_marker == 'ins':
            return 0
        if ch_marker == 'sub':
            return 99
        return int(ch_marker.replace('ch', ''))



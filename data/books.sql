--
-- PostgreSQL database dump
--

-- Dumped from database version 12.7 (Debian 12.7-1.pgdg100+1)
-- Dumped by pg_dump version 12.7 (Debian 12.7-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: books; Type: TABLE; Schema: ntg; Owner: ntg
--

CREATE TABLE IF NOT EXISTS ntg.books (
    bk_id integer NOT NULL,
    siglum character varying NOT NULL,
    book character varying NOT NULL,
    passage int4range NOT NULL
);


ALTER TABLE ntg.books OWNER TO ntg;

--
-- Name: books_bk_id_seq; Type: SEQUENCE; Schema: ntg; Owner: ntg
--

CREATE SEQUENCE IF NOT EXISTS ntg.books_bk_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ntg.books_bk_id_seq OWNER TO ntg;

--
-- Name: books_bk_id_seq; Type: SEQUENCE OWNED BY; Schema: ntg; Owner: ntg
--

ALTER SEQUENCE ntg.books_bk_id_seq OWNED BY ntg.books.bk_id;


--
-- Name: books bk_id; Type: DEFAULT; Schema: ntg; Owner: ntg
--

ALTER TABLE ONLY ntg.books ALTER COLUMN bk_id SET DEFAULT nextval('ntg.books_bk_id_seq'::regclass);


--
-- Data for Name: books; Type: TABLE DATA; Schema: ntg; Owner: ntg
--

INSERT INTO ntg.books (bk_id, siglum, book, passage) 
    VALUES  (1, 'Mt', 'Matthew', '[10000000,20000000)'),
            (2, 'Mc', 'Mark', '[20000000,30000000)'),
            (3, 'L',	'Luke', '[30000000,40000000)'),
            (4, 'J',	'John',	'[40000000,50000000)'),
            (5, 'Acts', 'Acts', '[50000000,60000000)'),
            (6, 'R', 'Romans', '[60000000,70000000)'),
            (7, '1K', '1 Corinthians', '[70000000,80000000)'),
            (8, '2K', '2 Corinthians', '[80000000,90000000)'),
            (9, 'G', 'Galatians', '[90000000,100000000)'),
            (10, 'E', 'Ephesians', '[100000000,110000000)'),
            (11, 'Ph', 'Philippians', '[110000000,120000000)'),
            (12, 'Kol', 'Colossians', '[120000000,130000000)'),
            (13, '1Th', '1 Thessalonians', '[130000000,140000000)'),
            (14, '2Th', '2 Thessalonians', '[140000000,150000000)'),
            (15, '1T', '1 Timothy', '[150000000,160000000)'),
            (16, '2T', '2 Timothy', '[160000000,170000000)'),
            (17, 'Tt', 'Titus', '[170000000,180000000)'),
            (18, 'Phm', 'Philemon', '[180000000,190000000)'),
            (19, 'H', 'Hebrews', '[190000000,200000000)'),
            (20, 'Jc', 'James', '[200000000,210000000)'),
            (21, '1P', '1 Peter', '[210000000,220000000)'),
            (22, '2P', '2 Peter', '[220000000,230000000)'),
            (23, '1J', '1 John', '[230000000,240000000)'),
            (24, '2J', '2 John', '[240000000,250000000)'),
            (25, '3J', '3 John', '[250000000,260000000)'),
            (26, 'Jd', 'Jude', '[260000000,270000000)'),
            (27, 'Ap', 'Revelation', '[270000000,280000000)'),
            (210, '2Sam', '2 Samuel', '[2100000000,2110000000)');


--
-- Name: books_bk_id_seq; Type: SEQUENCE SET; Schema: ntg; Owner: ntg
--

SELECT pg_catalog.setval('ntg.books_bk_id_seq', 1, false);


--
-- Name: TABLE books; Type: ACL; Schema: ntg; Owner: ntg
--

GRANT SELECT ON TABLE ntg.books TO ntg_readonly;


--
-- PostgreSQL database dump complete
--


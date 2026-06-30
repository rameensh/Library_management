--
-- PostgreSQL database dump
--

\restrict JEfZ0gLDzOUUamsL4byh7iSuH8JRuZE1s69aWT2CIDzJLproZh03S9RcrEkJcya

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: book_inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book_inventory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    book_id uuid NOT NULL,
    copy_number integer NOT NULL,
    condition character varying(50),
    is_available boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.book_inventory OWNER TO postgres;

--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    id uuid NOT NULL,
    title character varying(300) NOT NULL,
    author character varying(200) NOT NULL,
    isbn character varying(20),
    description character varying,
    genre character varying(80) NOT NULL,
    cover_url character varying,
    has_pdf boolean NOT NULL,
    pdf_url character varying,
    has_audio boolean NOT NULL,
    audio_url character varying,
    has_hardcopy boolean NOT NULL,
    hardcopy_total integer NOT NULL,
    total_pages integer,
    audio_duration_sec integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    hardcopy_available integer NOT NULL
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: hardcopy_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hardcopy_transactions (
    id uuid NOT NULL,
    book_id uuid NOT NULL,
    inventory_id uuid NOT NULL,
    user_id uuid NOT NULL,
    action character varying(20) NOT NULL,
    issued_at timestamp with time zone DEFAULT now(),
    due_date timestamp with time zone,
    returned_at timestamp with time zone,
    delivery_fee double precision,
    delivery_address character varying
);


ALTER TABLE public.hardcopy_transactions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(256) NOT NULL,
    address character varying(200),
    is_private boolean NOT NULL,
    avatar_url character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    role character varying(20) DEFAULT 'user'::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: book_inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.book_inventory (id, book_id, copy_number, condition, is_available, created_at) FROM stdin;
8eb46fd0-e768-4069-8e4e-2380832831c5	cea436e6-a234-4d66-b04c-f48610e3eae5	2	good	t	2026-06-24 14:11:15.913726+05:30
2cd27c71-e05a-4cc9-9144-991dc8435535	cea436e6-a234-4d66-b04c-f48610e3eae5	3	good	t	2026-06-24 14:11:15.913726+05:30
37ec149a-8716-449b-9716-5689526534d8	cea436e6-a234-4d66-b04c-f48610e3eae5	4	good	t	2026-06-24 14:11:15.913726+05:30
74f3f060-c1a2-4f5d-998a-7cdfb3211bf8	cea436e6-a234-4d66-b04c-f48610e3eae5	5	good	t	2026-06-24 14:11:15.913726+05:30
703f0870-9128-42ac-b98f-2eec549bbba2	57984aa0-6c37-4295-a464-fb2d63148505	3	good	t	2026-06-24 14:11:15.913726+05:30
82346f66-9c34-4480-af06-5044948aed01	57984aa0-6c37-4295-a464-fb2d63148505	4	good	t	2026-06-24 14:11:15.913726+05:30
aed5cbb5-21b9-4c73-81c7-2f2f3ac9fef5	57984aa0-6c37-4295-a464-fb2d63148505	5	good	t	2026-06-24 14:11:15.913726+05:30
eb249ce5-e99c-4ecd-8402-4cce9a888254	5fc020e3-b78f-4aaf-9f27-6ed966724f94	5	good	t	2026-06-24 14:11:15.913726+05:30
1bbedcb4-7396-4a67-aa27-e74078846e1b	5a55b15a-9289-4ea3-af5d-eecb490a3bb9	2	good	t	2026-06-24 14:11:15.913726+05:30
5c134e7a-342a-4e77-9fb5-f530958abe45	5a55b15a-9289-4ea3-af5d-eecb490a3bb9	3	good	t	2026-06-24 14:11:15.913726+05:30
f4bae85c-c98b-456f-b12e-f85a760efc24	5a55b15a-9289-4ea3-af5d-eecb490a3bb9	4	good	t	2026-06-24 14:11:15.913726+05:30
62546171-e00b-42cb-a194-317797503b50	a599e46f-c288-43e2-ab58-5c84ce8f0b07	1	good	t	2026-06-24 14:11:15.913726+05:30
fd09a28e-c3fd-4c97-8f46-f7299499bf9d	a599e46f-c288-43e2-ab58-5c84ce8f0b07	2	good	t	2026-06-24 14:11:15.913726+05:30
c33b8b96-3738-4c60-8782-d379e9fa355c	a599e46f-c288-43e2-ab58-5c84ce8f0b07	3	good	t	2026-06-24 14:11:15.913726+05:30
c45e670c-084a-4bca-9226-e5e1fe27bfe4	a599e46f-c288-43e2-ab58-5c84ce8f0b07	4	good	t	2026-06-24 14:11:15.913726+05:30
109097c6-b2f7-4fe6-8e6b-a194e2358e6d	cea436e6-a234-4d66-b04c-f48610e3eae5	1	good	t	2026-06-24 14:11:15.913726+05:30
c6bcb78a-420c-48ef-b17a-7420196c924b	5fc020e3-b78f-4aaf-9f27-6ed966724f94	1	good	t	2026-06-24 14:11:15.913726+05:30
4786a6e3-b6ec-488b-a880-9cd876d0edcb	57984aa0-6c37-4295-a464-fb2d63148505	1	good	f	2026-06-24 14:11:15.913726+05:30
7d81cdde-b5bb-4280-bbeb-84aeedb7e5c3	5fc020e3-b78f-4aaf-9f27-6ed966724f94	2	good	t	2026-06-24 14:11:15.913726+05:30
7a2959c8-7dbe-489a-95cc-c14c58ef0c73	5fc020e3-b78f-4aaf-9f27-6ed966724f94	3	good	t	2026-06-24 14:11:15.913726+05:30
ed0d9eaa-0899-448c-b63e-79372922b91d	57984aa0-6c37-4295-a464-fb2d63148505	2	good	f	2026-06-24 14:11:15.913726+05:30
d9ac006a-153f-452f-bd9e-4815eb6612e6	700e18e5-b647-444e-8552-bbedb3d230f0	2	good	f	2026-06-24 14:11:15.913726+05:30
abe51d68-0031-4b1a-ad3a-6bbe00d74de8	5fc020e3-b78f-4aaf-9f27-6ed966724f94	4	good	t	2026-06-24 14:11:15.913726+05:30
d4a22efb-a793-41de-9c52-d474f52ffd4a	5a55b15a-9289-4ea3-af5d-eecb490a3bb9	1	good	f	2026-06-24 14:11:15.913726+05:30
6e8808e3-7581-4683-b6e9-ed5dce43d32c	700e18e5-b647-444e-8552-bbedb3d230f0	3	good	t	2026-06-24 14:11:15.913726+05:30
891814e0-7a23-4303-a53c-64d7888a768f	700e18e5-b647-444e-8552-bbedb3d230f0	1	good	t	2026-06-24 14:11:15.913726+05:30
\.


--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.books (id, title, author, isbn, description, genre, cover_url, has_pdf, pdf_url, has_audio, audio_url, has_hardcopy, hardcopy_total, total_pages, audio_duration_sec, created_at, hardcopy_available) FROM stdin;
57984aa0-6c37-4295-a464-fb2d63148505	Sapiens	Yuval Noah Harari	9780062316110	A brief history of humankind from the Stone Age to the present.	Science	https://covers.openlibrary.org/b/isbn/9780062316110-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	t	https://your-bucket.r2.dev/sapiens.mp3	t	5	443	57600	2026-06-21 15:12:11.33114+05:30	3
5fc020e3-b78f-4aaf-9f27-6ed966724f94	Gone Girl	Gillian Flynn	9780307588371	A psychological thriller about a husband who becomes a suspect when his wife vanishes.	Mystery	https://covers.openlibrary.org/b/isbn/9780307588371-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	t	https://your-bucket.r2.dev/gone-girl.mp3	t	5	422	52200	2026-06-21 15:12:11.33114+05:30	5
5a55b15a-9289-4ea3-af5d-eecb490a3bb9	The Midnight Library	Matt Haig	9780525559474	Between life and death there is a library, and within that library, the shelves go on forever. Every book provides a chance to try another life you could have lived.	Fiction	https://covers.openlibrary.org/b/isbn/9780525559474-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	t	https://your-bucket.r2.dev/the-midnight-library.mp3	t	4	304	28800	2026-06-21 15:26:41.45114+05:30	3
cea436e6-a234-4d66-b04c-f48610e3eae5	Atomic Habits	James Clear	9780735211292	An easy and proven way to build good habits and break bad ones.	Motivational	https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	t	https://your-bucket.r2.dev/atomic-habits.mp3	t	5	320	19080	2026-06-21 15:12:11.33114+05:30	5
a599e46f-c288-43e2-ab58-5c84ce8f0b07	Elon Musk	Walter Isaacson	9781982181284	The inside story of the world's most controversial entrepreneur.	Biography	https://covers.openlibrary.org/b/isbn/9781982181284-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	t	https://your-bucket.r2.dev/elon-musk.mp3	t	4	688	79200	2026-06-21 15:12:11.33114+05:30	4
700e18e5-b647-444e-8552-bbedb3d230f0	The Alchemist	Paulo Coelho	9780062315007	A philosophical novel about a young Andalusian shepherd's journey.	Fiction	https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg	t	https://raw.githubusercontent.com/mozilla/pdf.js/master/web/compressed.tracemonkey-pldi-09.pdf	f	\N	t	3	208	\N	2026-06-21 15:12:11.33114+05:30	2
\.


--
-- Data for Name: hardcopy_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hardcopy_transactions (id, book_id, inventory_id, user_id, action, issued_at, due_date, returned_at, delivery_fee, delivery_address) FROM stdin;
81d1a7be-e82e-4f97-a5ad-9a8fc279253b	cea436e6-a234-4d66-b04c-f48610e3eae5	109097c6-b2f7-4fe6-8e6b-a194e2358e6d	af073d23-5a61-45ad-a1e3-55d38c221f76	borrowed	2026-06-25 14:54:51.772061+05:30	2026-07-09 14:54:51.807484+05:30	2026-06-25 14:57:17.379284+05:30	0	\N
5afa430a-7816-4da6-b3c8-122245338365	700e18e5-b647-444e-8552-bbedb3d230f0	891814e0-7a23-4303-a53c-64d7888a768f	af073d23-5a61-45ad-a1e3-55d38c221f76	returned	2026-06-25 15:06:10.805005+05:30	2026-07-09 15:06:10.832364+05:30	2026-06-25 15:49:13.205016+05:30	0	\N
20f122fd-13eb-4512-9537-e44622ab8011	5fc020e3-b78f-4aaf-9f27-6ed966724f94	c6bcb78a-420c-48ef-b17a-7420196c924b	df796650-a948-4f2c-a378-11c8c881184f	returned	2026-06-25 23:27:26.759985+05:30	2026-07-09 23:27:26.772923+05:30	2026-06-25 23:28:57.060092+05:30	0	\N
d123e5df-2115-479d-8ff5-74c0cb0b8d02	57984aa0-6c37-4295-a464-fb2d63148505	4786a6e3-b6ec-488b-a880-9cd876d0edcb	df796650-a948-4f2c-a378-11c8c881184f	borrowed	2026-06-25 23:33:56.921652+05:30	2026-07-09 23:33:56.928244+05:30	\N	0	\N
8fad34a2-a16d-4066-b872-082071c48d05	5fc020e3-b78f-4aaf-9f27-6ed966724f94	7d81cdde-b5bb-4280-bbeb-84aeedb7e5c3	661d6997-e3a3-47da-9ce5-cc83bd6fa381	returned	2026-06-25 23:47:45.112827+05:30	2026-07-09 23:47:45.120256+05:30	2026-06-25 23:47:50.781062+05:30	0	\N
1506d235-a99a-432a-80ab-b551a0a47eeb	5fc020e3-b78f-4aaf-9f27-6ed966724f94	7a2959c8-7dbe-489a-95cc-c14c58ef0c73	93789709-3f4f-42e6-bedb-77299387f8b3	returned	2026-06-26 13:51:57.778965+05:30	2026-07-10 13:51:57.798613+05:30	2026-06-26 13:52:24.41237+05:30	0	\N
ac1abf16-354d-4334-8fa2-d4d2f87e350f	57984aa0-6c37-4295-a464-fb2d63148505	ed0d9eaa-0899-448c-b63e-79372922b91d	93789709-3f4f-42e6-bedb-77299387f8b3	borrowed	2026-06-26 13:52:50.672484+05:30	2026-07-10 13:52:50.679677+05:30	\N	0	\N
35a4aa19-ff3f-4b2f-bffe-79467db3e161	700e18e5-b647-444e-8552-bbedb3d230f0	d9ac006a-153f-452f-bd9e-4815eb6612e6	af073d23-5a61-45ad-a1e3-55d38c221f76	borrowed	2026-06-26 14:47:16.217438+05:30	2026-07-10 14:47:16.238954+05:30	\N	0	\N
754ed527-d373-49f6-abe1-a2af14bfea7c	5fc020e3-b78f-4aaf-9f27-6ed966724f94	abe51d68-0031-4b1a-ad3a-6bbe00d74de8	9b36814a-63b3-4b1d-b8fe-a6e06892b3a2	returned	2026-06-27 18:09:12.155859+05:30	2026-07-11 18:09:12.168046+05:30	2026-06-27 18:09:50.796735+05:30	0	\N
6e4d10b9-89ae-4970-8283-5ada5e8bc953	5a55b15a-9289-4ea3-af5d-eecb490a3bb9	d4a22efb-a793-41de-9c52-d474f52ffd4a	9b36814a-63b3-4b1d-b8fe-a6e06892b3a2	borrowed	2026-06-27 18:10:19.866917+05:30	2026-07-11 18:10:19.872961+05:30	\N	0	\N
134db9bc-7a49-427b-abac-ee0be3313544	700e18e5-b647-444e-8552-bbedb3d230f0	6e8808e3-7581-4683-b6e9-ed5dce43d32c	213e6899-445b-4fe2-90e1-19fc772057ba	returned	2026-06-27 18:43:18.000189+05:30	2026-07-11 18:43:18.013459+05:30	2026-06-27 18:44:18.781629+05:30	0	\N
e86836fb-4610-4dd7-a7dc-ae2b01bf2a1b	700e18e5-b647-444e-8552-bbedb3d230f0	891814e0-7a23-4303-a53c-64d7888a768f	213e6899-445b-4fe2-90e1-19fc772057ba	returned	2026-06-27 18:44:32.017249+05:30	2026-07-11 18:44:32.021728+05:30	2026-06-27 18:44:43.541449+05:30	0	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, address, is_private, avatar_url, created_at, role) FROM stdin;
58a909ce-125f-4dd5-97d5-a946c9e37bd1	Zeba	alia12@gmail.com	$2b$12$eSP6Pb0anDOCkpnzoz0MMeyVIfN4ETUsqc7uwQUoSZUVXtoVopJLC	111/15 Ruia apartment juhu	t	https://randomuser.me/api/portraits/women/44.jpg	2026-06-22 12:28:30.433243+05:30	user
835a8917-86ff-4c1e-b4d1-7fb8be8d7844	Rameen	rim123@gmail.com	$2b$12$5eoc30w7UF8uaDNR5t398eGLpmNBOqt4VjPBccMb56SUBo1q2a	123 main street juhu	f	https://randomuser.me/api/portraits/women/45.jpg	2026-06-22 13:45:10.913995+05:30	admin
af073d23-5a61-45ad-a1e3-55d38c221f76	Nairah	nairah@gmail.com	$2b$12$RY6b9Ca4jcgknjTyfFFfKOICM/qCDt1CMHh.SnBwV.r1dcty47jwG	xyz	f	hello	2026-06-23 14:33:22.470906+05:30	admin
15f07499-2c12-4677-be01-bb3257b9df1c	Arham	arham123@gmail.com	$2b$12$dJ21bd2HPKrKjHait9u9puaVb2/34x.HQO8GliPp43R5/11qXxLee	Mumbai xyz	f	https://www.magnific.com/free-vector/smiling-young-man-illustration_336635642.htm#fromView=keyword&page=1&position=0&uuid=3c9a5222-b727-4905-9f09-ca2c7e33eb90&query=Man+avatar	2026-06-24 12:46:32.75657+05:30	user
df796650-a948-4f2c-a378-11c8c881184f	Arkam	arkam12@gmail.com	$2b$12$QJNX6u6b7YXoE0DpBQMsxOIzo9tJKIv5dg0cTqfBAAHxuphsTv/sG	abc	f	\N	2026-06-25 22:48:44.443814+05:30	user
661d6997-e3a3-47da-9ce5-cc83bd6fa381	mishquat	mish@gmail.com	$2b$12$knmX.Y0NzZMQjH9C3TRuTuwu/dUjCt/y99MEtFBH1ziwTkK.r8Fgm	fvfsfsf	t	\N	2026-06-25 23:16:52.055529+05:30	user
93789709-3f4f-42e6-bedb-77299387f8b3	Insha	insha123@gmail.com	$2b$12$ouYjF9VDOjTQIrsxdHQH8uT6OhK2eXTJ24r4QKGYo4OU4vh3r24Qu	dsjvshjb	f	https://www.google.com/imgres?q=give%20me%20a%20profile%20url%20for%20female&imgurl=https%3A%2F%2Fimg.magnific.com%2Ffree-vector%2Fwoman-with-long-brown-hair-pink-shirt_90220-2940.jpg%3Fsemt%3Dais_hybrid%26w%3D740%26q%3D80&imgrefurl=https%3A%2F%2Fwww.magnific.com%2Ffree-photos-vectors%2Fwoman-profile&docid=6fNJFTEJEnyCkM&tbnid=trMHiyxw6413xM&vet=12ahUKEwjC6tTVnaSVAxWpoGMGHT2DDUEQnPAOegQINxAA..i&w=740&h=740&hcb=2&ved=2ahUKEwjC6tTVnaSVAxWpoGMGHT2DDUEQnPAOegQINxAA	2026-06-26 11:32:52.672764+05:30	user
9b36814a-63b3-4b1d-b8fe-a6e06892b3a2	Zuhair	arham1223@gmail.com	$2b$12$K7rEZUvhJnZkPGJc7eQH6OpJjHAiB/RtuP54EZTFo8.CzulJaRoTK	dnvbj	f	\N	2026-06-27 17:58:56.90478+05:30	user
213e6899-445b-4fe2-90e1-19fc772057ba	Joe	joe1234@gmail.com	$2b$12$HLgu4Z7BQ7ZVwDyksEFhCejKxvnaDppmEI/irRydlNDjsykkl0Yeq	dgg	t	\N	2026-06-27 18:31:19.679584+05:30	user
\.


--
-- Name: book_inventory book_inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_inventory
    ADD CONSTRAINT book_inventory_pkey PRIMARY KEY (id);


--
-- Name: books books_isbn_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_isbn_key UNIQUE (isbn);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);


--
-- Name: hardcopy_transactions hardcopy_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hardcopy_transactions
    ADD CONSTRAINT hardcopy_transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_books_author; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_books_author ON public.books USING btree (author);


--
-- Name: ix_books_genre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_books_genre ON public.books USING btree (genre);


--
-- Name: ix_books_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_books_title ON public.books USING btree (title);


--
-- Name: book_inventory book_inventory_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_inventory
    ADD CONSTRAINT book_inventory_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: hardcopy_transactions hardcopy_transactions_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hardcopy_transactions
    ADD CONSTRAINT hardcopy_transactions_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: hardcopy_transactions hardcopy_transactions_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hardcopy_transactions
    ADD CONSTRAINT hardcopy_transactions_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.book_inventory(id);


--
-- Name: hardcopy_transactions hardcopy_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hardcopy_transactions
    ADD CONSTRAINT hardcopy_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict JEfZ0gLDzOUUamsL4byh7iSuH8JRuZE1s69aWT2CIDzJLproZh03S9RcrEkJcya


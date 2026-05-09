-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.act_books (
  id integer NOT NULL DEFAULT nextval('act_books_id_seq'::regclass),
  act_id integer,
  book_number integer,
  book_title text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT act_books_pkey PRIMARY KEY (id),
  CONSTRAINT act_books_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id)
);
CREATE TABLE public.act_groups (
  id integer NOT NULL DEFAULT nextval('act_groups_id_seq'::regclass),
  act_id integer,
  book_id integer,
  group_number integer,
  group_title text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT act_groups_pkey PRIMARY KEY (id),
  CONSTRAINT act_groups_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id),
  CONSTRAINT act_groups_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.act_books(id)
);
CREATE TABLE public.act_section_tags (
  act_section_id integer NOT NULL,
  tag_id integer NOT NULL,
  CONSTRAINT act_section_tags_pkey PRIMARY KEY (act_section_id, tag_id),
  CONSTRAINT act_section_tags_act_section_id_fkey FOREIGN KEY (act_section_id) REFERENCES public.act_sections(id),
  CONSTRAINT act_section_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE public.act_sections (
  id integer NOT NULL DEFAULT nextval('act_sections_id_seq'::regclass),
  act_id integer,
  book_id integer,
  group_id integer,
  super_id integer,
  section_number integer,
  sub_section text,
  paragraph_number integer,
  item_order text,
  text_original text,
  text_processed text,
  embedding USER-DEFINED,
  cross_references json,
  external_citations json,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT act_sections_pkey PRIMARY KEY (id),
  CONSTRAINT act_sections_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id),
  CONSTRAINT act_sections_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.act_books(id),
  CONSTRAINT act_sections_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.act_groups(id),
  CONSTRAINT act_sections_super_id_fkey FOREIGN KEY (super_id) REFERENCES public.act_super_sections(id)
);
CREATE TABLE public.act_super_sections (
  id integer NOT NULL DEFAULT nextval('act_super_sections_id_seq'::regclass),
  act_id integer,
  group_id integer,
  super_number integer,
  super_title text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT act_super_sections_pkey PRIMARY KEY (id),
  CONSTRAINT act_super_sections_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id),
  CONSTRAINT act_super_sections_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.act_groups(id)
);
CREATE TABLE public.act_tags (
  act_id integer NOT NULL,
  tag_id integer NOT NULL,
  CONSTRAINT act_tags_pkey PRIMARY KEY (act_id, tag_id),
  CONSTRAINT act_tags_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id),
  CONSTRAINT act_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE public.acts (
  id integer NOT NULL DEFAULT nextval('acts_id_seq'::regclass),
  title text NOT NULL,
  preface text,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT acts_pkey PRIMARY KEY (id)
);
CREATE TABLE public.chat_messages (
  id integer NOT NULL DEFAULT nextval('chat_messages_id_seq'::regclass),
  room_id integer,
  sender text CHECK (sender = ANY (ARRAY['user'::text, 'bot'::text])),
  message text,
  created_at timestamp without time zone DEFAULT now(),
  metadata jsonb,
  CONSTRAINT chat_messages_pkey PRIMARY KEY (id),
  CONSTRAINT chat_messages_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.chat_rooms(id)
);
CREATE TABLE public.chat_rooms (
  id integer NOT NULL DEFAULT nextval('chat_rooms_id_seq'::regclass),
  user_id uuid,
  title text,
  is_archive boolean,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT chat_rooms_pkey PRIMARY KEY (id),
  CONSTRAINT chat_rooms_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.citations (
  act_id integer NOT NULL,
  reference_number integer NOT NULL,
  citation_text text,
  imported_at timestamp without time zone DEFAULT now(),
  CONSTRAINT citations_pkey PRIMARY KEY (act_id, reference_number),
  CONSTRAINT citations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id)
);
CREATE TABLE public.job (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  description text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT job_pkey PRIMARY KEY (id)
);
CREATE TABLE public.job_type (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  description text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT job_type_pkey PRIMARY KEY (id)
);
CREATE TABLE public.judgment_tags (
  judgment_id integer NOT NULL,
  tag_id integer NOT NULL,
  CONSTRAINT judgment_tags_pkey PRIMARY KEY (judgment_id, tag_id),
  CONSTRAINT judgment_tags_judgment_id_fkey FOREIGN KEY (judgment_id) REFERENCES public.judgments(id),
  CONSTRAINT judgment_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE public.judgments (
  id integer NOT NULL DEFAULT nextval('judgments_id_seq'::regclass),
  title text NOT NULL,
  case_number text,
  summary text,
  summary_embedding USER-DEFINED,
  detail text,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT judgments_pkey PRIMARY KEY (id)
);
CREATE TABLE public.tags (
  id integer NOT NULL DEFAULT nextval('tags_id_seq'::regclass),
  name text NOT NULL UNIQUE,
  description text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT tags_pkey PRIMARY KEY (id)
);
CREATE TABLE public.users (
  id uuid NOT NULL,
  display_name text,
  avatar_url text,
  role text DEFAULT 'user'::text,
  detail text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  date_of_birth date,
  job_id bigint,
  start_work_date date,
  job_type_id bigint,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id),
  CONSTRAINT users_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.job(id),
  CONSTRAINT users_job_type_id_fkey FOREIGN KEY (job_type_id) REFERENCES public.job_type(id)
);
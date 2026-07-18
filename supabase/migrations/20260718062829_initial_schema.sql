-- Sahaay MVP schema (matches backend/app/models.py)

create table public.sessions (
  id text primary key,
  user_name varchar(120),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.messages (
  id bigint generated always as identity primary key,
  session_id text not null references public.sessions (id) on delete cascade,
  role varchar(20) not null,
  content text not null,
  created_at timestamptz not null default now()
);

create index messages_session_id_idx on public.messages (session_id);

create table public.routines (
  id bigint generated always as identity primary key,
  session_id text not null references public.sessions (id) on delete cascade,
  name varchar(200) not null,
  type varchar(50) not null default 'habit',
  timing varchar(50),
  frequency varchar(50) not null default 'daily',
  notes text,
  priority varchar(20) not null default 'normal',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index routines_session_id_idx on public.routines (session_id);

create table public.reminders (
  id bigint generated always as identity primary key,
  session_id text not null references public.sessions (id) on delete cascade,
  routine_id bigint references public.routines (id) on delete set null,
  message text not null,
  scheduled_time varchar(50),
  is_demo boolean not null default false,
  created_at timestamptz not null default now()
);

create index reminders_session_id_idx on public.reminders (session_id);

-- RLS: enabled on all public tables. Backend connects via Postgres (bypasses RLS).
-- Frontend anon key has no policies until auth is added.
alter table public.sessions enable row level security;
alter table public.messages enable row level security;
alter table public.routines enable row level security;
alter table public.reminders enable row level security;

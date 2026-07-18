-- Rebuild the empty hackathon schema for the web-first Sahaay MVP.
-- This migration deliberately refuses to remove legacy data if any exists.

do $$
declare
  legacy_table text;
  has_rows boolean;
begin
  foreach legacy_table in array array['messages', 'routines', 'reminders', 'sessions']
  loop
    if to_regclass(format('public.%I', legacy_table)) is not null then
      execute format('select exists (select 1 from public.%I limit 1)', legacy_table)
        into has_rows;
      if has_rows then
        raise exception
          'Cannot replace legacy table public.% because it contains data',
          legacy_table;
      end if;
    end if;
  end loop;
end
$$;

drop table if exists public.messages;
drop table if exists public.reminders;
drop table if exists public.routines;
drop table if exists public.sessions;

create schema if not exists private;
revoke all on schema private from public;

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text not null check (length(btrim(full_name)) between 1 and 150),
  email text,
  phone text,
  avatar_url text,
  account_type text not null default 'family'
    check (account_type in ('family', 'elder', 'both')),
  preferred_language text not null default 'en'
    check (preferred_language in ('en', 'hi', 'gu')),
  timezone text not null default 'Asia/Kolkata',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (email is null or length(btrim(email)) between 3 and 320)
);

create unique index profiles_email_lower_uidx
  on public.profiles (lower(email))
  where email is not null;

create table public.families (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users (id) on delete restrict,
  name text not null check (length(btrim(name)) between 1 and 120),
  description text,
  timezone text not null default 'Asia/Kolkata',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index families_owner_id_idx on public.families (owner_id);

create table public.invitations (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  invited_by uuid not null references auth.users (id) on delete restrict,
  email text not null check (length(btrim(email)) between 3 and 320),
  role text not null default 'member'
    check (role in ('admin', 'caregiver', 'member')),
  token uuid not null default gen_random_uuid(),
  status text not null default 'pending'
    check (status in ('pending', 'accepted', 'declined', 'revoked', 'expired')),
  expires_at timestamptz not null default (now() + interval '7 days'),
  accepted_by uuid references auth.users (id) on delete set null,
  accepted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (token),
  check (
    (status = 'accepted' and accepted_by is not null and accepted_at is not null)
    or status <> 'accepted'
  )
);

create index invitations_family_id_idx on public.invitations (family_id);
create index invitations_invited_by_idx on public.invitations (invited_by);
create index invitations_accepted_by_idx on public.invitations (accepted_by);
create index invitations_email_lower_idx on public.invitations (lower(email));
create index invitations_pending_expiry_idx
  on public.invitations (expires_at)
  where status = 'pending';

create table public.family_members (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  invitation_id uuid references public.invitations (id) on delete set null,
  role text not null default 'member'
    check (role in ('owner', 'admin', 'caregiver', 'member')),
  status text not null default 'active'
    check (status in ('active', 'inactive')),
  joined_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (family_id, user_id)
);

create index family_members_user_id_idx on public.family_members (user_id);
create index family_members_invitation_id_idx on public.family_members (invitation_id);
create index family_members_family_status_idx
  on public.family_members (family_id, status);

create table public.elder_profiles (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  user_id uuid unique references auth.users (id) on delete set null,
  created_by uuid not null references auth.users (id) on delete restrict,
  full_name text not null check (length(btrim(full_name)) between 1 and 150),
  photo_url text,
  date_of_birth date,
  gender text check (gender is null or gender in ('female', 'male', 'non_binary', 'other', 'prefer_not_to_say')),
  emergency_contact_name text,
  emergency_contact_phone text,
  emergency_contact_relationship text,
  medical_notes text,
  preferred_language text not null default 'en'
    check (preferred_language in ('en', 'hi', 'gu')),
  timezone text not null default 'Asia/Kolkata',
  consent_to_family_monitoring boolean not null default true,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (date_of_birth is null or date_of_birth <= current_date)
);

create index elder_profiles_family_id_idx on public.elder_profiles (family_id);
create index elder_profiles_created_by_idx on public.elder_profiles (created_by);

create table public.reminders (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  assigned_by uuid not null references auth.users (id) on delete restrict,
  type text not null
    check (type in ('medicine', 'meal', 'sleep', 'appointment', 'exercise', 'hydration', 'other')),
  title text not null check (length(btrim(title)) between 1 and 200),
  description text,
  note text,
  local_time time not null,
  timezone text not null default 'Asia/Kolkata',
  start_date date not null default current_date,
  end_date date,
  frequency text not null default 'daily'
    check (frequency in ('once', 'daily', 'weekly', 'monthly', 'custom')),
  repeat_rule jsonb not null default '{}'::jsonb
    check (jsonb_typeof(repeat_rule) = 'object'),
  status text not null default 'active'
    check (status in ('active', 'paused', 'completed', 'archived')),
  escalation_after_minutes integer not null default 60
    check (escalation_after_minutes between 0 and 10080),
  max_retries smallint not null default 2 check (max_retries between 0 and 20),
  next_run_at timestamptz,
  last_run_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (end_date is null or end_date >= start_date)
);

create index reminders_elder_id_idx on public.reminders (elder_id);
create index reminders_assigned_by_idx on public.reminders (assigned_by);
create index reminders_due_idx
  on public.reminders (next_run_at)
  where status = 'active';
create index reminders_elder_status_idx
  on public.reminders (elder_id, status);

create table public.reminder_completions (
  id uuid primary key default gen_random_uuid(),
  reminder_id uuid not null references public.reminders (id) on delete cascade,
  scheduled_for timestamptz not null,
  status text not null default 'completed'
    check (status in ('completed', 'skipped', 'missed')),
  completed_at timestamptz,
  completed_by uuid references auth.users (id) on delete set null,
  response_text text,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (reminder_id, scheduled_for),
  check (
    (status = 'completed' and completed_at is not null)
    or status <> 'completed'
  )
);

create index reminder_completions_completed_by_idx
  on public.reminder_completions (completed_by);
create index reminder_completions_scheduled_for_idx
  on public.reminder_completions (scheduled_for);
create index reminder_completions_status_idx
  on public.reminder_completions (status, scheduled_for);

create table public.activities (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  actor_id uuid references auth.users (id) on delete set null,
  activity_type text not null
    check (activity_type in (
      'reminder_created', 'reminder_sent', 'reminder_completed',
      'reminder_missed', 'wellness_check', 'ai_conversation',
      'notification', 'sos', 'profile_update', 'other'
    )),
  title text not null check (length(btrim(title)) between 1 and 200),
  description text,
  source text not null default 'system'
    check (source in ('user', 'family', 'ai', 'system')),
  occurred_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now()
);

create index activities_elder_id_idx on public.activities (elder_id);
create index activities_actor_id_idx on public.activities (actor_id);
create index activities_elder_occurred_idx
  on public.activities (elder_id, occurred_at desc);

create table public.wellness_checks (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  recorded_by uuid references auth.users (id) on delete set null,
  check_date date not null default current_date,
  mood smallint check (mood is null or mood between 1 and 5),
  mood_label text,
  sleep_quality smallint check (sleep_quality is null or sleep_quality between 1 and 5),
  sleep_hours numeric(4,2) check (sleep_hours is null or sleep_hours between 0 and 24),
  had_breakfast boolean,
  pain_level smallint check (pain_level is null or pain_level between 0 and 10),
  drank_enough_water boolean,
  notes text,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (elder_id, check_date)
);

create index wellness_checks_recorded_by_idx on public.wellness_checks (recorded_by);
create index wellness_checks_elder_date_idx
  on public.wellness_checks (elder_id, check_date desc);

create table public.ai_conversations (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  started_by uuid references auth.users (id) on delete set null,
  title text,
  status text not null default 'active'
    check (status in ('active', 'closed', 'archived')),
  summary text,
  memory jsonb not null default '{}'::jsonb
    check (jsonb_typeof(memory) = 'object'),
  last_message_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index ai_conversations_elder_id_idx on public.ai_conversations (elder_id);
create index ai_conversations_started_by_idx on public.ai_conversations (started_by);
create index ai_conversations_elder_recent_idx
  on public.ai_conversations (elder_id, last_message_at desc);

create table public.ai_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.ai_conversations (id) on delete cascade,
  sender_id uuid references auth.users (id) on delete set null,
  role text not null check (role in ('system', 'user', 'assistant', 'tool')),
  content text not null check (length(content) > 0),
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now()
);

create index ai_messages_conversation_id_idx on public.ai_messages (conversation_id);
create index ai_messages_sender_id_idx on public.ai_messages (sender_id);
create index ai_messages_conversation_created_idx
  on public.ai_messages (conversation_id, created_at);

create table public.device_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  token text not null unique check (length(token) > 20),
  platform text not null check (platform in ('web', 'android', 'ios')),
  device_name text,
  is_active boolean not null default true,
  last_used_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index device_tokens_user_id_idx on public.device_tokens (user_id);
create index device_tokens_active_user_idx
  on public.device_tokens (user_id)
  where is_active;

create table public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  elder_id uuid references public.elder_profiles (id) on delete cascade,
  type text not null
    check (type in ('reminder', 'family_alert', 'sos', 'appointment', 'daily_summary', 'emergency', 'wellness')),
  title text not null check (length(btrim(title)) between 1 and 200),
  body text not null,
  data jsonb not null default '{}'::jsonb
    check (jsonb_typeof(data) = 'object'),
  status text not null default 'pending'
    check (status in ('pending', 'sent', 'delivered', 'read', 'failed')),
  scheduled_at timestamptz,
  sent_at timestamptz,
  delivered_at timestamptz,
  read_at timestamptz,
  failure_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index notifications_user_id_idx on public.notifications (user_id);
create index notifications_elder_id_idx on public.notifications (elder_id);
create index notifications_user_created_idx
  on public.notifications (user_id, created_at desc);
create index notifications_delivery_queue_idx
  on public.notifications (scheduled_at)
  where status = 'pending';

create table public.health_scores (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  score smallint not null check (score between 0 and 100),
  score_date date not null default current_date,
  medicine_score smallint check (medicine_score is null or medicine_score between 0 and 100),
  meal_score smallint check (meal_score is null or meal_score between 0 and 100),
  sleep_score smallint check (sleep_score is null or sleep_score between 0 and 100),
  mood_score smallint check (mood_score is null or mood_score between 0 and 100),
  activity_score smallint check (activity_score is null or activity_score between 0 and 100),
  adherence_score smallint check (adherence_score is null or adherence_score between 0 and 100),
  factors jsonb not null default '{}'::jsonb
    check (jsonb_typeof(factors) = 'object'),
  insights jsonb not null default '[]'::jsonb
    check (jsonb_typeof(insights) = 'array'),
  generated_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (elder_id, score_date)
);

create index health_scores_elder_generated_idx
  on public.health_scores (elder_id, generated_at desc);

create table public.sos_alerts (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references public.elder_profiles (id) on delete cascade,
  triggered_by uuid references auth.users (id) on delete set null,
  status text not null default 'active'
    check (status in ('active', 'acknowledged', 'resolved', 'cancelled')),
  message text,
  latitude numeric(9,6) check (latitude is null or latitude between -90 and 90),
  longitude numeric(9,6) check (longitude is null or longitude between -180 and 180),
  location_accuracy_meters numeric(10,2)
    check (location_accuracy_meters is null or location_accuracy_meters >= 0),
  acknowledged_by uuid references auth.users (id) on delete set null,
  acknowledged_at timestamptz,
  resolved_by uuid references auth.users (id) on delete set null,
  resolved_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    (status in ('acknowledged', 'resolved') and acknowledged_at is not null)
    or status not in ('acknowledged', 'resolved')
  ),
  check (
    (status = 'resolved' and resolved_at is not null)
    or status <> 'resolved'
  )
);

create index sos_alerts_elder_id_idx on public.sos_alerts (elder_id);
create index sos_alerts_triggered_by_idx on public.sos_alerts (triggered_by);
create index sos_alerts_acknowledged_by_idx on public.sos_alerts (acknowledged_by);
create index sos_alerts_resolved_by_idx on public.sos_alerts (resolved_by);
create index sos_alerts_active_idx
  on public.sos_alerts (created_at desc)
  where status in ('active', 'acknowledged');

create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references auth.users (id) on delete set null,
  family_id uuid references public.families (id) on delete set null,
  elder_id uuid references public.elder_profiles (id) on delete set null,
  action text not null check (length(btrim(action)) between 1 and 120),
  entity_type text not null check (length(btrim(entity_type)) between 1 and 80),
  entity_id uuid,
  old_values jsonb check (old_values is null or jsonb_typeof(old_values) = 'object'),
  new_values jsonb check (new_values is null or jsonb_typeof(new_values) = 'object'),
  ip_address inet,
  user_agent text,
  created_at timestamptz not null default now()
);

create index audit_logs_actor_id_idx on public.audit_logs (actor_id);
create index audit_logs_family_id_idx on public.audit_logs (family_id);
create index audit_logs_elder_id_idx on public.audit_logs (elder_id);
create index audit_logs_family_created_idx
  on public.audit_logs (family_id, created_at desc);
create index audit_logs_entity_idx
  on public.audit_logs (entity_type, entity_id);

-- Authorization helpers live outside the exposed public schema. They bypass RLS
-- only for narrowly-scoped membership checks, preventing recursive policies on
-- family_members and elder_profiles.
create or replace function private.is_family_member(
  target_family_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and (
    exists (
      select 1
      from public.families f
      where f.id = target_family_id
        and f.owner_id = target_user_id
    )
    or exists (
      select 1
      from public.family_members fm
      where fm.family_id = target_family_id
        and fm.user_id = target_user_id
        and fm.status = 'active'
    )
  );
$$;

create or replace function private.is_family_owner(
  target_family_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and exists (
    select 1
    from public.families f
    where f.id = target_family_id
      and f.owner_id = target_user_id
  );
$$;

create or replace function private.shares_family(
  other_user_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and other_user_id is not null and exists (
    select 1
    from public.families f
    where private.is_family_member(f.id, target_user_id)
      and private.is_family_member(f.id, other_user_id)
  );
$$;

create or replace function private.can_access_elder(
  target_elder_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and exists (
    select 1
    from public.elder_profiles ep
    where ep.id = target_elder_id
      and (
        ep.user_id = target_user_id
        or private.is_family_member(ep.family_id, target_user_id)
      )
  );
$$;

create or replace function private.can_manage_elder(
  target_elder_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and exists (
    select 1
    from public.elder_profiles ep
    where ep.id = target_elder_id
      and private.is_family_member(ep.family_id, target_user_id)
  );
$$;

create or replace function private.can_access_reminder(
  target_reminder_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and exists (
    select 1
    from public.reminders r
    where r.id = target_reminder_id
      and private.can_access_elder(r.elder_id, target_user_id)
  );
$$;

create or replace function private.can_access_conversation(
  target_conversation_id uuid,
  target_user_id uuid default auth.uid()
)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select target_user_id is not null and exists (
    select 1
    from public.ai_conversations c
    where c.id = target_conversation_id
      and private.can_access_elder(c.elder_id, target_user_id)
  );
$$;

create or replace function private.is_invitation_recipient(invitation_email text)
returns boolean
language sql
stable
security invoker
set search_path = ''
as $$
  select auth.uid() is not null
    and lower(coalesce(auth.jwt() ->> 'email', '')) = lower(invitation_email);
$$;

create or replace function private.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

revoke all on all functions in schema private from public;
grant usage on schema private to authenticated;
grant execute on function private.is_family_member(uuid, uuid) to authenticated;
grant execute on function private.is_family_owner(uuid, uuid) to authenticated;
grant execute on function private.shares_family(uuid, uuid) to authenticated;
grant execute on function private.can_access_elder(uuid, uuid) to authenticated;
grant execute on function private.can_manage_elder(uuid, uuid) to authenticated;
grant execute on function private.can_access_reminder(uuid, uuid) to authenticated;
grant execute on function private.can_access_conversation(uuid, uuid) to authenticated;
grant execute on function private.is_invitation_recipient(text) to authenticated;

create trigger profiles_set_updated_at before update on public.profiles
  for each row execute function private.set_updated_at();
create trigger families_set_updated_at before update on public.families
  for each row execute function private.set_updated_at();
create trigger invitations_set_updated_at before update on public.invitations
  for each row execute function private.set_updated_at();
create trigger family_members_set_updated_at before update on public.family_members
  for each row execute function private.set_updated_at();
create trigger elder_profiles_set_updated_at before update on public.elder_profiles
  for each row execute function private.set_updated_at();
create trigger reminders_set_updated_at before update on public.reminders
  for each row execute function private.set_updated_at();
create trigger reminder_completions_set_updated_at before update on public.reminder_completions
  for each row execute function private.set_updated_at();
create trigger wellness_checks_set_updated_at before update on public.wellness_checks
  for each row execute function private.set_updated_at();
create trigger ai_conversations_set_updated_at before update on public.ai_conversations
  for each row execute function private.set_updated_at();
create trigger device_tokens_set_updated_at before update on public.device_tokens
  for each row execute function private.set_updated_at();
create trigger notifications_set_updated_at before update on public.notifications
  for each row execute function private.set_updated_at();
create trigger health_scores_set_updated_at before update on public.health_scores
  for each row execute function private.set_updated_at();
create trigger sos_alerts_set_updated_at before update on public.sos_alerts
  for each row execute function private.set_updated_at();

alter table public.profiles enable row level security;
alter table public.families enable row level security;
alter table public.family_members enable row level security;
alter table public.invitations enable row level security;
alter table public.elder_profiles enable row level security;
alter table public.reminders enable row level security;
alter table public.reminder_completions enable row level security;
alter table public.activities enable row level security;
alter table public.wellness_checks enable row level security;
alter table public.ai_conversations enable row level security;
alter table public.ai_messages enable row level security;
alter table public.device_tokens enable row level security;
alter table public.notifications enable row level security;
alter table public.health_scores enable row level security;
alter table public.sos_alerts enable row level security;
alter table public.audit_logs enable row level security;

-- Profiles: users manage themselves; family peers may read identity details.
create policy profiles_select on public.profiles for select to authenticated
  using (
    id = (select auth.uid())
    or private.shares_family(id, (select auth.uid()))
  );
create policy profiles_insert on public.profiles for insert to authenticated
  with check (
    id = (select auth.uid())
    and (
      email is null
      or lower(email) = lower(coalesce((select auth.jwt() ->> 'email'), ''))
    )
  );
create policy profiles_update on public.profiles for update to authenticated
  using (id = (select auth.uid()))
  with check (
    id = (select auth.uid())
    and (
      email is null
      or lower(email) = lower(coalesce((select auth.jwt() ->> 'email'), ''))
    )
  );
create policy profiles_delete on public.profiles for delete to authenticated
  using (id = (select auth.uid()));

-- Family ownership is immutable through RLS because both USING and WITH CHECK
-- require the current user to remain the owner.
create policy families_select on public.families for select to authenticated
  using (private.is_family_member(id, (select auth.uid())));
create policy families_insert on public.families for insert to authenticated
  with check (owner_id = (select auth.uid()));
create policy families_update on public.families for update to authenticated
  using (private.is_family_owner(id, (select auth.uid())))
  with check (owner_id = (select auth.uid()));
create policy families_delete on public.families for delete to authenticated
  using (private.is_family_owner(id, (select auth.uid())));

create policy family_members_select on public.family_members for select to authenticated
  using (
    user_id = (select auth.uid())
    or private.is_family_member(family_id, (select auth.uid()))
  );
create policy family_members_insert on public.family_members for insert to authenticated
  with check (private.is_family_owner(family_id, (select auth.uid())));
create policy family_members_update on public.family_members for update to authenticated
  using (private.is_family_owner(family_id, (select auth.uid())))
  with check (private.is_family_owner(family_id, (select auth.uid())));
create policy family_members_delete on public.family_members for delete to authenticated
  using (
    private.is_family_owner(family_id, (select auth.uid()))
    or user_id = (select auth.uid())
  );

create policy invitations_select on public.invitations for select to authenticated
  using (
    private.is_family_owner(family_id, (select auth.uid()))
    or private.is_invitation_recipient(email)
  );
create policy invitations_insert on public.invitations for insert to authenticated
  with check (
    private.is_family_owner(family_id, (select auth.uid()))
    and invited_by = (select auth.uid())
  );
create policy invitations_update on public.invitations for update to authenticated
  using (private.is_family_owner(family_id, (select auth.uid())))
  with check (private.is_family_owner(family_id, (select auth.uid())));
create policy invitations_delete on public.invitations for delete to authenticated
  using (private.is_family_owner(family_id, (select auth.uid())));

create policy elder_profiles_select on public.elder_profiles for select to authenticated
  using (private.can_access_elder(id, (select auth.uid())));
create policy elder_profiles_insert on public.elder_profiles for insert to authenticated
  with check (
    private.is_family_member(family_id, (select auth.uid()))
    and created_by = (select auth.uid())
  );
create policy elder_profiles_update on public.elder_profiles for update to authenticated
  using (private.can_manage_elder(id, (select auth.uid())))
  with check (private.is_family_member(family_id, (select auth.uid())));
create policy elder_profiles_delete on public.elder_profiles for delete to authenticated
  using (private.is_family_owner(family_id, (select auth.uid())));

create policy reminders_select on public.reminders for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));
create policy reminders_insert on public.reminders for insert to authenticated
  with check (
    private.can_manage_elder(elder_id, (select auth.uid()))
    and assigned_by = (select auth.uid())
  );
create policy reminders_update on public.reminders for update to authenticated
  using (private.can_manage_elder(elder_id, (select auth.uid())))
  with check (private.can_manage_elder(elder_id, (select auth.uid())));
create policy reminders_delete on public.reminders for delete to authenticated
  using (private.can_manage_elder(elder_id, (select auth.uid())));

create policy reminder_completions_select
  on public.reminder_completions for select to authenticated
  using (private.can_access_reminder(reminder_id, (select auth.uid())));
create policy reminder_completions_insert
  on public.reminder_completions for insert to authenticated
  with check (
    private.can_access_reminder(reminder_id, (select auth.uid()))
    and completed_by = (select auth.uid())
    and status in ('completed', 'skipped')
  );
create policy reminder_completions_update
  on public.reminder_completions for update to authenticated
  using (private.can_access_reminder(reminder_id, (select auth.uid())))
  with check (
    private.can_access_reminder(reminder_id, (select auth.uid()))
    and completed_by = (select auth.uid())
    and status in ('completed', 'skipped')
  );
create policy reminder_completions_delete
  on public.reminder_completions for delete to authenticated
  using (
    exists (
      select 1
      from public.reminders r
      where r.id = reminder_id
        and private.can_manage_elder(r.elder_id, (select auth.uid()))
    )
  );

create policy activities_select on public.activities for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));
create policy activities_insert on public.activities for insert to authenticated
  with check (
    private.can_access_elder(elder_id, (select auth.uid()))
    and actor_id = (select auth.uid())
    and (
      source = 'user'
      or (
        source = 'family'
        and private.can_manage_elder(elder_id, (select auth.uid()))
      )
    )
  );

create policy wellness_checks_select on public.wellness_checks for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));
create policy wellness_checks_insert on public.wellness_checks for insert to authenticated
  with check (
    private.can_access_elder(elder_id, (select auth.uid()))
    and recorded_by = (select auth.uid())
  );
create policy wellness_checks_update on public.wellness_checks for update to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())))
  with check (
    private.can_access_elder(elder_id, (select auth.uid()))
    and recorded_by = (select auth.uid())
  );
create policy wellness_checks_delete on public.wellness_checks for delete to authenticated
  using (private.can_manage_elder(elder_id, (select auth.uid())));

create policy ai_conversations_select on public.ai_conversations for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));
create policy ai_conversations_insert on public.ai_conversations for insert to authenticated
  with check (
    private.can_access_elder(elder_id, (select auth.uid()))
    and started_by = (select auth.uid())
  );
create policy ai_conversations_update on public.ai_conversations for update to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())))
  with check (private.can_access_elder(elder_id, (select auth.uid())));
create policy ai_conversations_delete on public.ai_conversations for delete to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));

create policy ai_messages_select on public.ai_messages for select to authenticated
  using (private.can_access_conversation(conversation_id, (select auth.uid())));
create policy ai_messages_insert on public.ai_messages for insert to authenticated
  with check (
    private.can_access_conversation(conversation_id, (select auth.uid()))
    and sender_id = (select auth.uid())
    and role = 'user'
  );

create policy device_tokens_select on public.device_tokens for select to authenticated
  using (user_id = (select auth.uid()));
create policy device_tokens_insert on public.device_tokens for insert to authenticated
  with check (user_id = (select auth.uid()));
create policy device_tokens_update on public.device_tokens for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
create policy device_tokens_delete on public.device_tokens for delete to authenticated
  using (user_id = (select auth.uid()));

create policy notifications_select on public.notifications for select to authenticated
  using (user_id = (select auth.uid()));
create policy notifications_update on public.notifications for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
create policy notifications_delete on public.notifications for delete to authenticated
  using (user_id = (select auth.uid()));

create policy health_scores_select on public.health_scores for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));

create policy sos_alerts_select on public.sos_alerts for select to authenticated
  using (private.can_access_elder(elder_id, (select auth.uid())));
create policy sos_alerts_insert on public.sos_alerts for insert to authenticated
  with check (
    private.can_access_elder(elder_id, (select auth.uid()))
    and triggered_by = (select auth.uid())
  );
create policy sos_alerts_update on public.sos_alerts for update to authenticated
  using (private.can_manage_elder(elder_id, (select auth.uid())))
  with check (private.can_manage_elder(elder_id, (select auth.uid())));

create policy audit_logs_select on public.audit_logs for select to authenticated
  using (
    actor_id = (select auth.uid())
    or (family_id is not null and private.is_family_owner(family_id, (select auth.uid())))
  );
create policy audit_logs_insert on public.audit_logs for insert to authenticated
  with check (
    actor_id = (select auth.uid())
    and (
      family_id is null
      or private.is_family_member(family_id, (select auth.uid()))
    )
    and (
      elder_id is null
      or private.can_access_elder(elder_id, (select auth.uid()))
    )
  );

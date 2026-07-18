-- Firebase is the sole identity provider. Application identities live in
-- public.users and are accessed only by the trusted backend service role.

create table public.users (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text unique not null,
  email text unique,
  name text,
  photo_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_login_at timestamptz,
  login_count integer not null default 0 check (login_count >= 0),
  onboarding_completed boolean not null default false,
  preferred_language text,
  status text not null default 'active'
);

create table public.login_history (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text,
  login_time timestamptz not null default now(),
  device text,
  browser text,
  os text,
  ip_address text,
  city text,
  country text,
  user_agent text,
  session_id text
);

create index login_history_firebase_uid_login_time_idx
  on public.login_history (firebase_uid, login_time desc);
create unique index login_history_session_id_uidx
  on public.login_history (session_id)
  where session_id is not null;

alter table public.users enable row level security;
alter table public.login_history enable row level security;

revoke all on table public.users from anon, authenticated;
revoke all on table public.login_history from anon, authenticated;
grant select, insert, update on table public.users to service_role;
grant select, insert on table public.login_history to service_role;

create trigger users_set_updated_at before update on public.users
  for each row execute function private.set_updated_at();

-- Preserve any existing Supabase-auth-backed identities before moving foreign
-- keys. A later Firebase login can claim a matching legacy row by verified email.
insert into public.users (id, firebase_uid, email, name, photo_url, created_at, updated_at)
select
  au.id,
  'legacy:' || au.id::text,
  au.email,
  coalesce(au.raw_user_meta_data ->> 'full_name', au.raw_user_meta_data ->> 'name'),
  coalesce(au.raw_user_meta_data ->> 'avatar_url', au.raw_user_meta_data ->> 'picture'),
  au.created_at,
  coalesce(au.updated_at, au.created_at)
from auth.users au
on conflict do nothing;

alter table public.profiles drop constraint profiles_id_fkey;
alter table public.profiles
  add constraint profiles_id_fkey foreign key (id) references public.users (id) on delete cascade;

alter table public.families drop constraint families_owner_id_fkey;
alter table public.families
  add constraint families_owner_id_fkey foreign key (owner_id) references public.users (id) on delete restrict;

alter table public.invitations drop constraint invitations_invited_by_fkey;
alter table public.invitations
  add constraint invitations_invited_by_fkey foreign key (invited_by) references public.users (id) on delete restrict;
alter table public.invitations drop constraint invitations_accepted_by_fkey;
alter table public.invitations
  add constraint invitations_accepted_by_fkey foreign key (accepted_by) references public.users (id) on delete set null;

alter table public.family_members drop constraint family_members_user_id_fkey;
alter table public.family_members
  add constraint family_members_user_id_fkey foreign key (user_id) references public.users (id) on delete cascade;

alter table public.elder_profiles drop constraint elder_profiles_user_id_fkey;
alter table public.elder_profiles
  add constraint elder_profiles_user_id_fkey foreign key (user_id) references public.users (id) on delete set null;
alter table public.elder_profiles drop constraint elder_profiles_created_by_fkey;
alter table public.elder_profiles
  add constraint elder_profiles_created_by_fkey foreign key (created_by) references public.users (id) on delete restrict;

alter table public.reminders drop constraint reminders_assigned_by_fkey;
alter table public.reminders
  add constraint reminders_assigned_by_fkey foreign key (assigned_by) references public.users (id) on delete restrict;

alter table public.reminder_completions drop constraint reminder_completions_completed_by_fkey;
alter table public.reminder_completions
  add constraint reminder_completions_completed_by_fkey foreign key (completed_by) references public.users (id) on delete set null;

alter table public.activities drop constraint activities_actor_id_fkey;
alter table public.activities
  add constraint activities_actor_id_fkey foreign key (actor_id) references public.users (id) on delete set null;

alter table public.wellness_checks drop constraint wellness_checks_recorded_by_fkey;
alter table public.wellness_checks
  add constraint wellness_checks_recorded_by_fkey foreign key (recorded_by) references public.users (id) on delete set null;

alter table public.ai_conversations drop constraint ai_conversations_started_by_fkey;
alter table public.ai_conversations
  add constraint ai_conversations_started_by_fkey foreign key (started_by) references public.users (id) on delete set null;

alter table public.ai_messages drop constraint ai_messages_sender_id_fkey;
alter table public.ai_messages
  add constraint ai_messages_sender_id_fkey foreign key (sender_id) references public.users (id) on delete set null;

alter table public.device_tokens drop constraint device_tokens_user_id_fkey;
alter table public.device_tokens
  add constraint device_tokens_user_id_fkey foreign key (user_id) references public.users (id) on delete cascade;

alter table public.notifications drop constraint notifications_user_id_fkey;
alter table public.notifications
  add constraint notifications_user_id_fkey foreign key (user_id) references public.users (id) on delete cascade;

alter table public.sos_alerts drop constraint sos_alerts_triggered_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_triggered_by_fkey foreign key (triggered_by) references public.users (id) on delete set null;
alter table public.sos_alerts drop constraint sos_alerts_acknowledged_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_acknowledged_by_fkey foreign key (acknowledged_by) references public.users (id) on delete set null;
alter table public.sos_alerts drop constraint sos_alerts_resolved_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_resolved_by_fkey foreign key (resolved_by) references public.users (id) on delete set null;

alter table public.audit_logs drop constraint audit_logs_actor_id_fkey;
alter table public.audit_logs
  add constraint audit_logs_actor_id_fkey foreign key (actor_id) references public.users (id) on delete set null;

-- The function makes user upsert, login counter increment, profile bootstrap,
-- and history insertion one transaction. Only the service role may execute it.
create or replace function public.record_firebase_login(
  p_firebase_uid text,
  p_email text default null,
  p_name text default null,
  p_photo_url text default null,
  p_device text default null,
  p_browser text default null,
  p_os text default null,
  p_ip_address text default null,
  p_city text default null,
  p_country text default null,
  p_user_agent text default null,
  p_session_id text default null
)
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
  authenticated_user public.users;
begin
  if p_firebase_uid is null or length(btrim(p_firebase_uid)) = 0 then
    raise exception 'firebase_uid is required' using errcode = '22023';
  end if;

  -- Claim a preserved legacy row only when Firebase supplied the same email.
  if p_email is not null then
    update public.users
    set firebase_uid = p_firebase_uid
    where lower(email) = lower(p_email)
      and firebase_uid like 'legacy:%'
      and not exists (
        select 1 from public.users existing
        where existing.firebase_uid = p_firebase_uid
      );
  end if;

  insert into public.users (
    firebase_uid, email, name, photo_url, last_login_at, login_count
  )
  values (
    p_firebase_uid, p_email, p_name, p_photo_url, now(), 1
  )
  on conflict (firebase_uid) do update
  set
    email = excluded.email,
    name = excluded.name,
    photo_url = excluded.photo_url,
    last_login_at = now(),
    login_count = public.users.login_count + 1
  returning * into authenticated_user;

  insert into public.profiles (id, full_name, email, avatar_url)
  values (
    authenticated_user.id,
    left(
      coalesce(
        nullif(btrim(p_name), ''),
        nullif(split_part(coalesce(p_email, ''), '@', 1), ''),
        'Sahaay User'
      ),
      150
    ),
    p_email,
    p_photo_url
  )
  on conflict (id) do nothing;

  insert into public.login_history (
    firebase_uid, device, browser, os, ip_address, city, country,
    user_agent, session_id
  )
  values (
    p_firebase_uid, p_device, p_browser, p_os, p_ip_address, p_city,
    p_country, p_user_agent, p_session_id
  );

  return to_jsonb(authenticated_user)
    || jsonb_build_object('session_id', p_session_id);
end;
$$;

revoke all on function public.record_firebase_login(
  text, text, text, text, text, text, text, text, text, text, text, text
) from public, anon, authenticated;
grant execute on function public.record_firebase_login(
  text, text, text, text, text, text, text, text, text, text, text, text
) to service_role;

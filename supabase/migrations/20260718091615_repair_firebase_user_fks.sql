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

-- Fix FKs that resolved to public.users (legacy) instead of auth.users.

alter table public.profiles drop constraint if exists profiles_id_fkey;
alter table public.profiles
  add constraint profiles_id_fkey
  foreign key (id) references auth.users (id) on delete cascade;

alter table public.families drop constraint if exists families_owner_id_fkey;
alter table public.families
  add constraint families_owner_id_fkey
  foreign key (owner_id) references auth.users (id) on delete restrict;

alter table public.invitations drop constraint if exists invitations_accepted_by_fkey;
alter table public.invitations
  add constraint invitations_accepted_by_fkey
  foreign key (accepted_by) references auth.users (id) on delete set null;

alter table public.invitations drop constraint if exists invitations_invited_by_fkey;
alter table public.invitations
  add constraint invitations_invited_by_fkey
  foreign key (invited_by) references auth.users (id) on delete restrict;

alter table public.family_members drop constraint if exists family_members_user_id_fkey;
alter table public.family_members
  add constraint family_members_user_id_fkey
  foreign key (user_id) references auth.users (id) on delete cascade;

alter table public.elder_profiles drop constraint if exists elder_profiles_created_by_fkey;
alter table public.elder_profiles
  add constraint elder_profiles_created_by_fkey
  foreign key (created_by) references auth.users (id) on delete restrict;

alter table public.elder_profiles drop constraint if exists elder_profiles_user_id_fkey;
alter table public.elder_profiles
  add constraint elder_profiles_user_id_fkey
  foreign key (user_id) references auth.users (id) on delete set null;

alter table public.reminders drop constraint if exists reminders_assigned_by_fkey;
alter table public.reminders
  add constraint reminders_assigned_by_fkey
  foreign key (assigned_by) references auth.users (id) on delete restrict;

alter table public.reminder_completions drop constraint if exists reminder_completions_completed_by_fkey;
alter table public.reminder_completions
  add constraint reminder_completions_completed_by_fkey
  foreign key (completed_by) references auth.users (id) on delete set null;

alter table public.activities drop constraint if exists activities_actor_id_fkey;
alter table public.activities
  add constraint activities_actor_id_fkey
  foreign key (actor_id) references auth.users (id) on delete set null;

alter table public.wellness_checks drop constraint if exists wellness_checks_recorded_by_fkey;
alter table public.wellness_checks
  add constraint wellness_checks_recorded_by_fkey
  foreign key (recorded_by) references auth.users (id) on delete set null;

alter table public.ai_conversations drop constraint if exists ai_conversations_started_by_fkey;
alter table public.ai_conversations
  add constraint ai_conversations_started_by_fkey
  foreign key (started_by) references auth.users (id) on delete set null;

alter table public.ai_messages drop constraint if exists ai_messages_sender_id_fkey;
alter table public.ai_messages
  add constraint ai_messages_sender_id_fkey
  foreign key (sender_id) references auth.users (id) on delete set null;

alter table public.device_tokens drop constraint if exists device_tokens_user_id_fkey;
alter table public.device_tokens
  add constraint device_tokens_user_id_fkey
  foreign key (user_id) references auth.users (id) on delete cascade;

alter table public.notifications drop constraint if exists notifications_user_id_fkey;
alter table public.notifications
  add constraint notifications_user_id_fkey
  foreign key (user_id) references auth.users (id) on delete cascade;

alter table public.sos_alerts drop constraint if exists sos_alerts_acknowledged_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_acknowledged_by_fkey
  foreign key (acknowledged_by) references auth.users (id) on delete set null;

alter table public.sos_alerts drop constraint if exists sos_alerts_resolved_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_resolved_by_fkey
  foreign key (resolved_by) references auth.users (id) on delete set null;

alter table public.sos_alerts drop constraint if exists sos_alerts_triggered_by_fkey;
alter table public.sos_alerts
  add constraint sos_alerts_triggered_by_fkey
  foreign key (triggered_by) references auth.users (id) on delete set null;

alter table public.audit_logs drop constraint if exists audit_logs_actor_id_fkey;
alter table public.audit_logs
  add constraint audit_logs_actor_id_fkey
  foreign key (actor_id) references auth.users (id) on delete set null;

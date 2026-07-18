-- Auth-ready RLS: sessions owned by auth.users; child rows scoped via session.

alter table public.sessions
  add column if not exists owner_id uuid references auth.users (id) on delete cascade;

create index if not exists sessions_owner_id_idx on public.sessions (owner_id);

-- Sessions
create policy "Users read own sessions"
  on public.sessions for select
  to authenticated
  using (owner_id = (select auth.uid()));

create policy "Users insert own sessions"
  on public.sessions for insert
  to authenticated
  with check (owner_id = (select auth.uid()));

create policy "Users update own sessions"
  on public.sessions for update
  to authenticated
  using (owner_id = (select auth.uid()))
  with check (owner_id = (select auth.uid()));

create policy "Users delete own sessions"
  on public.sessions for delete
  to authenticated
  using (owner_id = (select auth.uid()));

-- Messages
create policy "Users read own messages"
  on public.messages for select
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = messages.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users insert own messages"
  on public.messages for insert
  to authenticated
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = messages.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users update own messages"
  on public.messages for update
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = messages.session_id and s.owner_id = (select auth.uid())
    )
  )
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = messages.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users delete own messages"
  on public.messages for delete
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = messages.session_id and s.owner_id = (select auth.uid())
    )
  );

-- Routines
create policy "Users read own routines"
  on public.routines for select
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = routines.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users insert own routines"
  on public.routines for insert
  to authenticated
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = routines.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users update own routines"
  on public.routines for update
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = routines.session_id and s.owner_id = (select auth.uid())
    )
  )
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = routines.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users delete own routines"
  on public.routines for delete
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = routines.session_id and s.owner_id = (select auth.uid())
    )
  );

-- Reminders
create policy "Users read own reminders"
  on public.reminders for select
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = reminders.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users insert own reminders"
  on public.reminders for insert
  to authenticated
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = reminders.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users update own reminders"
  on public.reminders for update
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = reminders.session_id and s.owner_id = (select auth.uid())
    )
  )
  with check (
    exists (
      select 1 from public.sessions s
      where s.id = reminders.session_id and s.owner_id = (select auth.uid())
    )
  );

create policy "Users delete own reminders"
  on public.reminders for delete
  to authenticated
  using (
    exists (
      select 1 from public.sessions s
      where s.id = reminders.session_id and s.owner_id = (select auth.uid())
    )
  );

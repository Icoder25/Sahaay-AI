-- Explicit deny policies document that Firebase-backed identity data is only
-- available through the trusted backend service role.

create policy users_backend_only
  on public.users
  for all
  to anon, authenticated
  using (false)
  with check (false);

create policy login_history_backend_only
  on public.login_history
  for all
  to anon, authenticated
  using (false)
  with check (false);

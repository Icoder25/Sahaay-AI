-- Cache the JWT expression once per statement in profile write policies.
-- This avoids per-row auth.jwt() evaluation reported by the performance advisor.

alter policy profiles_insert
  on public.profiles
  with check (
    id = (select auth.uid())
    and (
      email is null
      or lower(email) = lower(coalesce((select auth.jwt()) ->> 'email', ''))
    )
  );

alter policy profiles_update
  on public.profiles
  using (id = (select auth.uid()))
  with check (
    id = (select auth.uid())
    and (
      email is null
      or lower(email) = lower(coalesce((select auth.jwt()) ->> 'email', ''))
    )
  );

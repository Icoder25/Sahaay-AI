drop function public.record_firebase_login(
  text, text, text, text, text, text, text, text, text, text, text, text
);

create function public.record_firebase_login(
  p_firebase_uid text,
  p_email text default null,
  p_email_verified boolean default false,
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

  if p_email is not null and not p_email_verified then
    raise exception 'verified email is required' using errcode = '22023';
  end if;

  if p_email is not null then
    update public.users
    set firebase_uid = p_firebase_uid
    where lower(email) = lower(p_email)
      and firebase_uid like 'legacy:%'
      and not exists (
        select 1 from public.users existing
        where existing.firebase_uid = p_firebase_uid
      );

    if exists (
      select 1
      from public.users existing
      where lower(existing.email) = lower(p_email)
        and existing.firebase_uid <> p_firebase_uid
    ) then
      raise exception 'firebase identity conflicts with an existing user'
        using errcode = '23505';
    end if;
  end if;

  insert into public.users (
    firebase_uid, email, name, photo_url, last_login_at, login_count
  )
  values (
    p_firebase_uid, p_email, p_name, p_photo_url, now(), 1
  )
  on conflict (firebase_uid) do update
  set
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
  text, text, boolean, text, text, text, text, text, text, text, text, text, text
) from public, anon, authenticated;
grant execute on function public.record_firebase_login(
  text, text, boolean, text, text, text, text, text, text, text, text, text, text
) to service_role;

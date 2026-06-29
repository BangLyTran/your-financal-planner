-- Run this entire file in Supabase Dashboard > SQL Editor.
-- It creates one private planner document per authenticated user.

create table if not exists public.financial_plans (
  user_id uuid primary key references auth.users(id) on delete cascade,
  planner_state jsonb not null,
  updated_at timestamptz not null default now()
);

create or replace function public.set_financial_plan_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_financial_plan_updated_at on public.financial_plans;
create trigger set_financial_plan_updated_at
before update on public.financial_plans
for each row execute function public.set_financial_plan_updated_at();

alter table public.financial_plans enable row level security;

revoke all on table public.financial_plans from anon;
grant select, insert, update, delete on table public.financial_plans to authenticated;

-- Re-create policies safely if this script is run more than once.
drop policy if exists "Users can read their own financial plan" on public.financial_plans;
drop policy if exists "Users can insert their own financial plan" on public.financial_plans;
drop policy if exists "Users can update their own financial plan" on public.financial_plans;
drop policy if exists "Users can delete their own financial plan" on public.financial_plans;

create policy "Users can read their own financial plan"
on public.financial_plans
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert their own financial plan"
on public.financial_plans
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update their own financial plan"
on public.financial_plans
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete their own financial plan"
on public.financial_plans
for delete
to authenticated
using ((select auth.uid()) = user_id);

-- Blend(AI)r – Supabase bootstrap schema
-- Run this in the SQL editor or via `supabase db push`.

-- 1. Enable uuid generator (usually enabled already on Supabase)
create extension if not exists "pgcrypto";

-- ============================
-- Tables
-- ============================

-- projects: user-owned 3D model sets
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamp with time zone default now()
);

-- models: uploaded OBJ/STL files
create table if not exists public.models (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete cascade,
  filename text not null,
  path text not null,
  uploaded_at timestamp with time zone default now()
);

-- jobs: each prompt or gesture → job
create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete cascade,
  model_id uuid references public.models(id) on delete cascade,
  type text check (type in ('prompt','gesture')) not null,
  input text not null,
  status text default 'queued' check (status in ('queued','running','done','error')),
  result_path text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Basic index for faster project/job lookup
create index if not exists idx_jobs_project_id on public.jobs(project_id);
create index if not exists idx_models_project_id on public.models(project_id);

-- ============================
-- Storage buckets
-- ============================
-- These helper calls work inside Supabase to create storage buckets.
-- Remove `if not exists` once Supabase adds support; otherwise run individually.

-- input_models – user-uploaded OBJ/STL
select
  case
    when exists (select 1 from storage.buckets where id='input_models') then null
    else storage.create_bucket('input_models', false, 'private')
  end;

-- renders – PNG/JPEG renders of edits
select
  case
    when exists (select 1 from storage.buckets where id='renders') then null
    else storage.create_bucket('renders', false, 'public')
  end;

-- output_models – processed OBJ/STL
select
  case
    when exists (select 1 from storage.buckets where id='output_models') then null
    else storage.create_bucket('output_models', false, 'private')
  end;

-- logs – Blender stdout/error logs
select
  case
    when exists (select 1 from storage.buckets where id='logs') then null
    else storage.create_bucket('logs', false, 'private')
  end;

-- ============================
-- Realtime configuration (optional - enable all events on jobs)
-- Enable RLS and replication to get realtime updates through Supabase.
-- Uncomment and adjust as needed.
-- alter publication supabase_realtime add table public.jobs;
-- alter table public.jobs enable row level security;

-- Example RLS policy to allow owners to read their jobs
-- create policy "jobs_read_own" on public.jobs for select using (exists (select 1 from public.projects p where p.id = project_id and p.user_id = auth.uid()));

-- Done.

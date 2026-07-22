create table appointments (
  id uuid primary key default gen_random_uuid(),
  business_name text not null,
  full_name text not null,
  phone_number text not null,
  appointment_type text not null,
  appointment_date date not null,
  appointment_time time not null,
  reason text,
  status text default 'booked',
  calendar_event_id text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

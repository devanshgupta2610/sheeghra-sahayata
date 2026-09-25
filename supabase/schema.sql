-- ============================================================
-- Sheeghra Sahayata — Database Schema (Hackathon MVP)
-- Run this in Supabase SQL Editor, or apply via MCP / CLI.
-- ============================================================

-- Profiles (extends phone-based auth users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    emergency_contact TEXT,
    medical_info JSONB DEFAULT '{}'::jsonb,  -- {blood_group, allergies}
    language_pref TEXT DEFAULT 'en',         -- 'en' | 'hi'
    age_range TEXT,                          -- e.g. '18-35', '60+'
    gender TEXT,                             -- optional, skippable
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trips
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'ended')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_user_status ON trips(user_id, status);

-- Incidents (SOS, Silent SOS, etc.)
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id) ON DELETE SET NULL,
    type TEXT NOT NULL DEFAULT 'sos',        -- 'sos' | 'silent_sos'
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'acknowledged', 'resolved')),
    silent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at DESC);

-- Location breadcrumbs — PRIVACY-BY-DESIGN
-- Only stored while trip.status = 'active'. Cleanup job deletes rows
-- after trip ends UNLESS the location is linked to an incident.
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    -- If set, this location is tied to an SOS and MUST NOT be auto-deleted
    incident_id UUID REFERENCES incidents(id) ON DELETE SET NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_locations_trip ON locations(trip_id);
CREATE INDEX IF NOT EXISTS idx_locations_incident ON locations(incident_id);

-- Demo OTP codes table (mock — accepts any 6-digit code in the API)
CREATE TABLE IF NOT EXISTS demo_otp (
    phone TEXT PRIMARY KEY,
    code TEXT NOT NULL DEFAULT '123456',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (backend uses service_role key which bypasses RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE demo_otp ENABLE ROW LEVEL SECURITY;

-- Permissive policies for demo (backend uses service role; these help
-- if anyone hits PostgREST with the anon key during judging)
CREATE POLICY "demo_all_profiles" ON profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "demo_all_trips" ON trips FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "demo_all_incidents" ON incidents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "demo_all_locations" ON locations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "demo_all_otp" ON demo_otp FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- Seed data — realistic mock incidents so the dashboard isn't empty
-- ============================================================

-- Demo tourist profiles
INSERT INTO profiles (id, phone, name, emergency_contact, medical_info, language_pref, age_range, gender)
VALUES
    ('11111111-1111-1111-1111-111111111111', '+919876543210', 'Priya Sharma', '+919811122233',
     '{"blood_group":"B+","allergies":"None"}'::jsonb, 'en', '18-35', 'female'),
    ('22222222-2222-2222-2222-222222222222', '+919123456789', 'Rajesh Kumar', '+919822233344',
     '{"blood_group":"O+","allergies":"Penicillin"}'::jsonb, 'hi', '60+', 'male'),
    ('33333333-3333-3333-3333-333333333333', '+919988877766', 'Alex Tourist', '+919900011122',
     '{"blood_group":"A+","allergies":"Peanuts"}'::jsonb, 'en', '36-59', 'other')
ON CONFLICT (phone) DO NOTHING;

-- Active trip for Priya
INSERT INTO trips (id, user_id, start_time, status)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     '11111111-1111-1111-1111-111111111111',
     NOW() - INTERVAL '2 hours', 'active')
ON CONFLICT DO NOTHING;

-- Seed active / acknowledged / resolved incidents (Delhi NCR sample coords)
INSERT INTO incidents (id, user_id, trip_id, type, lat, lon, status, silent, created_at)
VALUES
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
     '11111111-1111-1111-1111-111111111111',
     'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     'sos', 28.6139, 77.2090, 'active', false, NOW() - INTERVAL '15 minutes'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc',
     '22222222-2222-2222-2222-222222222222',
     NULL, 'silent_sos', 28.5562, 77.1000, 'acknowledged', true, NOW() - INTERVAL '45 minutes'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd',
     '33333333-3333-3333-3333-333333333333',
     NULL, 'sos', 28.7041, 77.1025, 'resolved', false, NOW() - INTERVAL '3 hours')
ON CONFLICT DO NOTHING;

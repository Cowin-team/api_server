CREATE TABLE resources(
    id serial,
    city text,
    resource_type text,
    google_sheet_id text,
    location geometry,
    raw_obj text[]
);

CREATE INDEX resource_location_idx ON resources USING GIST(location);
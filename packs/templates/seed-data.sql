-- Template: Seed Data
-- Variables: {{tenant_id}}, {{services}}, {{products}}, {{staff_roles}}, {{business_hours}}

DO $$
DECLARE
  tid UUID := '{{tenant_id}}';
BEGIN

-- Insert services
{{#services}}
INSERT INTO services (tenant_id, name, description, duration_minutes, price, category)
VALUES (tid, '{{name}}', '{{description}}', {{duration}}, {{price}}, '{{category}}');
{{/services}}

-- Insert products
{{#products}}
INSERT INTO products (tenant_id, name, category, price, stock, unit)
VALUES (tid, '{{name}}', '{{category}}', {{price}}, {{stock}}, '{{unit}}');
{{/products}}

-- Insert staff roles
{{#staff}}
INSERT INTO staff (tenant_id, name, role, phone, email)
VALUES (tid, '{{name}}', '{{role}}', '{{phone}}', '{{email}}');
{{/staff}}

-- Insert business hours
{{#hours}}
INSERT INTO business_hours (tenant_id, day_of_week, open_time, close_time, is_active)
VALUES (tid, {{day}}, '{{open}}', '{{close}}', {{active}});
{{/hours}}

END $$;

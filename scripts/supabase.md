# Supabase — Auth + Storage

- **MCP Server**: supabase_mcp
- **Tools**: supabase_signup, supabase_login, supabase_get_user, supabase_list_users, supabase_list_buckets, supabase_create_bucket, supabase_list_files, supabase_upload_file, supabase_delete_file, supabase_get_public_url
- **Input**: email+password (auth), bucket+path+content (storage)
- **Output**: `{user, session}` o `{url}` o `[{...}]`
- **Ejemplo**: `supabase_signup("fan@email.com", "pass123", "Fan Name")`
- **Permisos**: requiere SUPABASE_SERVICE_KEY para admin
- **Endpoint**: POST :8180/mcp/execute

"use client";

const MCP = "/api/mcp/execute";

export function useSupabase() {
  const signup = async (email: string, password: string, name?: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "supabase_signup", args: { email, password, name } }),
    });
    return resp.json();
  };

  const login = async (email: string, password: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "supabase_login", args: { email, password } }),
    });
    return resp.json();
  };

  const uploadFile = async (bucket: string, path: string, contentB64: string, contentType?: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tool: "upload_file",
        args: { bucket, path, content_b64: contentB64, content_type: contentType || "application/octet-stream" },
      }),
    });
    return resp.json();
  };

  const listFiles = async (bucket: string, folder = "") => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "supabase_list_files", args: { bucket, folder } }),
    });
    return resp.json();
  };

  const getPublicUrl = (bucket: string, path: string) => {
    return `https://jibalggzudkflwzdndqz.supabase.co/storage/v1/object/public/${bucket}/${path}`;
  };

  return { signup, login, uploadFile, listFiles, getPublicUrl };
}

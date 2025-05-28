from supabase import create_client

url = "https://avxyefrckoynbubddwhl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # recortado por seguridad

supabase = create_client(url, key)
from supabase import create_client

url = "https://avxyefrckoynbubddwhl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF2eHllZnJja295bmJ1YmRkd2hsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODM4ODQ3MCwiZXhwIjoyMDYzOTY0NDcwfQ.WC0RvJyNlGM_yxXzmCo4BHBtxUiJMkesg1TbLyOCp_k"  # recortado por seguridad

supabase = create_client(url, key)
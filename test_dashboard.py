import app

client = app.app.test_client()

with client.session_transaction() as session:
    session["admin_logged_in"] = True
    session["admin_username"] = "admin"

response = client.get("/dashboard")

print("STATUS:", response.status_code)

print(
    "NEW HEADING FOUND:",
    b"NEW DASHBOARD TEST 2026" in response.data
)

print("REDIRECT:", response.location)
"""Quick diagnostic: check DB state and test API"""
import sqlite3
import json

print("=" * 50)
print("DATABASE DIAGNOSTIC")
print("=" * 50)

# Check teachgenie.db
try:
    conn = sqlite3.connect('teachgenie.db')
    c = conn.cursor()
    
    # List tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    print(f"\nTables in teachgenie.db: {tables}")
    
    # Check users
    if 'users' in tables:
        c.execute("SELECT count(*) FROM users")
        count = c.fetchone()[0]
        print(f"Total users: {count}")
        
        if count > 0:
            c.execute("SELECT id, email, full_name, is_active, is_verified, email_verified FROM users LIMIT 5")
            users = c.fetchall()
            print("\nUsers (first 5):")
            for u in users:
                print(f"  ID={u[0]}, email={u[1]}, name={u[2]}, active={u[3]}, verified={u[4]}, email_verified={u[5]}")
    else:
        print("!! 'users' table NOT found !!")
        
    # Check email_otps
    if 'email_otps' in tables:
        c.execute("SELECT count(*) FROM email_otps")
        print(f"\nTotal OTP records: {c.fetchone()[0]}")
    
    conn.close()
except Exception as e:
    print(f"Error reading DB: {e}")

# Test API
print("\n" + "=" * 50)
print("API ENDPOINT TEST")
print("=" * 50)

import urllib.request
import urllib.error

# Test login
try:
    data = json.dumps({"email": "test@test.com", "password": "Test123!"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req)
    print(f"\nLogin response: {response.status} {response.read().decode()}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\nLogin error: {e.code} - {body}")
except Exception as e:
    print(f"\nLogin error: {e}")

# Test send-verification-email
try:
    data = json.dumps({"email": "test@test.com"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/send-verification-email",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req)
    print(f"\nVerification email response: {response.status} {response.read().decode()}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\nVerification email error: {e.code} - {body}")
except Exception as e:
    print(f"\nVerification email error: {e}")

print("\n" + "=" * 50)
print("DONE")

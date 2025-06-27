# hash_sample_pass.py
import streamlit_authenticator as stauth

# ✨ Replace these with your own passwords to generate bcrypt hashes
passwords = ['your_password1', 'your_password2']

# 🔐 Generate secure bcrypt hashes
hashed_passwords = stauth.Hasher(passwords).generate()

# 📋 Print the original and hashed versions
for i, pwd in enumerate(passwords):
    print(f"Original: {pwd} -> Hashed: {hashed_passwords[i]}")

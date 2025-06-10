import streamlit as st
import oracledb
# Test if oracledb can be imported
try:
    import oracledb
    st.success("✅ Successfully imported 'oracledb' module.")
except Exception as e:
    st.error("❌ Failed to import 'oracledb'")
    st.exception(e)
    st.stop()

# Force thin mode (important for Streamlit Cloud)
try:
    oracledb.init_oracle_client(lib_dir=None)
except Exception as e:
    st.info("Thin mode already active or no client needed.")

# Database connection section
st.header("🔗 Connect to Oracle Database")

with st.form("db_form"):
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    dsn = st.text_input("DSN (e.g. yourhost.example.com/servicename)")
    submitted = st.form_submit_button("Connect")

    if submitted:
        try:
            conn = oracledb.connect(user=user, password=password, dsn=dsn)
            st.success("✅ Connected to Oracle DB!")

            cursor = conn.cursor()
            cursor.execute("SELECT 'Hello from Oracle!' FROM dual")
            result = cursor.fetchone()
            st.write("📨 Query Result:", result[0])

        except Exception as e:
            st.error("❌ Connection or query failed.")
            st.exception(e)

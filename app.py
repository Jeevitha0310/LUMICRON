import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk
from utils.matcher import match_volunteers

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Smart Volunteer Allocation", layout="wide")

st.title("Smart Volunteer Allocation System")
st.markdown("### AI-Based Smart Resource Allocation for NGOs")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("database/data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    skill TEXT,
    location TEXT,
    availability TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type TEXT,
    location TEXT,
    urgency TEXT,
    description TEXT
)
""")

conn.commit()

# =========================
# LOCATION → COORDINATES
# =========================
def get_coordinates(location):
    location = str(location).strip().lower()

    mapping = {
        "chennai": (13.0827, 80.2707),
        "coimbatore": (11.0168, 76.9558),
        "madurai": (9.9252, 78.1198),
        "trichy": (10.7905, 78.7047),
        "salem": (11.6643, 78.1460)
    }

    return mapping.get(location, None)

# =========================
# MENU
# =========================
menu = ["Add Issue", "Add Volunteer", "Match Volunteers", "Dashboard", "Load Dataset", "Map View", "Manage Data"]
choice = st.sidebar.selectbox("Menu", menu)

# =========================
# ADD ISSUE
# =========================
if choice == "Add Issue":
    st.subheader("Add Community Issue")

    issue = st.text_input("Issue Type")
    location = st.text_input("Location")
    urgency = st.selectbox("Urgency", ["High", "Medium", "Low"])
    desc = st.text_area("Description")

    if st.button("Submit"):
        conn.execute(
            "INSERT INTO issues (issue_type, location, urgency, description) VALUES (?, ?, ?, ?)",
            (issue, location, urgency, desc)
        )
        conn.commit()
        st.success("Issue Added Successfully")

# =========================
# ADD VOLUNTEER
# =========================
elif choice == "Add Volunteer":
    st.subheader("Add Volunteer")

    name = st.text_input("Name")
    skill = st.text_input("Skill")
    location = st.text_input("Location")
    availability = st.selectbox("Availability", ["Yes", "No"])

    if st.button("Add"):
        conn.execute(
            "INSERT INTO volunteers (name, skill, location, availability) VALUES (?, ?, ?, ?)",
            (name, skill, location, availability)
        )
        conn.commit()
        st.success("Volunteer Added Successfully")

# =========================
# LOAD DATASET
# =========================
elif choice == "Load Dataset":
    st.subheader("Load Volunteer Dataset")

    if st.button("Load Excel Data"):
        try:
            df = pd.read_excel("dataset/Volunteer-match.xlsx")
            df.columns = df.columns.str.strip()
            df = df.dropna()

            inserted = 0

            for _, row in df.iterrows():
                conn.execute(
                    "INSERT INTO volunteers (name, skill, location, availability) VALUES (?, ?, ?, ?)",
                    (
                        str(row['Volunteer Name']),
                        str(row['Skills']),
                        str(row['Location']).strip(),
                        str(row['Availability'])
                    )
                )
                inserted += 1

            conn.commit()
            st.success(f"{inserted} volunteers loaded successfully!")

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# MATCHING
# =========================
elif choice == "Match Volunteers":
    st.subheader("Volunteer Matching")

    vol_df = pd.read_sql("SELECT * FROM volunteers", conn)
    issue_df = pd.read_sql("SELECT * FROM issues", conn)

    if vol_df.empty or issue_df.empty:
        st.warning("Add both volunteers and issues first")
    else:
        matches = match_volunteers(
            vol_df.to_dict('records'),
            issue_df.to_dict('records')
        )

        for m in matches:
            issue = m["issue"]
            vol = m["volunteer"]

            if vol:
                st.success(
                    f"Issue: {issue['issue_type']} ({issue['location']}) → "
                    f"Volunteer: {vol['name']} (Score: {m['score']})"
                )
            else:
                st.error(f"No match found for {issue['issue_type']}")

# =========================
# DASHBOARD
# =========================
elif choice == "Dashboard":
    st.subheader("Dashboard")

    issue_df = pd.read_sql("SELECT * FROM issues", conn)
    vol_df = pd.read_sql("SELECT * FROM volunteers", conn)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Issues", len(issue_df))
    with col2:
        st.metric("Total Volunteers", len(vol_df))

    if not issue_df.empty:
        st.write("Issue Distribution by Urgency")
        st.bar_chart(issue_df['urgency'].value_counts())

    if not vol_df.empty:
        st.write("Volunteers by Location")
        st.bar_chart(vol_df['location'].value_counts())

# =========================
# ADVANCED MAP VIEW
# =========================
elif choice == "Map View":
    st.subheader("Advanced Map: Issues ↔ Volunteers Matching")

    issue_df = pd.read_sql("SELECT * FROM issues", conn)
    vol_df = pd.read_sql("SELECT * FROM volunteers", conn)

    if issue_df.empty or vol_df.empty:
        st.warning("Add both issues and volunteers first")
    else:
        matches = match_volunteers(
            vol_df.to_dict('records'),
            issue_df.to_dict('records')
        )

        points = []
        lines = []

        for m in matches:
            issue = m["issue"]
            vol = m["volunteer"]

            issue_coords = get_coordinates(issue['location'])

            if issue_coords:
                i_lat, i_lon = issue_coords

                # ISSUE (RED)
                points.append({
                    "lat": i_lat,
                    "lon": i_lon,
                    "type": "Issue",
                    "name": issue['issue_type'],
                    "color": [255, 0, 0]
                })

                if vol:
                    vol_coords = get_coordinates(vol['location'])

                    if vol_coords:
                        v_lat, v_lon = vol_coords

                        # VOLUNTEER (GREEN)
                        points.append({
                            "lat": v_lat,
                            "lon": v_lon,
                            "type": "Volunteer",
                            "name": vol['name'],
                            "color": [0, 200, 0]
                        })

                        # LINE (MATCH)
                        lines.append({
                            "from_lon": i_lon,
                            "from_lat": i_lat,
                            "to_lon": v_lon,
                            "to_lat": v_lat
                        })

        if len(points) > 0:
            df_points = pd.DataFrame(points)
            df_lines = pd.DataFrame(lines)

            point_layer = pdk.Layer(
                "ScatterplotLayer",
                df_points,
                get_position='[lon, lat]',
                get_color='color',
                get_radius=40000,
                pickable=True
            )

            line_layer = pdk.Layer(
                "LineLayer",
                df_lines,
                get_source_position='[from_lon, from_lat]',
                get_target_position='[to_lon, to_lat]',
                get_color='[0, 0, 255]',
                get_width=5
            )

            view_state = pdk.ViewState(
                latitude=df_points['lat'].mean(),
                longitude=df_points['lon'].mean(),
                zoom=5
            )

            tooltip = {
                "html": "<b>{type}</b><br/>{name}",
                "style": {"backgroundColor": "black", "color": "white"}
            }

            st.pydeck_chart(pdk.Deck(
                layers=[point_layer, line_layer],
                initial_view_state=view_state,
                tooltip=tooltip
            ))
        else:
            st.error("No valid data for map")
    # =========================
# MANAGE DATA (HISTORY + DELETE)
# =========================
elif choice == "Manage Data":
    st.subheader("Manage Data (History & Delete)")

    tab1, tab2 = st.tabs(["Issues", "Volunteers"])

    # -------------------------
    # ISSUES TABLE
    # -------------------------
    with tab1:
        st.write("All Issues")

        issue_df = pd.read_sql("SELECT * FROM issues", conn)

        if not issue_df.empty:
            st.dataframe(issue_df)

            delete_id = st.number_input("Enter Issue ID to delete", step=1)

            if st.button("Delete Issue"):
                conn.execute("DELETE FROM issues WHERE id=?", (int(delete_id),))
                conn.commit()
                st.success("Issue deleted. Refresh page.")

        else:
            st.info("No issues available")

    # -------------------------
    # VOLUNTEERS TABLE
    # -------------------------
    with tab2:
        st.write("All Volunteers")

        vol_df = pd.read_sql("SELECT * FROM volunteers", conn)

        if not vol_df.empty:
            st.dataframe(vol_df)

            delete_id = st.number_input("Enter Volunteer ID to delete", step=1)

            if st.button("Delete Volunteer"):
                conn.execute("DELETE FROM volunteers WHERE id=?", (int(delete_id),))
                conn.commit()
                st.success("Volunteer deleted. Refresh page.")

        else:
            st.info("No volunteers available")

    # -------------------------
    # CLEAR DATABASE
    # -------------------------
    st.markdown("---")
    st.subheader("Danger Zone")

    if st.button("Clear All Data"):
        conn.execute("DELETE FROM issues")
        conn.execute("DELETE FROM volunteers")
        conn.commit()
        st.warning("All data cleared!")
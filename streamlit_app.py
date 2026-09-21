import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


# ---------------- DATABASE ----------------

DB_NAME = "campusfix.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def load_data():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM complaints",
        conn
    )

    conn.close()
    return df


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="CampusFix",
    page_icon="🏫",
    layout="wide"
)


# ---------------- TITLE ----------------

st.title("🏫 CampusFix")
st.subheader("Campus Maintenance Complaint & Tracking System")

st.write(
    "Manage, track and analyze campus maintenance complaints."
)

st.divider()


# ---------------- SIDEBAR ----------------

menu = st.sidebar.radio(
    "Select Option",
    [
        "Dashboard",
        "Register Complaint",
        "All Tickets",
        "Search Tickets",
        "Reports & Analytics"
    ]
)


# ==================================================
# DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.header("📊 Dashboard")

    df = load_data()

    total = len(df)

    pending = len(
        df[df["status"] == "Pending"]
    )

    in_progress = len(
        df[df["status"] == "In Progress"]
    )

    resolved = len(
        df[df["status"] == "Resolved"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Complaints", total)
    col2.metric("Pending", pending)
    col3.metric("In Progress", in_progress)
    col4.metric("Resolved", resolved)

    st.divider()

    st.info(
        "Welcome to CampusFix! "
        "Use the sidebar to register and manage maintenance complaints."
    )


# ==================================================
# REGISTER COMPLAINT
# ==================================================

elif menu == "Register Complaint":

    st.header("📝 Register Complaint")

    with st.form("complaint_form"):

        student_name = st.text_input(
            "Student Name"
        )

        department = st.text_input(
            "Department"
        )

        building = st.text_input(
            "Building"
        )

        room_number = st.text_input(
            "Room Number"
        )

        category = st.selectbox(
            "Complaint Category",
            [
                "Electrical",
                "Plumbing",
                "Cleaning",
                "Furniture",
                "Internet",
                "Other"
            ]
        )

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High",
                "Urgent"
            ]
        )

        description = st.text_area(
            "Problem Description"
        )

        submitted = st.form_submit_button(
            "Submit Complaint"
        )

        if submitted:

            if (
                not student_name
                or not department
                or not building
                or not room_number
                or not description
            ):
                st.error(
                    "Please fill all required fields."
                )

            else:

                conn = get_connection()

                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO complaints
                    (
                        student_name,
                        department,
                        building,
                        room_number,
                        category,
                        priority,
                        description,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_name,
                        department,
                        building,
                        room_number,
                        category,
                        priority,
                        description,
                        "Pending"
                    )
                )

                ticket_id = cursor.lastrowid

                conn.commit()
                conn.close()

                st.success(
                    f"Complaint submitted successfully! "
                    f"Your Ticket ID is: {ticket_id}"
                )


# ==================================================
# ALL TICKETS
# ==================================================

elif menu == "All Tickets":

    st.header("🎫 All Tickets")

    df = load_data()

    if df.empty:

        st.info("No complaints found.")

    else:

        display_columns = [
            "id",
            "student_name",
            "department",
            "building",
            "room_number",
            "category",
            "priority",
            "status"
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True
        )

        st.divider()

        st.subheader("Update Ticket Status")

        ticket_id = st.number_input(
            "Ticket ID",
            min_value=1,
            step=1
        )

        new_status = st.selectbox(
            "New Status",
            [
                "Pending",
                "In Progress",
                "Resolved"
            ]
        )

        if st.button("Update Status"):

            conn = get_connection()

            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE complaints
                SET status = ?
                WHERE id = ?
                """,
                (
                    new_status,
                    ticket_id
                )
            )

            conn.commit()

            changed = cursor.rowcount

            conn.close()

            if changed:

                st.success(
                    "Ticket status updated successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Ticket ID not found."
                )


# ==================================================
# SEARCH TICKETS
# ==================================================

elif menu == "Search Tickets":

    st.header("🔍 Search Tickets")

    search_text = st.text_input(
        "Search by Ticket ID, Student Name or Department"
    )

    df = load_data()

    if search_text:

        result = df[
            df["id"].astype(str).str.contains(
                search_text,
                case=False,
                na=False
            )
            |
            df["student_name"].str.contains(
                search_text,
                case=False,
                na=False
            )
            |
            df["department"].str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

        if result.empty:

            st.warning("No tickets found.")

        else:

            st.dataframe(
                result,
                use_container_width=True
            )

    else:

        st.info(
            "Enter a Ticket ID, student name or department."
        )


# ==================================================
# REPORTS & ANALYTICS
# ==================================================

elif menu == "Reports & Analytics":

    st.header("📈 Reports & Analytics")

    df = load_data()

    if df.empty:

        st.info("No complaint data available.")

    else:

        total = len(df)

        pending = len(
            df[df["status"] == "Pending"]
        )

        in_progress = len(
            df[df["status"] == "In Progress"]
        )

        resolved = len(
            df[df["status"] == "Resolved"]
        )

        total_cost = 0

        if "repair_cost" in df.columns:
            total_cost = pd.to_numeric(
                df["repair_cost"],
                errors="coerce"
            ).fillna(0).sum()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total", total)
        col2.metric("Pending", pending)
        col3.metric("In Progress", in_progress)
        col4.metric("Resolved", resolved)
        col5.metric(
            "Repair Cost",
            f"₹{total_cost:.2f}"
        )

        st.divider()

        # -------- CATEGORY CHART --------

        st.subheader("Complaints by Category")

        category_counts = df["category"].value_counts()

        fig1, ax1 = plt.subplots()

        category_counts.plot(
            kind="bar",
            ax=ax1
        )

        ax1.set_xlabel("Category")
        ax1.set_ylabel("Number of Complaints")
        ax1.set_title("Complaints by Category")

        plt.xticks(rotation=45)

        st.pyplot(fig1)

        plt.close(fig1)

        # -------- STATUS CHART --------

        st.subheader("Complaints by Status")

        status_counts = df["status"].value_counts()

        fig2, ax2 = plt.subplots()

        status_counts.plot(
            kind="bar",
            ax=ax2
        )

        ax2.set_xlabel("Status")
        ax2.set_ylabel("Number of Complaints")
        ax2.set_title("Complaints by Status")

        st.pyplot(fig2)

        plt.close(fig2)

        # -------- PRIORITY CHART --------

        st.subheader("Priority Distribution")

        priority_counts = df["priority"].value_counts()

        fig3, ax3 = plt.subplots()

        priority_counts.plot(
            kind="pie",
            autopct="%1.1f%%",
            ax=ax3
        )

        ax3.set_ylabel("")
        ax3.set_title("Priority Distribution")

        st.pyplot(fig3)

        plt.close(fig3)

        # -------- CSV EXPORT --------

        st.subheader("Export Report")

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name="campusfix_report.csv",
            mime="text/csv"
        )
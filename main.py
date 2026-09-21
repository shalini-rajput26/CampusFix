import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect("campusfix.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            department TEXT,
            building TEXT,
            room_number TEXT,
            category TEXT,
            priority TEXT,
            description TEXT,
            status TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(complaints)")
    columns = [column[1] for column in cursor.fetchall()]

    if "technician" not in columns:
        cursor.execute(
            "ALTER TABLE complaints ADD COLUMN technician TEXT"
        )

    if "repair_cost" not in columns:
        cursor.execute(
            "ALTER TABLE complaints ADD COLUMN repair_cost REAL DEFAULT 0"
        )

    if "maintenance_notes" not in columns:
        cursor.execute(
            "ALTER TABLE complaints ADD COLUMN maintenance_notes TEXT"
        )

    connection.commit()
    connection.close()


create_database()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():

    dashboard_window = tk.Toplevel(window)

    dashboard_window.title("Dashboard")
    dashboard_window.geometry("900x600")
    dashboard_window.configure(bg="#0d1b2a")

    tk.Label(
        dashboard_window,
        text="CAMPUSFIX DASHBOARD",
        font=("Arial", 26, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).pack(pady=30)

    connection = sqlite3.connect("campusfix.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Pending'"
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'"
    )
    in_progress = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'"
    )
    resolved = cursor.fetchone()[0]

    connection.close()

    cards_frame = tk.Frame(
        dashboard_window,
        bg="#0d1b2a"
    )

    cards_frame.pack(pady=30)

    create_card(
        cards_frame,
        "TOTAL",
        total,
        "#62c6df",
        0,
        0
    )

    create_card(
        cards_frame,
        "PENDING",
        pending,
        "#f0ad4e",
        0,
        1
    )

    create_card(
        cards_frame,
        "IN PROGRESS",
        in_progress,
        "#5bc0de",
        1,
        0
    )

    create_card(
        cards_frame,
        "RESOLVED",
        resolved,
        "#5cb85c",
        1,
        1
    )


# =========================================================
# DASHBOARD CARD
# =========================================================

def create_card(parent, title, number, color, row, column):

    frame = tk.Frame(
        parent,
        bg=color,
        width=250,
        height=150
    )

    frame.grid(
        row=row,
        column=column,
        padx=20,
        pady=20
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=title,
        font=("Arial", 15, "bold"),
        bg=color,
        fg="white"
    ).pack(pady=20)

    tk.Label(
        frame,
        text=str(number),
        font=("Arial", 32, "bold"),
        bg=color,
        fg="white"
    ).pack()


# =========================================================
# ALL TICKETS
# =========================================================

def show_all_tickets():

    tickets_window = tk.Toplevel(window)

    tickets_window.title("All Tickets")
    tickets_window.geometry("1200x750")
    tickets_window.configure(bg="#0d1b2a")

    tk.Label(
        tickets_window,
        text="ALL COMPLAINT TICKETS",
        font=("Arial", 24, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).pack(pady=20)

    table_frame = tk.Frame(
        tickets_window,
        bg="#0d1b2a"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    columns = (
        "ID",
        "Student",
        "Department",
        "Building",
        "Room",
        "Category",
        "Priority",
        "Status"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)

    table.column("ID", width=50)
    table.column("Student", width=120)
    table.column("Department", width=120)
    table.column("Building", width=120)
    table.column("Room", width=70)
    table.column("Category", width=110)
    table.column("Priority", width=90)
    table.column("Status", width=100)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    def load_tickets():

        for item in table.get_children():
            table.delete(item)

        connection = sqlite3.connect("campusfix.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                student_name,
                department,
                building,
                room_number,
                category,
                priority,
                status
            FROM complaints
        """)

        complaints = cursor.fetchall()

        connection.close()

        for complaint in complaints:
            table.insert(
                "",
                "end",
                values=complaint
            )

    load_tickets()

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    update_frame = tk.Frame(
        tickets_window,
        bg="#0d1b2a"
    )

    update_frame.pack(pady=15)

    tk.Label(
        update_frame,
        text="New Status:",
        font=("Arial", 12, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).grid(
        row=0,
        column=0,
        padx=10
    )

    status_combo = ttk.Combobox(
        update_frame,
        values=[
            "Pending",
            "In Progress",
            "Resolved"
        ],
        state="readonly",
        width=18,
        font=("Arial", 12)
    )

    status_combo.grid(
        row=0,
        column=1,
        padx=10
    )

    status_combo.set("Select Status")

    def update_status():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Ticket Selected",
                "Please select a ticket first."
            )
            return

        new_status = status_combo.get()

        if new_status == "Select Status":
            messagebox.showwarning(
                "No Status Selected",
                "Please select a new status."
            )
            return

        ticket_id = table.item(
            selected[0]
        )["values"][0]

        connection = sqlite3.connect("campusfix.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE complaints
            SET status = ?
            WHERE id = ?
            """,
            (new_status, ticket_id)
        )

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Complaint status updated successfully!"
        )

        load_tickets()
        status_combo.set("Select Status")

    tk.Button(
        update_frame,
        text="Update Status",
        font=("Arial", 12, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=18,
        height=2,
        command=update_status
    ).grid(
        row=0,
        column=2,
        padx=10
    )

    # =====================================================
    # MAINTENANCE DETAILS
    # =====================================================

    maintenance_frame = tk.LabelFrame(
        tickets_window,
        text="Maintenance Details",
        font=("Arial", 13, "bold"),
        bg="#0d1b2a",
        fg="white",
        padx=15,
        pady=10
    )

    maintenance_frame.pack(
        fill="x",
        padx=30,
        pady=10
    )

    tk.Label(
        maintenance_frame,
        text="Technician:",
        font=("Arial", 11),
        bg="#0d1b2a",
        fg="white"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=8
    )

    technician_entry = tk.Entry(
        maintenance_frame,
        font=("Arial", 11),
        width=25
    )

    technician_entry.grid(
        row=0,
        column=1,
        padx=10
    )

    tk.Label(
        maintenance_frame,
        text="Repair Cost:",
        font=("Arial", 11),
        bg="#0d1b2a",
        fg="white"
    ).grid(
        row=0,
        column=2,
        padx=10
    )

    cost_entry = tk.Entry(
        maintenance_frame,
        font=("Arial", 11),
        width=15
    )

    cost_entry.grid(
        row=0,
        column=3,
        padx=10
    )

    tk.Label(
        maintenance_frame,
        text="Notes:",
        font=("Arial", 11),
        bg="#0d1b2a",
        fg="white"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=8
    )

    notes_entry = tk.Entry(
        maintenance_frame,
        font=("Arial", 11),
        width=60
    )

    notes_entry.grid(
        row=1,
        column=1,
        columnspan=3,
        padx=10
    )

    def save_maintenance():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Ticket Selected",
                "Please select a ticket first."
            )
            return

        technician = technician_entry.get().strip()
        cost = cost_entry.get().strip()
        notes = notes_entry.get().strip()

        if technician == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Technician name."
            )
            return

        if cost == "":
            cost = "0"

        try:
            cost = float(cost)
        except ValueError:
            messagebox.showwarning(
                "Invalid Cost",
                "Please enter a valid number."
            )
            return

        ticket_id = table.item(
            selected[0]
        )["values"][0]

        connection = sqlite3.connect("campusfix.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE complaints
            SET technician = ?,
                repair_cost = ?,
                maintenance_notes = ?
            WHERE id = ?
            """,
            (
                technician,
                cost,
                notes,
                ticket_id
            )
        )

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Maintenance details saved successfully!"
        )

        technician_entry.delete(0, tk.END)
        cost_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)

    tk.Button(
        maintenance_frame,
        text="Save Maintenance Details",
        font=("Arial", 11, "bold"),
        bg="#5cb85c",
        fg="white",
        width=25,
        height=2,
        command=save_maintenance
    ).grid(
        row=2,
        column=0,
        columnspan=4,
        pady=10
    )


# =========================================================
# SEARCH TICKETS
# =========================================================

def search_tickets():

    search_window = tk.Toplevel(window)

    search_window.title("Search Tickets")
    search_window.geometry("1100x650")
    search_window.configure(bg="#0d1b2a")

    tk.Label(
        search_window,
        text="SEARCH COMPLAINT TICKETS",
        font=("Arial", 24, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).pack(pady=20)

    search_frame = tk.Frame(
        search_window,
        bg="#0d1b2a"
    )

    search_frame.pack(pady=10)

    tk.Label(
        search_frame,
        text="Search:",
        font=("Arial", 13, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).grid(
        row=0,
        column=0,
        padx=10
    )

    search_entry = tk.Entry(
        search_frame,
        font=("Arial", 13),
        width=35
    )

    search_entry.grid(
        row=0,
        column=1,
        padx=10
    )

    search_type = ttk.Combobox(
        search_frame,
        values=[
            "Ticket ID",
            "Student Name",
            "Department"
        ],
        state="readonly",
        font=("Arial", 12),
        width=18
    )

    search_type.grid(
        row=0,
        column=2,
        padx=10
    )

    search_type.set("Student Name")

    table_frame = tk.Frame(
        search_window,
        bg="#0d1b2a"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    columns = (
        "ID",
        "Student",
        "Department",
        "Building",
        "Room",
        "Category",
        "Priority",
        "Status"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)

    table.column("ID", width=50)
    table.column("Student", width=120)
    table.column("Department", width=120)
    table.column("Building", width=120)
    table.column("Room", width=70)
    table.column("Category", width=110)
    table.column("Priority", width=90)
    table.column("Status", width=100)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    def perform_search():

        search_text = search_entry.get().strip()
        selected_type = search_type.get()

        for item in table.get_children():
            table.delete(item)

        if search_text == "":
            messagebox.showwarning(
                "Empty Search",
                "Please enter something to search."
            )
            return

        connection = sqlite3.connect("campusfix.db")
        cursor = connection.cursor()

        if selected_type == "Ticket ID":

            cursor.execute("""
                SELECT
                    id,
                    student_name,
                    department,
                    building,
                    room_number,
                    category,
                    priority,
                    status
                FROM complaints
                WHERE id = ?
            """, (search_text,))

        elif selected_type == "Student Name":

            cursor.execute("""
                SELECT
                    id,
                    student_name,
                    department,
                    building,
                    room_number,
                    category,
                    priority,
                    status
                FROM complaints
                WHERE student_name LIKE ?
            """, ("%" + search_text + "%",))

        else:

            cursor.execute("""
                SELECT
                    id,
                    student_name,
                    department,
                    building,
                    room_number,
                    category,
                    priority,
                    status
                FROM complaints
                WHERE department LIKE ?
            """, ("%" + search_text + "%",))

        results = cursor.fetchall()

        connection.close()

        for complaint in results:

            table.insert(
                "",
                "end",
                values=complaint
            )

        if len(results) == 0:
            messagebox.showinfo(
                "No Results",
                "No complaint found."
            )

    tk.Button(
        search_frame,
        text="Search",
        font=("Arial", 12, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=12,
        height=2,
        command=perform_search
    ).grid(
        row=0,
        column=3,
        padx=10
    )


# =========================================================
# REGISTER COMPLAINT
# =========================================================

def register_complaint():

    complaint_window = tk.Toplevel(window)

    complaint_window.title("Register Complaint")
    complaint_window.geometry("650x1000")
    complaint_window.configure(bg="#0d1b2a")

    tk.Label(
        complaint_window,
        text="REGISTER A COMPLAINT",
        font=("Arial", 24, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).pack(pady=25)

    tk.Label(
        complaint_window,
        text="Student Name",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(anchor="w", padx=50)

    name_entry = tk.Entry(
        complaint_window,
        font=("Arial", 12),
        width=45
    )

    name_entry.pack(pady=5)

    tk.Label(
        complaint_window,
        text="Department",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    department_entry = tk.Entry(
        complaint_window,
        font=("Arial", 12),
        width=45
    )

    department_entry.pack(pady=5)

    tk.Label(
        complaint_window,
        text="Building",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    building_entry = tk.Entry(
        complaint_window,
        font=("Arial", 12),
        width=45
    )

    building_entry.pack(pady=5)

    tk.Label(
        complaint_window,
        text="Room Number",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    room_entry = tk.Entry(
        complaint_window,
        font=("Arial", 12),
        width=45
    )

    room_entry.pack(pady=5)

    tk.Label(
        complaint_window,
        text="Complaint Category",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    category_combo = ttk.Combobox(
        complaint_window,
        values=[
            "Electrical",
            "Plumbing",
            "Cleaning",
            "Furniture",
            "Internet",
            "Other"
        ],
        font=("Arial", 12),
        width=43,
        state="readonly"
    )

    category_combo.pack(pady=5)
    category_combo.set("Select Category")

    tk.Label(
        complaint_window,
        text="Priority",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    priority_combo = ttk.Combobox(
        complaint_window,
        values=[
            "Low",
            "Medium",
            "High",
            "Urgent"
        ],
        font=("Arial", 12),
        width=43,
        state="readonly"
    )

    priority_combo.pack(pady=5)
    priority_combo.set("Select Priority")

    tk.Label(
        complaint_window,
        text="Problem Description",
        font=("Arial", 12),
        bg="#0d1b2a",
        fg="white"
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 0)
    )

    description_text = tk.Text(
        complaint_window,
        font=("Arial", 12),
        width=45,
        height=6
    )

    description_text.pack(pady=5)

    def submit_complaint():

        student_name = name_entry.get().strip()
        department = department_entry.get().strip()
        building = building_entry.get().strip()
        room_number = room_entry.get().strip()
        category = category_combo.get()
        priority = priority_combo.get()

        description = description_text.get(
            "1.0",
            tk.END
        ).strip()

        if student_name == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Student Name."
            )
            return

        if department == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Department."
            )
            return

        if building == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Building."
            )
            return

        if room_number == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Room Number."
            )
            return

        if category == "Select Category":
            messagebox.showwarning(
                "Missing Information",
                "Please select Complaint Category."
            )
            return

        if priority == "Select Priority":
            messagebox.showwarning(
                "Missing Information",
                "Please select Priority."
            )
            return

        if description == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter Problem Description."
            )
            return

        connection = sqlite3.connect("campusfix.db")
        cursor = connection.cursor()

        cursor.execute("""
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
        """, (
            student_name,
            department,
            building,
            room_number,
            category,
            priority,
            description,
            "Pending"
        ))

        connection.commit()
        ticket_id = cursor.lastrowid
        connection.close()

        messagebox.showinfo(
            "Complaint Submitted",
            f"Complaint submitted successfully!\n\nYour Ticket ID is: {ticket_id}\n\nPlease save this Ticket ID to track your complaint."
        )

        complaint_window.destroy()

    tk.Button(
        complaint_window,
        text="Submit Complaint",
        font=("Arial", 13, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=25,
        height=2,
        command=submit_complaint
    ).pack(pady=25)


# =========================================================
# REPORTS
# =========================================================

def show_reports():

    reports_window = tk.Toplevel(window)

    reports_window.title("CampusFix Reports")
    reports_window.geometry("800x650")
    reports_window.configure(bg="#0d1b2a")

    tk.Label(
        reports_window,
        text="CAMPUSFIX REPORTS",
        font=("Arial", 26, "bold"),
        bg="#0d1b2a",
        fg="white"
    ).pack(pady=25)

    # -----------------------------------------------------
    # READ DATABASE USING PANDAS
    # -----------------------------------------------------

    connection = sqlite3.connect("campusfix.db")

    query = """
        SELECT
            id,
            student_name,
            department,
            building,
            room_number,
            category,
            priority,
            description,
            status,
            technician,
            repair_cost,
            maintenance_notes
        FROM complaints
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    # -----------------------------------------------------
    # NO DATA
    # -----------------------------------------------------

    if data.empty:

        tk.Label(
            reports_window,
            text="No complaints available for reports.",
            font=("Arial", 16),
            bg="#0d1b2a",
            fg="white"
        ).pack(pady=40)

        return

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    total = len(data)

    pending = len(
        data[data["status"] == "Pending"]
    )

    in_progress = len(
        data[data["status"] == "In Progress"]
    )

    resolved = len(
        data[data["status"] == "Resolved"]
    )

    total_cost = data["repair_cost"].fillna(0).sum()

    summary_frame = tk.Frame(
        reports_window,
        bg="#0d1b2a"
    )

    summary_frame.pack(pady=10)

    create_report_card(
        summary_frame,
        "TOTAL",
        total,
        0,
        0
    )

    create_report_card(
        summary_frame,
        "PENDING",
        pending,
        0,
        1
    )

    create_report_card(
        summary_frame,
        "IN PROGRESS",
        in_progress,
        1,
        0
    )

    create_report_card(
        summary_frame,
        "RESOLVED",
        resolved,
        1,
        1
    )

    tk.Label(
        reports_window,
        text=f"Total Repair Cost: ₹{total_cost:.2f}",
        font=("Arial", 16, "bold"),
        bg="#0d1b2a",
        fg="#62c6df"
    ).pack(pady=15)

    # -----------------------------------------------------
    # CHART BUTTONS
    # -----------------------------------------------------

    chart_frame = tk.Frame(
        reports_window,
        bg="#0d1b2a"
    )

    chart_frame.pack(pady=20)

    tk.Button(
        chart_frame,
        text="Complaints by Category",
        font=("Arial", 11, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=25,
        height=2,
        command=lambda: show_category_chart(data)
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=10
    )

    tk.Button(
        chart_frame,
        text="Complaints by Status",
        font=("Arial", 11, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=25,
        height=2,
        command=lambda: show_status_chart(data)
    ).grid(
        row=0,
        column=1,
        padx=10,
        pady=10
    )

    tk.Button(
        chart_frame,
        text="Priority Distribution",
        font=("Arial", 11, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        width=25,
        height=2,
        command=lambda: show_priority_chart(data)
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=10
    )

    tk.Button(
        chart_frame,
        text="Export CSV",
        font=("Arial", 11, "bold"),
        bg="#5cb85c",
        fg="white",
        width=25,
        height=2,
        command=lambda: export_csv(data)
    ).grid(
        row=1,
        column=1,
        padx=10,
        pady=10
    )


# =========================================================
# REPORT CARD
# =========================================================

def create_report_card(parent, title, number, row, column):

    frame = tk.Frame(
        parent,
        bg="#62c6df",
        width=220,
        height=100
    )

    frame.grid(
        row=row,
        column=column,
        padx=10,
        pady=10
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=title,
        font=("Arial", 12, "bold"),
        bg="#62c6df",
        fg="#0d1b2a"
    ).pack(pady=10)

    tk.Label(
        frame,
        text=str(number),
        font=("Arial", 24, "bold"),
        bg="#62c6df",
        fg="#0d1b2a"
    ).pack()


# =========================================================
# CATEGORY CHART
# =========================================================

def show_category_chart(data):

    category_counts = data["category"].value_counts()

    plt.figure(figsize=(8, 5))

    category_counts.plot(
        kind="bar"
    )

    plt.title("Complaints by Category")
    plt.xlabel("Category")
    plt.ylabel("Number of Complaints")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# =========================================================
# STATUS CHART
# =========================================================

def show_status_chart(data):

    status_counts = data["status"].value_counts()

    plt.figure(figsize=(7, 5))

    status_counts.plot(
        kind="bar"
    )

    plt.title("Complaints by Status")
    plt.xlabel("Status")
    plt.ylabel("Number of Complaints")

    plt.xticks(rotation=0)

    plt.tight_layout()

    plt.show()


# =========================================================
# PRIORITY CHART
# =========================================================

def show_priority_chart(data):

    priority_counts = data["priority"].value_counts()

    plt.figure(figsize=(7, 5))

    priority_counts.plot(
        kind="pie",
        autopct="%1.1f%%"
    )

    plt.title("Priority Distribution")

    plt.ylabel("")

    plt.tight_layout()

    plt.show()


# =========================================================
# EXPORT CSV
# =========================================================

def export_csv(data):

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[
            ("CSV Files", "*.csv")
        ],
        title="Save Complaint Report"
    )

    if file_path == "":
        return

    data.to_csv(
        file_path,
        index=False
    )

    messagebox.showinfo(
        "Export Successful",
        "Complaint report exported successfully!"
    )


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title("CampusFix - Campus Maintenance System")
window.geometry("1000x700")
window.configure(bg="#0d1b2a")


# =========================================================
# TOP HEADER
# =========================================================

header = tk.Frame(
    window,
    bg="#132f4c",
    height=150
)

header.pack(fill="x")
header.pack_propagate(False)


tk.Label(
    header,
    text="CampusFix",
    font=("Arial", 32, "bold"),
    bg="#132f4c",
    fg="white"
).pack(pady=(25, 5))


tk.Label(
    header,
    text="Campus Maintenance Complaint & Tracking System",
    font=("Arial", 14),
    bg="#132f4c",
    fg="#b8c7d9"
).pack()


# =========================================================
# WELCOME TEXT
# =========================================================

tk.Label(
    window,
    text="Welcome to CampusFix",
    font=("Arial", 22, "bold"),
    bg="#0d1b2a",
    fg="white"
).pack(pady=(35, 5))


tk.Label(
    window,
    text="Manage, track and analyze campus maintenance complaints",
    font=("Arial", 12),
    bg="#0d1b2a",
    fg="#aab7c4"
).pack(pady=(0, 25))


# =========================================================
# BUTTON FRAME
# =========================================================

button_frame = tk.Frame(
    window,
    bg="#0d1b2a"
)

button_frame.pack(pady=5)


# =========================================================
# BUTTON STYLE FUNCTION
# =========================================================

def create_main_button(parent, text, command, row, column):

    button = tk.Button(
        parent,
        text=text,
        font=("Arial", 12, "bold"),
        bg="#62c6df",
        fg="#0d1b2a",
        activebackground="#4fb3cc",
        activeforeground="#0d1b2a",
        width=22,
        height=3,
        relief="flat",
        cursor="hand2",
        command=command
    )

    button.grid(
        row=row,
        column=column,
        padx=15,
        pady=12
    )

    return button


# =========================================================
# MAIN BUTTONS
# =========================================================

create_main_button(
    button_frame,
    "Dashboard",
    show_dashboard,
    0,
    0
)


create_main_button(
    button_frame,
    "Register Complaint",
    register_complaint,
    0,
    1
)


create_main_button(
    button_frame,
    "All Tickets",
    show_all_tickets,
    1,
    0
)


create_main_button(
    button_frame,
    "Search Tickets",
    search_tickets,
    1,
    1
)


create_main_button(
    button_frame,
    "Reports & Analytics",
    show_reports,
    2,
    0
)


# =========================================================
# FOOTER
# =========================================================

tk.Label(
    window,
    text="CampusFix • Maintenance Management System",
    font=("Arial", 10),
    bg="#0d1b2a",
    fg="#718096"
).pack(side="bottom", pady=20)


# =========================================================
# RUN APPLICATION
# =========================================================

window.mainloop()

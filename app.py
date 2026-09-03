
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime

DATABASE = "assignments.db"


def get_connection():
    return sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT NOT NULL,
            weight REAL DEFAULT 0,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


def add_assignment(
    title,
    subject,
    deadline,
    weight,
    priority,
    status,
    notes
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assignments
        (title, subject, deadline, weight, priority, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        subject,
        deadline.isoformat(),
        weight,
        priority,
        status,
        notes,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_assignments():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM assignments ORDER BY deadline ASC",
        conn
    )

    conn.close()

    return df


def delete_assignment(assignment_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM assignments WHERE id = ?",
        (assignment_id,)
    )

    conn.commit()
    conn.close()


def update_assignment(
    assignment_id,
    title,
    subject,
    deadline,
    weight,
    priority,
    status,
    notes
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE assignments
        SET
            title = ?,
            subject = ?,
            deadline = ?,
            weight = ?,
            priority = ?,
            status = ?,
            notes = ?
        WHERE id = ?
    """, (
        title,
        subject,
        deadline.isoformat(),
        weight,
        priority,
        status,
        notes,
        assignment_id
    ))

    conn.commit()
    conn.close()


def update_status(assignment_id, status):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE assignments
        SET status = ?
        WHERE id = ?
    """, (
        status,
        assignment_id
    ))

    conn.commit()
    conn.close()


def calculate_days_remaining(deadline):
    return (deadline - date.today()).days


def priority_icon(priority):
    if priority == "High":
        return "🔴 High"
    elif priority == "Medium":
        return "🟠 Medium"
    return "🟢 Low"


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Assignment Manager",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Assignment & Deadline Manager")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "📊 Dashboard",
        "📝 Assignments",
        "➕ Add Assignment",
        "✏️ Edit Assignment"
    ]
)


# ============================================================
# LOAD DATA
# ============================================================

df = get_assignments()

if not df.empty:

    df["deadline"] = pd.to_datetime(
        df["deadline"]
    ).dt.date

    df["days_remaining"] = df["deadline"].apply(
        calculate_days_remaining
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.header("📊 Dashboard")

    if df.empty:

        st.info(
            "You don't have any assignments yet."
        )

    else:

        total = len(df)

        completed = len(
            df[df["status"] == "Completed"]
        )

        overdue = len(
            df[
                (df["days_remaining"] < 0)
                &
                (df["status"] != "Completed")
            ]
        )

        due_soon = len(
            df[
                (df["days_remaining"].between(0, 3))
                &
                (df["status"] != "Completed")
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📚 Total",
            total
        )

        col2.metric(
            "⏰ Due Soon",
            due_soon
        )

        col3.metric(
            "🔴 Overdue",
            overdue
        )

        col4.metric(
            "✅ Completed",
            completed
        )

        st.divider()

        # Progress

        progress = completed / total

        st.subheader("🎯 Completion Progress")

        st.progress(progress)

        st.write(
            f"{completed}/{total} assignments completed "
            f"({progress * 100:.1f}%)"
        )

        st.divider()

        # Upcoming

        st.subheader("⏰ Upcoming Deadlines")

        upcoming = df[
            (df["days_remaining"] >= 0)
            &
            (df["status"] != "Completed")
        ].sort_values(
            "deadline"
        ).head(5)

        if upcoming.empty:

            st.success(
                "🎉 No upcoming assignments!"
            )

        else:

            for _, row in upcoming.iterrows():

                days = row["days_remaining"]

                if days == 0:
                    deadline_text = "Due today"
                elif days == 1:
                    deadline_text = "Due tomorrow"
                else:
                    deadline_text = f"Due in {days} days"

                st.markdown(
                    f"""
                    ### {row['title']}

                    📚 {row['subject']}  
                    📅 {row['deadline'].strftime('%d %B %Y')}  
                    ⏰ **{deadline_text}**  
                    {priority_icon(row['priority'])}
                    """
                )

                st.divider()

        # Subject chart

        st.subheader("📚 Assignments by Subject")

        subject_counts = df["subject"].value_counts()

        st.bar_chart(subject_counts)


# ============================================================
# ASSIGNMENTS
# ============================================================

elif page == "📝 Assignments":

    st.header("📝 My Assignments")

    if df.empty:

        st.info("No assignments found.")

    else:

        subjects = [
            "All"
        ] + sorted(
            df["subject"].unique().tolist()
        )

        selected_subject = st.selectbox(
            "Filter by subject",
            subjects
        )

        selected_status = st.selectbox(
            "Filter by status",
            [
                "All",
                "Not Started",
                "In Progress",
                "Completed"
            ]
        )

        filtered = df.copy()

        if selected_subject != "All":

            filtered = filtered[
                filtered["subject"]
                == selected_subject
            ]

        if selected_status != "All":

            filtered = filtered[
                filtered["status"]
                == selected_status
            ]

        for _, row in filtered.iterrows():

            with st.container(border=True):

                st.subheader(row["title"])

                st.write(
                    f"📚 **Subject:** {row['subject']}"
                )

                st.write(
                    f"📅 **Deadline:** "
                    f"{row['deadline'].strftime('%d %B %Y')}"
                )

                days = row["days_remaining"]

                if row["status"] == "Completed":

                    st.success("✅ Completed")

                elif days < 0:

                    st.error(
                        f"🔴 {abs(days)} days overdue"
                    )

                elif days == 0:

                    st.error("🔴 Due today")

                elif days == 1:

                    st.warning("🟠 Due tomorrow")

                else:

                    st.info(
                        f"🟢 {days} days remaining"
                    )

                st.write(
                    priority_icon(row["priority"])
                )

                st.write(
                    f"Assignment weight: "
                    f"{row['weight']:.1f}%"
                )

                if row["notes"]:

                    st.write(
                        f"📝 {row['notes']}"
                    )

                new_status = st.selectbox(
                    "Status",
                    [
                        "Not Started",
                        "In Progress",
                        "Completed"
                    ],
                    index=[
                        "Not Started",
                        "In Progress",
                        "Completed"
                    ].index(row["status"]),
                    key=f"status_{row['id']}"
                )

                if new_status != row["status"]:

                    update_status(
                        row["id"],
                        new_status
                    )

                    st.rerun()


# ============================================================
# ADD ASSIGNMENT
# ============================================================

elif page == "➕ Add Assignment":

    st.header("➕ Add Assignment")

    with st.form("assignment_form"):

        title = st.text_input(
            "Assignment name",
            placeholder="e.g. Economics Essay"
        )

        subject = st.text_input(
            "Subject / Course",
            placeholder="e.g. Economics"
        )

        deadline = st.date_input(
            "Deadline",
            value=date.today()
        )

        weight = st.number_input(
            "Assignment weight (%)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=0.5
        )

        priority = st.selectbox(
            "Priority",
            [
                "High",
                "Medium",
                "Low"
            ]
        )

        status = st.selectbox(
            "Status",
            [
                "Not Started",
                "In Progress",
                "Completed"
            ]
        )

        notes = st.text_area(
            "Notes"
        )

        submit = st.form_submit_button(
            "➕ Add Assignment",
            use_container_width=True
        )

        if submit:

            if not title.strip():

                st.error(
                    "Please enter an assignment name."
                )

            elif not subject.strip():

                st.error(
                    "Please enter a subject."
                )

            else:

                add_assignment(
                    title,
                    subject,
                    deadline,
                    weight,
                    priority,
                    status,
                    notes
                )

                st.success(
                    "✅ Assignment added!"
                )

                st.rerun()


# ============================================================
# EDIT ASSIGNMENT
# ============================================================

elif page == "✏️ Edit Assignment":

    st.header("✏️ Edit Assignment")

    if df.empty:

        st.info(
            "There are no assignments to edit."
        )

    else:

        options = {}

        for _, row in df.iterrows():

            options[
                f"{row['title']} — {row['subject']}"
            ] = row["id"]

        selected = st.selectbox(
            "Select assignment",
            list(options.keys())
        )

        assignment_id = options[selected]

        assignment = df[
            df["id"] == assignment_id
        ].iloc[0]

        with st.form("edit_form"):

            title = st.text_input(
                "Assignment name",
                value=assignment["title"]
            )

            subject = st.text_input(
                "Subject",
                value=assignment["subject"]
            )

            deadline = st.date_input(
                "Deadline",
                value=assignment["deadline"]
            )

            weight = st.number_input(
                "Assignment weight (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(assignment["weight"]),
                step=0.5
            )

            priority = st.selectbox(
                "Priority",
                [
                    "High",
                    "Medium",
                    "Low"
                ],
                index=[
                    "High",
                    "Medium",
                    "Low"
                ].index(
                    assignment["priority"]
                )
            )

            status = st.selectbox(
                "Status",
                [
                    "Not Started",
                    "In Progress",
                    "Completed"
                ],
                index=[
                    "Not Started",
                    "In Progress",
                    "Completed"
                ].index(
                    assignment["status"]
                )
            )

            notes = st.text_area(
                "Notes",
                value=assignment["notes"] or ""
            )

            save = st.form_submit_button(
                "💾 Save Changes",
                use_container_width=True
            )

            if save:

                update_assignment(
                    assignment_id,
                    title,
                    subject,
                    deadline,
                    weight,
                    priority,
                    status,
                    notes
                )

                st.success(
                    "✅ Assignment updated!"
                )

                st.rerun()

        st.divider()

        if st.button(
            "🗑️ Delete Assignment"
        ):

            delete_assignment(
                assignment_id
            )

            st.success(
                "Assignment deleted."
            )

            st.rerun()

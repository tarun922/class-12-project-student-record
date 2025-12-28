import mysql.connector
from mysql.connector import Error
from datetime import datetime
from tabulate import tabulate
import os
import csv


class StudentConductDB:
    def __init__(self, host='localhost', user='root', password='', database='student_conduct_db'):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✓ Connected to MySQL database\n")
        except Error as e:
            print(f"✗ Connection error: {e}")
            self.conn = None

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_number VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(15),
                    grade VARCHAR(10),
                    class_section VARCHAR(10),
                    parent_name VARCHAR(100),
                    parent_phone VARCHAR(15),
                    enrollment_date DATE,
                    status ENUM('Active', 'Suspended', 'Expelled') DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS conduct_incidents (
                    incident_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    incident_type VARCHAR(100) NOT NULL,
                    category ENUM('Attendance', 'Academic Dishonesty', 'Behavior', 'Bullying', 'Violence', 'Substance', 'Other') DEFAULT 'Other',
                    description TEXT NOT NULL,
                    severity_score INT CHECK (severity_score >= 1 AND severity_score <= 10),
                    incident_date DATE NOT NULL,
                    incident_time TIME,
                    location VARCHAR(100),
                    witnesses TEXT,
                    reported_by VARCHAR(100),
                    status ENUM('Pending', 'Resolved', 'Escalated') DEFAULT 'Pending',
                    action_taken VARCHAR(500),
                    follow_up_date DATE,
                    parent_notified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    INDEX idx_student_date (student_id, incident_date),
                    INDEX idx_severity (severity_score)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS conduct_actions (
                    action_id INT AUTO_INCREMENT PRIMARY KEY,
                    incident_id INT NOT NULL,
                    action_type VARCHAR(100),
                    action_duration INT,
                    duration_unit ENUM('Minutes', 'Hours', 'Days') DEFAULT 'Days',
                    notes TEXT,
                    action_date DATE,
                    assigned_by VARCHAR(100),
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES conduct_incidents(incident_id) ON DELETE CASCADE
                )
            """)

            self.conn.commit()
            print("✓ All tables created successfully\n")
        except Error as e:
            print(f"✗ Error creating tables: {e}\n")

    def add_student(self, roll_number, name, email, phone, grade, class_section, parent_name, parent_phone):
        try:
            if not name or len(name.strip()) == 0:
                print("✗ Student name cannot be empty")
                return None
            
            self.cursor.execute(
                """INSERT INTO students 
                   (roll_number, name, email, phone, grade, class_section, parent_name, parent_phone, enrollment_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (roll_number, name, email, phone, grade, class_section, parent_name, parent_phone, datetime.now().date())
            )
            self.conn.commit()
            student_id = self.cursor.lastrowid
            print(f"✓ Student '{name}' (Roll: {roll_number}) added successfully (ID: {student_id})\n")
            return student_id
        except mysql.connector.errors.IntegrityError:
            print(f"✗ Roll number '{roll_number}' already exists\n")
            return None
        except Error as e:
            print(f"✗ Error adding student: {e}\n")
            return None

    def record_incident(self, student_id, incident_type, category, description, severity_score, 
                       location, witnesses, reported_by, action_taken=None):
        if not (1 <= severity_score <= 10):
            print("✗ Severity score must be between 1 and 10\n")
            return False
        
        try:
            self.cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
            if not self.cursor.fetchone():
                print(f"✗ Student ID {student_id} does not exist\n")
                return False

            self.cursor.execute(
                """INSERT INTO conduct_incidents 
                   (student_id, incident_type, category, description, severity_score, 
                    incident_date, incident_time, location, witnesses, reported_by, action_taken)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (student_id, incident_type, category, description, severity_score, 
                 datetime.now().date(), datetime.now().time(), location, witnesses, reported_by, action_taken)
            )
            self.conn.commit()
            print(f"✓ Incident recorded for student ID {student_id} with severity {severity_score}/10\n")
            return self.cursor.lastrowid
        except Error as e:
            print(f"✗ Error recording incident: {e}\n")
            return False

    def add_action_to_incident(self, incident_id, action_type, duration, duration_unit, notes, assigned_by):
        try:
            self.cursor.execute(
                """INSERT INTO conduct_actions 
                   (incident_id, action_type, action_duration, duration_unit, notes, action_date, assigned_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (incident_id, action_type, duration, duration_unit, notes, datetime.now().date(), assigned_by)
            )
            self.conn.commit()
            print(f"✓ Action '{action_type}' added to incident {incident_id}\n")
            return True
        except Error as e:
            print(f"✗ Error adding action: {e}\n")
            return False

    def get_student_record(self, student_id):
        try:
            self.cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = self.cursor.fetchone()
            
            if not student:
                print(f"✗ Student ID {student_id} not found\n")
                return None
            
            self.cursor.execute(
                """SELECT * FROM conduct_incidents 
                   WHERE student_id = %s 
                   ORDER BY incident_date DESC""",
                (student_id,)
            )
            incidents = self.cursor.fetchall()
            
            return {'student': student, 'incidents': incidents}
        except Error as e:
            print(f"✗ Error retrieving record: {e}\n")
            return None

    def get_student_stats(self, student_id):
        try:
            self.cursor.execute(
                """SELECT COUNT(*) as total_incidents, 
                          AVG(severity_score) as avg_score,
                          MAX(severity_score) as worst_incident,
                          MIN(severity_score) as least_severe
                   FROM conduct_incidents 
                   WHERE student_id = %s""",
                (student_id,)
            )
            result = self.cursor.fetchone()
            
            if result['total_incidents'] == 0:
                return {'total_incidents': 0, 'avg_score': 0, 'worst': 0, 'least': 0}
            
            self.cursor.execute(
                """SELECT category, COUNT(*) as count
                   FROM conduct_incidents
                   WHERE student_id = %s
                   GROUP BY category""",
                (student_id,)
            )
            category_breakdown = self.cursor.fetchall()
            
            return {
                'total_incidents': result['total_incidents'],
                'avg_score': round(result['avg_score'], 2),
                'worst_incident': result['worst_incident'],
                'least_severe': result['least_severe'],
                'category_breakdown': category_breakdown
            }
        except Error as e:
            print(f"✗ Error retrieving stats: {e}\n")
            return None

    def list_all_students(self, status='Active'):
        try:
            self.cursor.execute(
                """SELECT s.student_id, s.roll_number, s.name, s.grade, s.class_section,
                          s.status, COUNT(c.incident_id) as incident_count,
                          ROUND(AVG(c.severity_score), 2) as avg_severity
                   FROM students s
                   LEFT JOIN conduct_incidents c ON s.student_id = c.student_id
                   WHERE s.status = %s
                   GROUP BY s.student_id
                   ORDER BY s.student_id ASC""",
                (status,)
            )
            students = self.cursor.fetchall()
            return students
        except Error as e:
            print(f"✗ Error listing students: {e}\n")
            return []

    def get_high_risk_students(self, threshold=7):
        try:
            self.cursor.execute(
                """SELECT s.student_id, s.roll_number, s.name, s.grade, s.class_section,
                          COUNT(c.incident_id) as incident_count,
                          ROUND(AVG(c.severity_score), 2) as avg_score
                   FROM students s
                   JOIN conduct_incidents c ON s.student_id = c.student_id
                   GROUP BY s.student_id
                   HAVING AVG(c.severity_score) >= %s
                   ORDER BY s.student_id ASC""",
                (threshold,)
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Error retrieving high-risk students: {e}\n")
            return []

    def get_incidents_by_category(self, category):
        try:
            self.cursor.execute(
                """SELECT c.incident_id, s.student_id, s.name, c.incident_type, c.severity_score, 
                          c.incident_date, c.status
                   FROM conduct_incidents c
                   JOIN students s ON c.student_id = s.student_id
                   WHERE c.category = %s
                   ORDER BY c.incident_date DESC""",
                (category,)
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Error retrieving incidents: {e}\n")
            return []

    def get_pending_incidents(self):
        try:
            self.cursor.execute(
                """SELECT c.incident_id, s.student_id, s.name, c.incident_type, c.severity_score,
                          c.incident_date, c.status
                   FROM conduct_incidents c
                   JOIN students s ON c.student_id = s.student_id
                   WHERE c.status IN ('Pending', 'Escalated')
                   ORDER BY c.severity_score DESC, c.incident_date ASC"""
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Error retrieving pending incidents: {e}\n")
            return []

    def update_incident_status(self, incident_id, status, follow_up_date=None):
        try:
            self.cursor.execute(
                "UPDATE conduct_incidents SET status = %s, follow_up_date = %s WHERE incident_id = %s",
                (status, follow_up_date, incident_id)
            )
            self.conn.commit()
            print(f"✓ Incident {incident_id} status updated to '{status}'\n")
            return True
        except Error as e:
            print(f"✗ Error updating incident: {e}\n")
            return False

    def mark_parent_notified(self, incident_id):
        try:
            self.cursor.execute(
                "UPDATE conduct_incidents SET parent_notified = TRUE WHERE incident_id = %s",
                (incident_id,)
            )
            self.conn.commit()
            print(f"✓ Parents marked as notified for incident {incident_id}\n")
            return True
        except Error as e:
            print(f"✗ Error updating notification status: {e}\n")
            return False

    def update_student_status(self, student_id, status):
        try:
            self.cursor.execute(
                "UPDATE students SET status = %s WHERE student_id = %s",
                (status, student_id)
            )
            self.conn.commit()
            print(f"✓ Student status updated to '{status}'\n")
            return True
        except Error as e:
            print(f"✗ Error updating student status: {e}\n")
            return False

    def delete_student(self, student_id):
        try:
            self.cursor.execute("SELECT name FROM students WHERE student_id = %s", (student_id,))
            result = self.cursor.fetchone()
            
            if not result:
                print(f"✗ Student ID {student_id} not found\n")
                return False
            
            self.cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            self.conn.commit()
            print(f"✓ Student '{result['name']}' and all records deleted\n")
            return True
        except Error as e:
            print(f"✗ Error deleting student: {e}\n")
            return False

    def get_monthly_report(self, month, year):
        try:
            self.cursor.execute(
                """SELECT c.incident_id, s.student_id, s.name, c.incident_type, c.category, 
                          c.severity_score, c.incident_date
                   FROM conduct_incidents c
                   JOIN students s ON c.student_id = s.student_id
                   WHERE MONTH(c.incident_date) = %s AND YEAR(c.incident_date) = %s
                   ORDER BY c.incident_date DESC""",
                (month, year)
            )
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Error retrieving monthly report: {e}\n")
            return []

    def get_severity_distribution(self):
        try:
            self.cursor.execute(
                """SELECT 
                     SUM(CASE WHEN severity_score <= 3 THEN 1 ELSE 0 END) as minor,
                     SUM(CASE WHEN severity_score BETWEEN 4 AND 6 THEN 1 ELSE 0 END) as moderate,
                     SUM(CASE WHEN severity_score BETWEEN 7 AND 9 THEN 1 ELSE 0 END) as serious,
                     SUM(CASE WHEN severity_score = 10 THEN 1 ELSE 0 END) as critical
                   FROM conduct_incidents"""
            )
            return self.cursor.fetchone()
        except Error as e:
            print(f"✗ Error retrieving distribution: {e}\n")
            return None

    def export_student_card_csv(self, student_id):
        try:
            record = self.get_student_record(student_id)
            if not record:
                print(f"✗ Student ID {student_id} not found\n")
                return False
            
            student = record['student']
            incidents = record['incidents']
            stats = self.get_student_stats(student_id)
            
            filename = f"{student_id}_{student['roll_number']}.csv"
            filepath = os.path.join('student_cards', filename)
            
            os.makedirs('student_cards', exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['STUDENT CONDUCT RECORD CARD'])
                writer.writerow([])
                
                writer.writerow(['STUDENT DETAILS'])
                writer.writerow(['Student ID', student['student_id']])
                writer.writerow(['Roll Number', student['roll_number']])
                writer.writerow(['Name', student['name']])
                writer.writerow(['Email', student['email']])
                writer.writerow(['Phone', student['phone']])
                writer.writerow(['Grade', student['grade']])
                writer.writerow(['Class Section', student['class_section']])
                writer.writerow(['Parent Name', student['parent_name']])
                writer.writerow(['Parent Phone', student['parent_phone']])
                writer.writerow(['Status', student['status']])
                writer.writerow(['Enrollment Date', student['enrollment_date']])
                writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                writer.writerow(['CONDUCT STATISTICS'])
                writer.writerow(['Total Incidents', stats['total_incidents']])
                writer.writerow(['Average Severity Score', f"{stats['avg_score']}/10"])
                writer.writerow(['Worst Incident Score', f"{stats['worst_incident']}/10"])
                writer.writerow(['Least Severe Score', f"{stats['least_severe']}/10"])
                writer.writerow([])
                
                if stats['category_breakdown']:
                    writer.writerow(['INCIDENTS BY CATEGORY'])
                    for item in stats['category_breakdown']:
                        writer.writerow([item['category'], item['count']])
                    writer.writerow([])
                
                writer.writerow(['DETAILED INCIDENT RECORDS'])
                writer.writerow(['Incident ID', 'Date', 'Time', 'Type', 'Category', 'Description', 
                                'Severity', 'Location', 'Reported By', 'Status', 'Action Taken', 
                                'Parent Notified'])
                
                for incident in incidents:
                    writer.writerow([
                        incident['incident_id'],
                        incident['incident_date'],
                        incident['incident_time'] or 'N/A',
                        incident['incident_type'],
                        incident['category'],
                        incident['description'][:100] if incident['description'] else 'N/A',
                        incident['severity_score'],
                        incident['location'] or 'N/A',
                        incident['reported_by'] or 'N/A',
                        incident['status'],
                        incident['action_taken'] or 'N/A',
                        'Yes' if incident['parent_notified'] else 'No'
                    ])
            
            print(f"✓ Student card exported successfully!")
            print(f"  File saved as: {filepath}\n")
            return True
            
        except Error as e:
            print(f"✗ Error exporting student card: {e}\n")
            return False

    def export_all_students_csv(self):
        try:
            self.cursor.execute(
                """SELECT s.student_id, s.roll_number, s.name, s.grade, s.class_section, s.status,
                          COUNT(c.incident_id) as incident_count,
                          ROUND(AVG(c.severity_score), 2) as avg_severity
                   FROM students s
                   LEFT JOIN conduct_incidents c ON s.student_id = c.student_id
                   GROUP BY s.student_id
                   ORDER BY s.student_id ASC"""
            )
            students = self.cursor.fetchall()
            
            filename = f"all_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('student_cards', filename)
            
            os.makedirs('student_cards', exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['STUDENT CONDUCT SUMMARY REPORT'])
                writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                writer.writerow(['Student ID', 'Roll Number', 'Name', 'Grade', 'Section', 
                                'Status', 'Total Incidents', 'Average Severity Score'])
                
                for student in students:
                    writer.writerow([
                        student['student_id'],
                        student['roll_number'],
                        student['name'],
                        student['grade'],
                        student['class_section'],
                        student['status'],
                        student['incident_count'] or 0,
                        student['avg_severity'] or 'N/A'
                    ])
            
            print(f"✓ All students exported successfully!")
            print(f"  File saved as: {filepath}\n")
            return True
            
        except Error as e:
            print(f"✗ Error exporting students: {e}\n")
            return False

    def export_monthly_report_csv(self, month, year):
        try:
            self.cursor.execute(
                """SELECT c.incident_id, s.student_id, s.roll_number, s.name, 
                          c.incident_type, c.category, c.severity_score, c.incident_date,
                          c.location, c.reported_by, c.status
                   FROM conduct_incidents c
                   JOIN students s ON c.student_id = s.student_id
                   WHERE MONTH(c.incident_date) = %s AND YEAR(c.incident_date) = %s
                   ORDER BY c.incident_date DESC""",
                (month, year)
            )
            incidents = self.cursor.fetchall()
            
            filename = f"monthly_report_{month:02d}_{year}.csv"
            filepath = os.path.join('student_cards', filename)
            
            os.makedirs('student_cards', exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['MONTHLY INCIDENT REPORT'])
                writer.writerow([f'Month: {month}/{year}'])
                writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                writer.writerow(['Incident ID', 'Student ID', 'Roll Number', 'Student Name', 
                                'Incident Type', 'Category', 'Severity', 'Date', 'Location', 
                                'Reported By', 'Status'])
                
                for incident in incidents:
                    writer.writerow([
                        incident['incident_id'],
                        incident['student_id'],
                        incident['roll_number'],
                        incident['name'],
                        incident['incident_type'],
                        incident['category'],
                        incident['severity_score'],
                        incident['incident_date'],
                        incident['location'] or 'N/A',
                        incident['reported_by'] or 'N/A',
                        incident['status']
                    ])
            
            print(f"✓ Monthly report exported successfully!")
            print(f"  File saved as: {filepath}\n")
            return True
            
        except Error as e:
            print(f"✗ Error exporting monthly report: {e}\n")
            return False

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("\n✓ Database connection closed")


class ConductManagementSystem:
    def __init__(self, db):
        self.db = db
        self.db.create_tables()

    def display_menu(self):
        print("\n" + "="*60)
        print("STUDENT CONDUCT MANAGEMENT SYSTEM".center(60))
        print("="*60)
        print("1.  Add New Student")
        print("2.  Record Incident")
        print("3.  View Student Record")
        print("4.  View Student Statistics")
        print("5.  List All Students")
        print("6.  High-Risk Students Report")
        print("7.  Pending Incidents")
        print("8.  Monthly Report")
        print("9.  Severity Distribution")
        print("10. Update Incident Status")
        print("11. Manage Student Status")
        print("12. Delete Student")
        print("\n--- EXPORT OPTIONS ---")
        print("13. Export Individual Student Card (CSV)")
        print("14. Export All Students Summary (CSV)")
        print("15. Export Monthly Report (CSV)")
        print("16. Exit")
        print("="*60)

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-16): ").strip()

            if choice == '1':
                self.add_student_menu()
            elif choice == '2':
                self.record_incident_menu()
            elif choice == '3':
                self.view_student_record()
            elif choice == '4':
                self.view_student_stats()
            elif choice == '5':
                self.list_students()
            elif choice == '6':
                self.high_risk_report()
            elif choice == '7':
                self.pending_incidents()
            elif choice == '8':
                self.monthly_report()
            elif choice == '9':
                self.severity_report()
            elif choice == '10':
                self.update_incident()
            elif choice == '11':
                self.manage_student_status()
            elif choice == '12':
                self.delete_student()
            elif choice == '13':
                self.export_student_card()
            elif choice == '14':
                self.export_all_students()
            elif choice == '15':
                self.export_monthly_report()
            elif choice == '16':
                print("\nThank you for using the system!")
                self.db.close()
                break
            else:
                print("✗ Invalid choice. Please try again.")

    def add_student_menu(self):
        print("\n" + "-"*40)
        print("ADD NEW STUDENT")
        print("-"*40)
        roll = input("Roll Number: ").strip()
        name = input("Student Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        grade = input("Grade (e.g., 10, 11, 12): ").strip()
        section = input("Class Section (e.g., A, B, C): ").strip()
        parent_name = input("Parent Name: ").strip()
        parent_phone = input("Parent Phone: ").strip()
        
        self.db.add_student(roll, name, email, phone, grade, section, parent_name, parent_phone)

    def record_incident_menu(self):
        print("\n" + "-"*40)
        print("RECORD INCIDENT")
        print("-"*40)
        student_id = int(input("Student ID: "))
        incident_type = input("Incident Type: ").strip()
        print("\nCategory: Attendance | Academic Dishonesty | Behavior | Bullying | Violence | Substance | Other")
        category = input("Select Category: ").strip()
        description = input("Description: ").strip()
        severity = int(input("Severity Score (1-10): "))
        location = input("Location/Class: ").strip()
        witnesses = input("Witnesses (comma-separated): ").strip()
        reported_by = input("Reported By (Staff Name): ").strip()
        action = input("Initial Action (optional): ").strip()
        
        self.db.record_incident(student_id, incident_type, category, description, 
                               severity, location, witnesses, reported_by, action)

    def view_student_record(self):
        print("\n" + "-"*40)
        student_id = int(input("Enter Student ID: "))
        record = self.db.get_student_record(student_id)
        
        if record:
            s = record['student']
            print(f"\nStudent: {s['name']} (ID: {s['student_id']}, Roll: {s['roll_number']})")
            print(f"Grade: {s['grade']}-{s['class_section']} | Email: {s['email']}")
            print(f"Parent: {s['parent_name']} | Phone: {s['parent_phone']}")
            print(f"Status: {s['status']}\n")
            
            if record['incidents']:
                headers = ['ID', 'Type', 'Category', 'Severity', 'Date', 'Status']
                data = [[i['incident_id'], i['incident_type'], i['category'], 
                        i['severity_score'], i['incident_date'], i['status']] 
                       for i in record['incidents']]
                print(tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No incidents recorded.")

    def view_student_stats(self):
        print("\n" + "-"*40)
        student_id = int(input("Enter Student ID: "))
        stats = self.db.get_student_stats(student_id)
        
        if stats:
            print(f"\nTotal Incidents: {stats['total_incidents']}")
            print(f"Average Severity: {stats['avg_score']}/10")
            print(f"Worst Incident: {stats['worst_incident']}/10")
            print(f"Least Severe: {stats['least_severe']}/10")
            
            if stats['category_breakdown']:
                print("\nCategory Breakdown:")
                for item in stats['category_breakdown']:
                    print(f"  {item['category']}: {item['count']}")

    def list_students(self):
        print("\n" + "-"*40)
        status = input("Filter by Status (Active/Suspended/Expelled) [Leave empty for Active]: ").strip() or 'Active'
        students = self.db.list_all_students(status)
        
        if students:
            headers = ['ID', 'Roll', 'Name', 'Grade', 'Section', 'Status', 'Incidents', 'Avg Severity']
            print(tabulate(students, headers=headers, tablefmt='grid'))
        else:
            print("No students found.")

    def high_risk_report(self):
        print("\n" + "-"*40)
        threshold = float(input("Enter severity threshold (1-10) [Default: 7]: ") or 7)
        high_risk = self.db.get_high_risk_students(threshold)
        
        if high_risk:
            headers = ['ID', 'Roll', 'Name', 'Grade', 'Section', 'Incidents', 'Avg Severity']
            print(f"\nStudents with Average Severity >= {threshold}:")
            print(tabulate(high_risk, headers=headers, tablefmt='grid'))
        else:
            print(f"No students found with average severity >= {threshold}")

    def pending_incidents(self):
        print("\n" + "-"*40)
        pending = self.db.get_pending_incidents()
        
        if pending:
            headers = ['ID', 'Student ID', 'Student', 'Type', 'Severity', 'Date', 'Status']
            print("\nPending & Escalated Incidents:")
            print(tabulate(pending, headers=headers, tablefmt='grid'))
        else:
            print("No pending incidents.")

    def monthly_report(self):
        print("\n" + "-"*40)
        month = int(input("Enter Month (1-12): "))
        year = int(input("Enter Year: "))
        report = self.db.get_monthly_report(month, year)
        
        if report:
            headers = ['ID', 'Student ID', 'Student', 'Type', 'Category', 'Severity', 'Date']
            print(f"\nIncidents for {month}/{year}:")
            print(tabulate(report, headers=headers, tablefmt='grid'))
        else:
            print("No incidents found for this month.")

    def severity_report(self):
        print("\n" + "-"*40)
        dist = self.db.get_severity_distribution()
        if dist:
            print(f"\nSeverity Distribution (All Incidents):")
            print(f"Minor (1-3):     {dist['minor'] or 0} incidents")
            print(f"Moderate (4-6):  {dist['moderate'] or 0} incidents")
            print(f"Serious (7-9):   {dist['serious'] or 0} incidents")
            print(f"Critical (10):   {dist['critical'] or 0} incidents")

    def update_incident(self):
        print("\n" + "-"*40)
        incident_id = int(input("Enter Incident ID: "))
        print("Status: Pending | Resolved | Escalated")
        status = input("New Status: ").strip()
        follow_up = input("Follow-up Date (YYYY-MM-DD) [Optional]: ").strip() or None
        self.db.update_incident_status(incident_id, status, follow_up)

    def manage_student_status(self):
        print("\n" + "-"*40)
        student_id = int(input("Enter Student ID: "))
        print("Status: Active | Suspended | Expelled")
        status = input("New Status: ").strip()
        self.db.update_student_status(student_id, status)

    def delete_student(self):
        print("\n" + "-"*40)
        student_id = int(input("Enter Student ID: "))
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == 'yes':
            self.db.delete_student(student_id)

    def export_student_card(self):
        print("\n" + "-"*40)
        print("EXPORT STUDENT CARD")
        print("-"*40)
        student_id = int(input("Enter Student ID: "))
        self.db.export_student_card_csv(student_id)

    def export_all_students(self):
        print("\n" + "-"*40)
        print("EXPORT ALL STUDENTS")
        print("-"*40)
        confirm = input("Export all students to CSV? (yes/no): ").strip().lower()
        if confirm == 'yes':
            self.db.export_all_students_csv()

    def export_monthly_report(self):
        print("\n" + "-"*40)
        print("EXPORT MONTHLY REPORT")
        print("-"*40)
        month = int(input("Enter Month (1-12): "))
        year = int(input("Enter Year: "))
        self.db.export_monthly_report_csv(month, year)


if __name__ == "__main__":
    db = StudentConductDB(
        host='localhost',
        user='root',
        password='your_password',
        database='student_conduct_db'
    )
    
    if db.conn:
        system = ConductManagementSystem(db)
        system.run()
    else:
        print("Failed to connect to database.")

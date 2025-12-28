from student_conduct_system import StudentConductDB, ConductManagementSystem

db = StudentConductDB(
    host='localhost',
    user='root',
    password='your_password',
    database='student_conduct_db'
)

db.create_tables()

print("\n" + "="*70)
print("STUDENT CONDUCT MANAGEMENT SYSTEM - SAMPLE USAGE")
print("="*70)

print("\n--- 1. ADD STUDENTS ---")
s1 = db.add_student("A001", "John Doe", "john@school.com", "9876543210", "10", "A", "Mr. Doe", "9876543210")
s2 = db.add_student("A002", "Jane Smith", "jane@school.com", "9876543211", "10", "B", "Mrs. Smith", "9876543211")
s3 = db.add_student("A003", "Mike Johnson", "mike@school.com", "9876543212", "11", "A", "Mr. Johnson", "9876543212")
s4 = db.add_student("A004", "Sarah Williams", "sarah@school.com", "9876543213", "9", "C", "Mrs. Williams", "9876543213")
s5 = db.add_student("A005", "David Brown", "david@school.com", "9876543214", "10", "B", "Mr. Brown", "9876543214")

print("\n--- 2. RECORD INCIDENTS ---")
inc1 = db.record_incident(
    student_id=s1,
    incident_type="Cheating in Exam",
    category="Academic Dishonesty",
    description="Caught copying answers from neighboring student during final exam",
    severity_score=8,
    location="Exam Hall A",
    witnesses="Ms. Principal, Mr. Invigilator",
    reported_by="Mr. Invigilator",
    action_taken="1 hour detention"
)

inc2 = db.record_incident(
    student_id=s1,
    incident_type="Disrupting Class",
    category="Behavior",
    description="Making unnecessary noise and disturbing other students",
    severity_score=3,
    location="Class 10A",
    witnesses="Ms. Teacher",
    reported_by="Ms. Teacher",
    action_taken="Warning given"
)

inc3 = db.record_incident(
    student_id=s2,
    incident_type="Bullying Incident",
    category="Bullying",
    description="Harassing junior student in corridors",
    severity_score=9,
    location="School Corridor",
    witnesses="Student witnesses",
    reported_by="Mr. Principal",
    action_taken="Parent meeting scheduled"
)

inc4 = db.record_incident(
    student_id=s3,
    incident_type="Physical Fight",
    category="Violence",
    description="Physical altercation with another student over sports",
    severity_score=7,
    location="Sports Field",
    witnesses="Coach, Students",
    reported_by="Mr. Coach",
    action_taken="3 days suspension"
)

inc5 = db.record_incident(
    student_id=s3,
    incident_type="Late Submission",
    category="Attendance",
    description="Project submission 5 days late without valid reason",
    severity_score=2,
    location="N/A",
    witnesses="N/A",
    reported_by="Mr. Teacher",
    action_taken="Grade reduction"
)

inc6 = db.record_incident(
    student_id=s4,
    incident_type="Vandalism",
    category="Behavior",
    description="Writing on school desk and breaking chair",
    severity_score=6,
    location="Classroom 9C",
    witnesses="Janitor",
    reported_by="Principal",
    action_taken="Fine + Repair cost"
)

inc7 = db.record_incident(
    student_id=s5,
    incident_type="Substance",
    category="Substance",
    description="Found with cigarettes in school premises",
    severity_score=10,
    location="Behind School Building",
    witnesses="Security Guard",
    reported_by="Security Head",
    action_taken="Parents called, Investigation ongoing"
)

print("\n--- 3. ADD ACTIONS TO INCIDENTS ---")
db.add_action_to_incident(
    incident_id=inc1,
    action_type="Detention",
    duration=1,
    duration_unit="Hours",
    notes="To be served after school hours",
    assigned_by="Mr. Principal"
)

db.add_action_to_incident(
    incident_id=inc3,
    action_type="Parent Meeting",
    duration=1,
    duration_unit="Days",
    notes="Parents to be called for discussion",
    assigned_by="Mr. Principal"
)

print("\n--- 4. GET INDIVIDUAL STUDENT RECORD ---")
record = db.get_student_record(s1)
if record:
    student = record['student']
    print(f"\nStudent: {student['name']} (ID: {student['student_id']}, Roll: {student['roll_number']})")
    print(f"Grade: {student['grade']}-{student['class_section']}")
    print(f"Email: {student['email']} | Phone: {student['phone']}")
    print(f"Parent: {student['parent_name']} | Parent Phone: {student['parent_phone']}")
    print(f"Status: {student['status']}")
    print(f"\nTotal Incidents: {len(record['incidents'])}")
    for incident in record['incidents']:
        print(f"  - {incident['incident_type']} ({incident['category']}) - Severity: {incident['severity_score']}/10 - {incident['incident_date']}")

print("\n--- 5. GET STUDENT STATISTICS ---")
stats = db.get_student_stats(s1)
print(f"\nStudent ID {s1} Statistics:")
print(f"  Total Incidents: {stats['total_incidents']}")
print(f"  Average Severity: {stats['avg_score']}/10")
print(f"  Worst Incident: {stats['worst_incident']}/10")
print(f"  Least Severe: {stats['least_severe']}/10")
if stats['category_breakdown']:
    print(f"  Category Breakdown:")
    for item in stats['category_breakdown']:
        print(f"    - {item['category']}: {item['count']}")

print("\n--- 6. LIST ALL STUDENTS ---")
students = db.list_all_students(status='Active')
print(f"\nAll Active Students:")
print(f"{'ID':<5} {'Roll':<10} {'Name':<20} {'Grade':<8} {'Section':<10} {'Incidents':<12} {'Avg Severity':<15}")
print("-" * 90)
for student in students:
    print(f"{student['student_id']:<5} {student['roll_number']:<10} {student['name']:<20} {student['grade']:<8} {student['class_section']:<10} {student['incident_count'] or 0:<12} {student['avg_severity'] or 'N/A':<15}")

print("\n--- 7. GET HIGH-RISK STUDENTS (Severity >= 7) ---")
high_risk = db.get_high_risk_students(threshold=7)
print(f"\nHigh-Risk Students (Average Severity >= 7):")
print(f"{'ID':<5} {'Roll':<10} {'Name':<20} {'Grade':<8} {'Section':<10} {'Incidents':<12} {'Avg Severity':<15}")
print("-" * 90)
for student in high_risk:
    print(f"{student['student_id']:<5} {student['roll_number']:<10} {student['name']:<20} {student['grade']:<8} {student['class_section']:<10} {student['incident_count']:<12} {student['avg_score']:<15}")

print("\n--- 8. GET HIGH-RISK STUDENTS (Severity >= 5) ---")
high_risk_5 = db.get_high_risk_students(threshold=5)
print(f"\nHigh-Risk Students (Average Severity >= 5):")
for student in high_risk_5:
    print(f"  {student['name']} (ID: {student['student_id']}) - Avg Severity: {student['avg_score']}/10 - Incidents: {student['incident_count']}")

print("\n--- 9. GET INCIDENTS BY CATEGORY ---")
behavior_incidents = db.get_incidents_by_category('Behavior')
print(f"\nBehavior Category Incidents:")
print(f"{'ID':<8} {'Student ID':<12} {'Name':<20} {'Type':<25} {'Severity':<10} {'Date':<12}")
print("-" * 90)
for incident in behavior_incidents:
    print(f"{incident['incident_id']:<8} {incident['student_id']:<12} {incident['name']:<20} {incident['incident_type']:<25} {incident['severity_score']:<10} {incident['incident_date']:<12}")

print("\n--- 10. GET PENDING INCIDENTS ---")
pending = db.get_pending_incidents()
print(f"\nPending & Escalated Incidents:")
print(f"{'ID':<8} {'Student ID':<12} {'Name':<20} {'Type':<25} {'Severity':<10} {'Status':<15}")
print("-" * 95)
for incident in pending:
    print(f"{incident['incident_id']:<8} {incident['student_id']:<12} {incident['name']:<20} {incident['incident_type']:<25} {incident['severity_score']:<10} {incident['status']:<15}")

print("\n--- 11. UPDATE INCIDENT STATUS ---")
if inc1:
    print(f"Updating incident {inc1} status to 'Resolved'")
    db.update_incident_status(inc1, 'Resolved', follow_up_date='2025-02-15')

print("\n--- 12. MARK PARENT NOTIFIED ---")
if inc3:
    print(f"Marking parents as notified for incident {inc3}")
    db.mark_parent_notified(inc3)

print("\n--- 13. UPDATE STUDENT STATUS ---")
print(f"Updating student {s3} status to 'Suspended'")
db.update_student_status(s3, 'Suspended')

print("\n--- 14. GET MONTHLY REPORT ---")
from datetime import datetime
current_month = datetime.now().month
current_year = datetime.now().year
monthly_report = db.get_monthly_report(current_month, current_year)
print(f"\nIncidents for {current_month}/{current_year}:")
print(f"{'ID':<8} {'Student ID':<12} {'Name':<20} {'Type':<25} {'Category':<20} {'Severity':<10}")
print("-" * 100)
for incident in monthly_report:
    print(f"{incident['incident_id']:<8} {incident['student_id']:<12} {incident['name']:<20} {incident['incident_type']:<25} {incident['category']:<20} {incident['severity_score']:<10}")

print("\n--- 15. GET SEVERITY DISTRIBUTION ---")
distribution = db.get_severity_distribution()
if distribution:
    print(f"\nSeverity Distribution (All Incidents):")
    print(f"  Minor (1-3):     {distribution['minor'] or 0} incidents")
    print(f"  Moderate (4-6):  {distribution['moderate'] or 0} incidents")
    print(f"  Serious (7-9):   {distribution['serious'] or 0} incidents")
    print(f"  Critical (10):   {distribution['critical'] or 0} incidents")
    total = (distribution['minor'] or 0) + (distribution['moderate'] or 0) + (distribution['serious'] or 0) + (distribution['critical'] or 0)
    print(f"  TOTAL:           {total} incidents")

print("\n--- 16. EXPORT INDIVIDUAL STUDENT CARD (CSV) ---")
print(f"Exporting student card for ID {s1}...")
db.export_student_card_csv(s1)

print("\n--- 17. EXPORT ALL STUDENTS SUMMARY (CSV) ---")
print("Exporting all students summary...")
db.export_all_students_csv()

print("\n--- 18. EXPORT MONTHLY REPORT (CSV) ---")
print(f"Exporting monthly report for {current_month}/{current_year}...")
db.export_monthly_report_csv(current_month, current_year)

print("\n--- 19. DELETE STUDENT ---")
print(f"Note: Deleting student would remove all associated records")
print(f"Skipping deletion in demo mode")

print("\n" + "="*70)
print("SAMPLE USAGE DEMONSTRATION COMPLETED")
print("="*70)

db.close()

# Student Conduct Management System

A comprehensive Python + MySQL application for managing and tracking student conduct records with severity scoring (1-10 scale), detailed incident tracking, and CSV export capabilities.

## Features

### Core Functionality
- **Student Management**: Add, view, update, and delete student records with complete details
- **Incident Recording**: Log conduct incidents with severity scores (1-10), categories, and detailed descriptions
- **Conduct Statistics**: Analyze student behavior patterns with average scores, worst incidents, and category breakdowns
- **High-Risk Identification**: Automatically identify students exceeding severity thresholds
- **Status Management**: Track student status (Active, Suspended, Expelled)
- **Parent Notifications**: Mark parent notification status for incidents

### Reporting & Analytics
- Individual student conduct cards with full history
- Student roster with incident counts and average severity
- Monthly incident reports with filtering
- Severity distribution analysis (Minor, Moderate, Serious, Critical)
- Pending and escalated incidents dashboard
- Category-wise incident breakdown

### Export Features
- Export individual student conduct cards as CSV (filename: `{student_id}_{roll_number}.csv`)
- Export all students summary report as CSV
- Export monthly reports as CSV
- Automatic folder creation for exports (`student_cards/`)
- Professional formatting with metadata and timestamps

## Installation

### Requirements
- Python 3.7+
- MySQL Server 5.7+

### Dependencies
```bash
pip install mysql-connector-python tabulate
```

### Database Setup
```sql
CREATE DATABASE student_conduct_db;
```

## Configuration

Update the database credentials in the main execution section:

```python
db = StudentConductDB(
    host='localhost',
    user='root',
    password='your_password',
    database='student_conduct_db'
)
```

## Database Schema

### Tables

**students**
- student_id (INT, Primary Key)
- roll_number (VARCHAR, Unique)
- name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- grade (VARCHAR)
- class_section (VARCHAR)
- parent_name (VARCHAR)
- parent_phone (VARCHAR)
- enrollment_date (DATE)
- status (ENUM: Active, Suspended, Expelled)
- created_at, updated_at (TIMESTAMP)

**conduct_incidents**
- incident_id (INT, Primary Key)
- student_id (INT, Foreign Key)
- incident_type (VARCHAR)
- category (ENUM: Attendance, Academic Dishonesty, Behavior, Bullying, Violence, Substance, Other)
- description (TEXT)
- severity_score (INT, 1-10)
- incident_date (DATE)
- incident_time (TIME)
- location (VARCHAR)
- witnesses (TEXT)
- reported_by (VARCHAR)
- status (ENUM: Pending, Resolved, Escalated)
- action_taken (VARCHAR)
- follow_up_date (DATE)
- parent_notified (BOOLEAN)
- created_at (TIMESTAMP)

**conduct_actions**
- action_id (INT, Primary Key)
- incident_id (INT, Foreign Key)
- action_type (VARCHAR)
- action_duration (INT)
- duration_unit (ENUM: Minutes, Hours, Days)
- notes (TEXT)
- action_date (DATE)
- assigned_by (VARCHAR)
- completed (BOOLEAN)
- created_at (TIMESTAMP)

## Usage

### Running the Application
```bash
python student_conduct_system.py
```

### Menu Options

| Option | Description |
|--------|-------------|
| 1 | Add New Student |
| 2 | Record Incident |
| 3 | View Student Record |
| 4 | View Student Statistics |
| 5 | List All Students |
| 6 | High-Risk Students Report |
| 7 | Pending Incidents |
| 8 | Monthly Report |
| 9 | Severity Distribution |
| 10 | Update Incident Status |
| 11 | Manage Student Status |
| 12 | Delete Student |
| 13 | Export Individual Student Card (CSV) |
| 14 | Export All Students Summary (CSV) |
| 15 | Export Monthly Report (CSV) |
| 16 | Exit |

### Example Workflow

#### 1. Add a Student
```
Enter Student ID: 1
Roll Number: A001
Student Name: John Doe
Email: john@school.com
Phone: 9876543210
Grade: 10
Class Section: A
Parent Name: Mr. Doe
Parent Phone: 9876543210
```

#### 2. Record an Incident
```
Student ID: 1
Incident Type: Cheating in Exam
Category: Academic Dishonesty
Description: Caught copying during final exam
Severity Score: 8
Location: Hall A
Witnesses: Ms. Smith, Mr. Johnson
Reported By: Mr. Principal
Initial Action: 1 hour detention
```

#### 3. Export Student Card
```
Enter Student ID: 1
```
Creates: `1_A001.csv`

## Severity Score Scale

- **1-3 (Minor)**: Late submission, minor disruption, dress code violation
- **4-6 (Moderate)**: Repeated warnings, assignment not submitted, cheating attempt
- **7-9 (Serious)**: Fighting, bullying, serious academic dishonesty, vandalism
- **10 (Critical)**: Severe violence, drug/substance involvement, extreme misconduct

## CSV Export Format

### Student Card Export
Includes:
- Student details (ID, Roll number, name, contact info)
- Conduct statistics (total incidents, average severity)
- Category breakdown
- Detailed incident records with all metadata

### All Students Export
Includes:
- Student ID, Roll number, Name
- Grade, Section, Status
- Total incidents count
- Average severity score

### Monthly Report Export
Includes:
- Incident ID, Student ID, Roll number
- Student name, Incident type, Category
- Severity score, Date
- Location, Reported by, Status

## Key Methods

### StudentConductDB Class

```python
add_student(roll_number, name, email, phone, grade, class_section, parent_name, parent_phone)
record_incident(student_id, incident_type, category, description, severity_score, location, witnesses, reported_by, action_taken)
get_student_record(student_id)
get_student_stats(student_id)
list_all_students(status='Active')
get_high_risk_students(threshold=7)
get_pending_incidents()
update_incident_status(incident_id, status, follow_up_date)
update_student_status(student_id, status)
export_student_card_csv(student_id)
export_all_students_csv()
export_monthly_report_csv(month, year)
```

## File Structure

```
student_conduct_system/
├── student_conduct_system.py    (Main application)
├── README.md                     (This file)
└── student_cards/               (Exported CSV files - auto-created)
    ├── 1_A001.csv
    ├── 2_B002.csv
    ├── all_students_20250101_120000.csv
    └── monthly_report_01_2025.csv
```

## Error Handling

- Duplicate roll number prevention
- Student existence validation
- Severity score range validation (1-10)
- Database connection error handling
- File operation error handling
- Proper exception messages for user guidance

## Security Considerations

- Use strong MySQL passwords in production
- Implement user authentication for the application
- Restrict database access to trusted networks
- Regular database backups
- Audit logging for sensitive operations

## Troubleshooting

### Connection Failed
- Verify MySQL server is running
- Check host, user, and password credentials
- Ensure database `student_conduct_db` exists

### Table Creation Failed
- Verify MySQL user has CREATE TABLE privileges
- Check for existing tables with conflicting names
- Ensure database is selected

### CSV Export Failed
- Verify write permissions in application directory
- Ensure `student_cards/` folder has proper permissions
- Check disk space availability

## Future Enhancements

- Web-based dashboard with Flask/Django
- Email notifications to parents
- Advanced analytics and visualizations
- Role-based access control
- Audit trail logging
- Backup and restore functionality
- Multi-language support
- Mobile app integration

## Support

For issues, feature requests, or contributions, please contact the development team.

## License

This project is licensed under the MIT License.

## Version

**v1.0.0** - Initial Release (January 2025)

---

**Last Updated**: January 2025

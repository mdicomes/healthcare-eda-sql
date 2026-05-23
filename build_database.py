import sqlite3

def build_ehr_database(path="../ehr.db"):
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS patients (
            patient_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name    TEXT NOT NULL,
            last_name     TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            sex           TEXT CHECK(sex IN ('M','F','O')),
            zip_code      TEXT
        );

        CREATE TABLE IF NOT EXISTS encounters (
            encounter_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id     INTEGER NOT NULL REFERENCES patients(patient_id),
            encounter_date DATE NOT NULL,
            encounter_type TEXT CHECK(encounter_type IN ('inpatient','outpatient','emergency','telehealth')),
            facility       TEXT,
            provider       TEXT
        );

        CREATE TABLE IF NOT EXISTS diagnoses (
            diagnosis_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id   INTEGER NOT NULL REFERENCES encounters(encounter_id),
            icd10_code     TEXT NOT NULL,
            description    TEXT,
            diagnosis_type TEXT CHECK(diagnosis_type IN ('primary','secondary'))
        );

        CREATE TABLE IF NOT EXISTS medications (
            medication_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id   INTEGER NOT NULL REFERENCES encounters(encounter_id),
            drug_name      TEXT NOT NULL,
            dose           TEXT,
            route          TEXT,
            start_date     DATE,
            end_date       DATE
        );

        CREATE TABLE IF NOT EXISTS lab_results (
            result_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL REFERENCES encounters(encounter_id),
            test_name    TEXT NOT NULL,
            loinc_code   TEXT,
            result_value REAL,
            unit         TEXT,
            result_date  DATE,
            flag         TEXT CHECK(flag IN ('normal','high','low','critical'))
                         DEFAULT 'normal'
        );
    """)

    # Patients
    cur.executemany(
        "INSERT INTO patients (first_name, last_name, date_of_birth, sex, zip_code) VALUES (?,?,?,?,?)",
        [
            ("Maria",  "Santos",  "1968-03-14", "F", "87102"),
            ("James",  "Okafor",  "1955-11-02", "M", "87110"),
            ("Priya",  "Sharma",  "1979-07-22", "F", "87104"),
            ("Robert", "Chen",    "1942-01-30", "M", "87108"),
            ("Lisa",   "Trevino", "1990-05-05", "F", "87106"),
        ]
    )

    # Encounters
    cur.executemany(
        "INSERT INTO encounters (patient_id, encounter_date, encounter_type, facility, provider) VALUES (?,?,?,?,?)",
        [
            (1, "2023-01-10", "outpatient",  "UNM Clinic",     "Dr. Patel"),
            (1, "2023-06-15", "outpatient",  "UNM Clinic",     "Dr. Patel"),
            (2, "2023-02-20", "inpatient",   "UNMH",           "Dr. Kim"),
            (2, "2023-08-05", "outpatient",  "UNM Clinic",     "Dr. Kim"),
            (3, "2023-03-12", "outpatient",  "UNM Clinic",     "Dr. Reyes"),
            (3, "2023-09-18", "telehealth",  "UNM Telehealth", "Dr. Reyes"),
            (4, "2023-04-07", "emergency",   "UNMH ED",        "Dr. Smith"),
            (5, "2023-05-22", "outpatient",  "UNM Clinic",     "Dr. Patel"),
            (5, "2023-11-03", "outpatient",  "UNM Clinic",     "Dr. Patel"),
        ]
    )

    # Diagnoses
    cur.executemany(
        "INSERT INTO diagnoses (encounter_id, icd10_code, description, diagnosis_type) VALUES (?,?,?,?)",
        [
            (1, "E11.9",  "Type 2 diabetes, uncontrolled",     "primary"),
            (1, "I10",    "Essential hypertension",             "secondary"),
            (2, "E11.65", "Type 2 diabetes with hyperglycemia", "primary"),
            (2, "E11.9",  "Type 2 diabetes follow-up",          "primary"),
            (3, "I10",    "Essential hypertension",             "primary"),
            (4, "I10",    "Hypertension, follow-up",            "primary"),
            (5, "J18.9",  "Pneumonia, unspecified",             "primary"),
            (6, "J18.9",  "Pneumonia, follow-up",               "primary"),
            (7, "I21.9",  "Acute MI, unspecified",              "primary"),
            (8, "Z00.00", "Annual wellness visit",              "primary"),
            (9, "E11.9",  "Type 2 diabetes screening",          "primary"),
        ]
    )

    # Medications
    cur.executemany(
        "INSERT INTO medications (encounter_id, drug_name, dose, route, start_date, end_date) VALUES (?,?,?,?,?,?)",
        [
            (1, "Metformin",    "500mg",   "oral",  "2023-01-10", None),
            (1, "Lisinopril",   "10mg",    "oral",  "2023-01-10", None),
            (2, "Metformin",    "1000mg",  "oral",  "2023-06-15", None),
            (3, "Insulin",      "10 units","subq",  "2023-02-20", "2023-03-05"),
            (4, "Metformin",    "500mg",   "oral",  "2023-08-05", None),
            (5, "Amlodipine",   "5mg",     "oral",  "2023-03-12", None),
            (7, "Aspirin",      "325mg",   "oral",  "2023-04-07", None),
            (7, "Atorvastatin", "40mg",    "oral",  "2023-04-07", None),
            (8, "Amoxicillin",  "500mg",   "oral",  "2023-05-22", "2023-06-05"),
        ]
    )

    # Lab results
    cur.executemany(
        "INSERT INTO lab_results (encounter_id, test_name, loinc_code, result_value, unit, result_date, flag) VALUES (?,?,?,?,?,?,?)",
        [
            (1, "HbA1c",      "4548-4",  8.2,   "%",      "2023-01-10", "high"),
            (1, "Creatinine", "2160-0",  1.1,   "mg/dL",  "2023-01-10", "normal"),
            (2, "HbA1c",      "4548-4",  7.6,   "%",      "2023-06-15", "high"),
            (2, "eGFR",       "62238-1", 72.0,  "mL/min", "2023-06-15", "normal"),
            (3, "Glucose",    "2345-7",  320.0, "mg/dL",  "2023-02-20", "critical"),
            (4, "HbA1c",      "4548-4",  7.9,   "%",      "2023-08-05", "high"),
            (5, "BMP-Sodium", "2951-2",  139.0, "mmol/L", "2023-03-12", "normal"),
            (7, "Troponin",   "6598-7",  2.4,   "ng/mL",  "2023-04-07", "critical"),
            (7, "BNP",        "42637-9", 180.0, "pg/mL",  "2023-04-07", "high"),
            (9, "HbA1c",      "4548-4",  6.1,   "%",      "2023-11-03", "normal"),
        ]
    )

    conn.commit()
    conn.close()
    print(f"EHR database built successfully at: {path}")
    print("Tables created: patients, encounters, diagnoses, medications, lab_results")


if __name__ == "__main__":
    build_ehr_database()
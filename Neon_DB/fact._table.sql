CREATE TABLE "fact_admission" (
	"admission_id" varchar(50) PRIMARY KEY,
	"patient_id" varchar(50),
	"doctor_id" varchar(50),
	"disease_id" varchar(50),
	"department_id" varchar(50),
	"admit_date" date,
	"discharge_date" date,
	"severity" varchar(50) NOT NULL,
	"sample_id" integer,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP,
	"batch_id" varchar(50),
	"source_system" varchar(50) DEFAULT 'HIS'
);
CREATE UNIQUE INDEX "fact_admission_pkey" ON "fact_admission" ("admission_id");
ALTER TABLE "fact_admission" ADD CONSTRAINT "fact_admission_department_id_fkey" FOREIGN KEY ("department_id") REFERENCES "dim_departments"("department_id") ON DELETE CASCADE;
ALTER TABLE "fact_admission" ADD CONSTRAINT "fact_admission_disease_id_fkey" FOREIGN KEY ("disease_id") REFERENCES "dim_diseases"("disease_id") ON DELETE CASCADE;
ALTER TABLE "fact_admission" ADD CONSTRAINT "fact_admission_doctor_id_fkey" FOREIGN KEY ("doctor_id") REFERENCES "dim_doctors"("doctor_id") ON DELETE CASCADE;
ALTER TABLE "fact_admission" ADD CONSTRAINT "fact_admission_patient_id_fkey" FOREIGN KEY ("patient_id") REFERENCES "dim_patients"("patient_id") ON DELETE CASCADE;
ALTER TABLE "fact_admission" ADD CONSTRAINT "fact_admission_sample_id_fkey" FOREIGN KEY ("sample_id") REFERENCES "mtsamples"("sample_id") ON DELETE CASCADE;

---

CREATE TABLE "fact_billing" (
	"billingid" varchar(50) PRIMARY KEY,
	"admissionid" varchar(50),
	"patientid" varchar(50),
	"insuranceprovider" varchar(50) NOT NULL,
	"totalamount" varchar(20) NOT NULL,
	"insurancecoveredamount" varchar(20) NOT NULL,
	"patientresponsibility" varchar(20) NOT NULL,
	"paymentstatus" varchar(15),
	"billingdate" date NOT NULL,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP,
	"batch_id" varchar(50),
	"source_system" varchar(50) DEFAULT 'Billing App',
	CONSTRAINT "fact_billing_paymentstatus_check" CHECK (((paymentstatus)::text = ANY ((ARRAY['Paid'::character varying, 'Pending'::character varying, 'Appealed'::character varying])::text[])))
);
CREATE UNIQUE INDEX "fact_billing_pkey" ON "fact_billing" ("billingid");
ALTER TABLE "fact_billing" ADD CONSTRAINT "fact_billing_admissionid_fkey" FOREIGN KEY ("admissionid") REFERENCES "fact_admission"("admission_id") ON DELETE CASCADE;
ALTER TABLE "fact_billing" ADD CONSTRAINT "fact_billing_patientid_fkey" FOREIGN KEY ("patientid") REFERENCES "dim_patients"("patient_id") ON DELETE CASCADE;

---

CREATE TABLE "fact_lab_reports" (
	"labreportid" varchar(50) PRIMARY KEY,
	"admissionid" varchar(50),
	"patientid" varchar(50),
	"testname" varchar(50) NOT NULL,
	"resultvalue" varchar(50) NOT NULL,
	"unit" varchar(20) NOT NULL,
	"referencerange" varchar(50) NOT NULL,
	"flag" varchar(50),
	"testdate" date,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP,
	"batch_id" varchar(50),
	"source_system" varchar(50) DEFAULT 'LIMS',
	CONSTRAINT "fact_lab_reports_flag_check" CHECK (((flag)::text = ANY ((ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying])::text[])))
);
CREATE UNIQUE INDEX "fact_lab_reports_pkey" ON "fact_lab_reports" ("labreportid");
ALTER TABLE "fact_lab_reports" ADD CONSTRAINT "fact_lab_reports_admissionid_fkey" FOREIGN KEY ("admissionid") REFERENCES "fact_admission"("admission_id") ON DELETE CASCADE;
ALTER TABLE "fact_lab_reports" ADD CONSTRAINT "fact_lab_reports_patientid_fkey" FOREIGN KEY ("patientid") REFERENCES "dim_patients"("patient_id") ON DELETE CASCADE;

---

CREATE TABLE "fact_prescription" (
	"prescription_id" varchar(50) PRIMARY KEY,
	"admission_id" varchar(50),
	"patient_id" varchar(50),
	"doctor_id" varchar(50),
	"medication_name" varchar(60) NOT NULL,
	"dosage" varchar(20) NOT NULL,
	"route" varchar(20) NOT NULL,
	"frequency" varchar(30) NOT NULL,
	"prescription_date" date NOT NULL,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP,
	"batch_id" varchar(50),
	"source_system" varchar(50) DEFAULT 'HIS'
);
CREATE UNIQUE INDEX "fact_prescription_pkey" ON "fact_prescription" ("prescription_id");
ALTER TABLE "fact_prescription" ADD CONSTRAINT "fact_prescription_admission_id_fkey" FOREIGN KEY ("admission_id") REFERENCES "fact_admission"("admission_id") ON DELETE CASCADE;
ALTER TABLE "fact_prescription" ADD CONSTRAINT "fact_prescription_doctor_id_fkey" FOREIGN KEY ("doctor_id") REFERENCES "dim_doctors"("doctor_id") ON DELETE CASCADE;
ALTER TABLE "fact_prescription" ADD CONSTRAINT "fact_prescription_patient_id_fkey" FOREIGN KEY ("patient_id") REFERENCES "dim_patients"("patient_id") ON DELETE CASCADE;

---

CREATE TABLE "mtsamples" (
	"sample_id" integer PRIMARY KEY,
	"description" text NOT NULL,
	"medical_specialty" varchar(60) NOT NULL,
	"sample_name" varchar(50) NOT NULL,
	"transcription" text NOT NULL,
	"keywords" text NOT NULL
);
CREATE UNIQUE INDEX "mtsamples_pkey" ON "mtsamples" ("sample_id");

---

CREATE TABLE "track_raw" (
	"title" text,
	"artist" text,
	"album" text,
	"album_id" integer,
	"count" integer,
	"rating" integer,
	"len" integer
);

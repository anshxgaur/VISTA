CREATE TABLE "dim_diseases" (
	"disease_id" varchar(50) PRIMARY KEY,
	"diseasename" varchar(100) NOT NULL,
	"departmentname" varchar(50) NOT NULL,
	"icd10_code" varchar(50) NOT NULL,
	"severity" varchar(50) NOT NULL,
	"genderconstraint" varchar(20) NOT NULL,
	"ageconstraint" varchar(50) NOT NULL,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT "dim_diseases_ageconstraint_check" CHECK (((ageconstraint)::text = ANY ((ARRAY['All'::character varying, 'Adult'::character varying, 'Senior'::character varying])::text[]))),
	CONSTRAINT "dim_diseases_genderconstraint_check" CHECK (((genderconstraint)::text = ANY ((ARRAY['Male'::character varying, 'Female'::character varying, 'All'::character varying])::text[])))
);
CREATE UNIQUE INDEX "dim_diseases_pkey" ON "dim_diseases" ("disease_id");

---

CREATE TABLE "dim_departments" (
	"department_id" varchar(50) PRIMARY KEY,
	"department_name" varchar(50) NOT NULL,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX "dim_departments_pkey" ON "dim_departments" ("department_id");

---

CREATE TABLE "dim_doctors" (
	"doctor_id" varchar(50) PRIMARY KEY,
	"doctor_name" varchar(50) NOT NULL,
	"gender" varchar(20) NOT NULL,
	"age" integer NOT NULL,
	"specialty" varchar(60) NOT NULL,
	"qualification" varchar(20) NOT NULL,
	"experience_years" integer,
	"phone_number" varchar(50) NOT NULL,
	"email" varchar(100) NOT NULL,
	"load_date" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX "dim_doctors_pkey" ON "dim_doctors" ("doctor_id");

---

CREATE TABLE "dim_patients" (
	"patient_id" varchar(50) PRIMARY KEY,
	"first_name" varchar(50) NOT NULL,
	"last_name" varchar(50) NOT NULL,
	"gender" varchar(10),
	"age" integer NOT NULL,
	"blood_group" varchar(10),
	"city" varchar(50) NOT NULL,
	"state" varchar(50) NOT NULL,
	"country" varchar(50) NOT NULL,
	"phone_number" varchar(50) NOT NULL,
	"email" varchar(100) NOT NULL,
	"eff_start_date" date,
	"eff_end_date" date,
	"is_current" boolean DEFAULT true,
	CONSTRAINT "dim_patients_blood_group_check" CHECK (((blood_group)::text = ANY ((ARRAY['A+'::character varying, 'A-'::character varying, 'B+'::character varying, 'B-'::character varying, 'AB+'::character varying, 'AB-'::character varying, 'O+'::character varying, 'O-'::character varying])::text[]))),
	CONSTRAINT "dim_patients_gender_check" CHECK (((gender)::text = ANY ((ARRAY['Male'::character varying, 'Female'::character varying, 'All'::character varying])::text[])))
);
CREATE UNIQUE INDEX "dim_patients_pkey" ON "dim_patients" ("patient_id");


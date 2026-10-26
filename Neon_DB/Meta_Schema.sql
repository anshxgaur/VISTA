CREATE TABLE "meta"."column_registry" (
	"column_id" serial PRIMARY KEY,
	"table_name" varchar(100) NOT NULL,
	"column_name" varchar(100) NOT NULL,
	"data_type" varchar(50),
	"is_key" boolean DEFAULT false,
	"key_type" varchar(10),
	"references_table" varchar(100),
	"is_pil" boolean DEFAULT false,
	"business_definition" varchar(500),
	CONSTRAINT "column_registry_table_name_column_name_key" UNIQUE("table_name","column_name")
);
CREATE UNIQUE INDEX "column_registry_pkey" ON "meta"."column_registry" ("column_id");
CREATE UNIQUE INDEX "column_registry_table_name_column_name_key" ON "meta"."column_registry" ("table_name","column_name");
ALTER TABLE "meta"."column_registry" ADD CONSTRAINT "column_registry_table_name_fkey" FOREIGN KEY ("table_name") REFERENCES "meta"."table_registry"("table_name");

---

CREATE TABLE "meta"."data_lineage" (
	"lineage_id" serial PRIMARY KEY,
	"source_system" varchar(100),
	"source_object" varchar(200),
	"target_table" varchar(100),
	"transformation_logic" varchar(1000),
	"last_updated" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX "data_lineage_pkey" ON "meta"."data_lineage" ("lineage_id");
ALTER TABLE "meta"."data_lineage" ADD CONSTRAINT "data_lineage_target_table_fkey" FOREIGN KEY ("target_table") REFERENCES "meta"."table_registry"("table_name");

---

CREATE TABLE "meta"."etl_load_log" (
	"load_id" serial PRIMARY KEY,
	"table_name" varchar(100) NOT NULL,
	"batch_id" varchar(50) NOT NULL,
	"start_time" timestamp,
	"end_time" timestamp,
	"rows_inserted" integer,
	"rows_updated" integer,
	"rows_rejected" integer,
	"status" varchar(20),
	"error_message" varchar(1000),
	CONSTRAINT "etl_load_log_status_check" CHECK (((status)::text = ANY ((ARRAY['SUCCESS'::character varying, 'FAILED'::character varying, 'PARTIAL'::character varying])::text[])))
);
CREATE UNIQUE INDEX "etl_load_log_pkey" ON "meta"."etl_load_log" ("load_id");
ALTER TABLE "meta"."etl_load_log" ADD CONSTRAINT "etl_load_log_table_name_fkey" FOREIGN KEY ("table_name") REFERENCES "meta"."table_registry"("table_name");

---

CREATE TABLE "meta"."scd_config" (
	"table_name" varchar(100) PRIMARY KEY,
	"scd_type" varchar(10) NOT NULL,
	"tracked_columns" varchar(500),
	"effective_start_col" varchar(50),
	"effective_end_col" varchar(50),
	"is_current_col" varchar(50),
	CONSTRAINT "scd_config_scd_type_check" CHECK (((scd_type)::text = ANY ((ARRAY['SCD1'::character varying, 'SCD2'::character varying, 'SCD3'::character varying])::text[])))
);
CREATE UNIQUE INDEX "scd_config_pkey" ON "meta"."scd_config" ("table_name");
ALTER TABLE "meta"."scd_config" ADD CONSTRAINT "scd_config_table_name_fkey" FOREIGN KEY ("table_name") REFERENCES "meta"."table_registry"("table_name");

---

CREATE TABLE "meta"."table_registry" (
	"table_id" serial PRIMARY KEY,
	"schema_name" varchar(50) DEFAULT 'public' NOT NULL,
	"table_name" varchar(100) NOT NULL CONSTRAINT "table_registry_table_name_key" UNIQUE,
	"table_type" varchar(10) NOT NULL,
	"grain" varchar(255),
	"source_system" varchar(100),
	"business_owner" varchar(100),
	"description" varchar(500),
	"created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
	"updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT "table_registry_table_type_check" CHECK (((table_type)::text = ANY ((ARRAY['FACT'::character varying, 'DIM'::character varying])::text[])))
);
CREATE UNIQUE INDEX "table_registry_pkey" ON "meta"."table_registry" ("table_id");
CREATE UNIQUE INDEX "table_registry_table_name_key" ON "meta"."table_registry" ("table_name");

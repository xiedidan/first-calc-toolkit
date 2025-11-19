DROP TABLE IF EXISTS "TB_KSCB_YJ";
CREATE TABLE "TB_KSCB_YJ" (
    "YLJGDM" varchar(33),
    "FID" varchar(75),
    "TJND" varchar(6),
    "TJYF" varchar(3),
    "FSOURCE" varchar(30),
    "FBUSQTY" numeric(18,2),
    "DEPTID" varchar(45),
    "DEPTNAME" varchar(75),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_KSCB_YJ" IS '医技业务量中间表';
COMMENT ON COLUMN "TB_KSCB_YJ"."YLJGDM" IS '医疗机构组代码';
COMMENT ON COLUMN "TB_KSCB_YJ"."FID" IS '主键';
COMMENT ON COLUMN "TB_KSCB_YJ"."TJND" IS '统计年度';
COMMENT ON COLUMN "TB_KSCB_YJ"."TJYF" IS '统计月份';
COMMENT ON COLUMN "TB_KSCB_YJ"."FSOURCE" IS '来源类型';
COMMENT ON COLUMN "TB_KSCB_YJ"."FBUSQTY" IS '业务量';
COMMENT ON COLUMN "TB_KSCB_YJ"."DEPTID" IS '科室编码';
COMMENT ON COLUMN "TB_KSCB_YJ"."DEPTNAME" IS '科室名称';
COMMENT ON COLUMN "TB_KSCB_YJ"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_KSCB_YJ"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_KSCB_YJ"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_KSCB_YJ"."YLYL2" IS '预留二';
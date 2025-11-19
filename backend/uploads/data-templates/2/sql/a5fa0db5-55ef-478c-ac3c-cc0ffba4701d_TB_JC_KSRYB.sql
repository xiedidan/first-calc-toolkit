DROP TABLE IF EXISTS "TB_JC_KSRYB";
CREATE TABLE "TB_JC_KSRYB" (
    "FID" varchar(54),
    "YLJGDM" varchar(33),
    "RYID" varchar(15),
    "XM" varchar(30),
    "KSID" varchar(15),
    "KSMC" varchar(30),
    "ZZZID" varchar(15),
    "ZZZMC" varchar(30),
    "XL" varchar(30),
    "TYBS" numeric,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_JC_KSRYB" IS '科室人员表';
COMMENT ON COLUMN "TB_JC_KSRYB"."FID" IS '唯一码';
COMMENT ON COLUMN "TB_JC_KSRYB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_JC_KSRYB"."RYID" IS '人员 ID';
COMMENT ON COLUMN "TB_JC_KSRYB"."XM" IS '姓名';
COMMENT ON COLUMN "TB_JC_KSRYB"."KSID" IS '科室 ID';
COMMENT ON COLUMN "TB_JC_KSRYB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_JC_KSRYB"."ZZZID" IS '主诊组 ID';
COMMENT ON COLUMN "TB_JC_KSRYB"."ZZZMC" IS '主诊组名称';
COMMENT ON COLUMN "TB_JC_KSRYB"."XL" IS '序列';
COMMENT ON COLUMN "TB_JC_KSRYB"."TYBS" IS '停用标识';
COMMENT ON COLUMN "TB_JC_KSRYB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_JC_KSRYB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_JC_KSRYB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_JC_KSRYB"."YLYL2" IS '预留二';
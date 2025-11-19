DROP TABLE IF EXISTS "TB_YB_CZBJL";
CREATE TABLE "TB_YB_CZBJL" (
    "YLJGDM" varchar(33),
    "TJND" varchar(6),
    "TJYF" varchar(3),
    "ZEFYJE" numeric(15,4),
    "BXSBJE" numeric(15,4),
    "CYFJES" numeric(15,4),
    "YYZCDCBJE" numeric(15,4),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YB_CZBJL" IS '医院分担超指标统计';
COMMENT ON COLUMN "TB_YB_CZBJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_YB_CZBJL"."TJND" IS '统计年度';
COMMENT ON COLUMN "TB_YB_CZBJL"."TJYF" IS '统计月份';
COMMENT ON COLUMN "TB_YB_CZBJL"."ZEFYJE" IS '总额预付金额';
COMMENT ON COLUMN "TB_YB_CZBJL"."BXSBJE" IS '报销申报金额';
COMMENT ON COLUMN "TB_YB_CZBJL"."CYFJES" IS '超预付金额数';
COMMENT ON COLUMN "TB_YB_CZBJL"."YYZCDCBJE" IS '医院自承担超标金额';
COMMENT ON COLUMN "TB_YB_CZBJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YB_CZBJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YB_CZBJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YB_CZBJL"."YLYL2" IS '预留二';
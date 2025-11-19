DROP TABLE IF EXISTS "TB_STAT_LIS_Report";
CREATE TABLE "TB_STAT_LIS_Report" (
    "YLJGDM" varchar(33),
    "YWRQ" varchar(12),
    "JYBGDLB" varchar(6),
    "BGDZFS" numeric,
    "MZBGDFS" numeric,
    "ZYBGDFS" numeric,
    "QTYWBGDFS" numeric,
    "JYRC" numeric,
    "MZJYRC" numeric,
    "ZYJYRC" numeric,
    "QTYWJCRS" numeric,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_STAT_LIS_Report" IS '实验室检验报告数量日汇总';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."YWRQ" IS '业务日期';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."JYBGDLB" IS '检验报告单类别编码';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."BGDZFS" IS '报告单总份数';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."MZBGDFS" IS '门诊报告单份数';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."ZYBGDFS" IS '住院报告单份数';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."QTYWBGDFS" IS '其他业务报告单份数';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."JYRC" IS '检验人次';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."MZJYRC" IS '门诊检验人次';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."ZYJYRC" IS '住院检验人次';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."QTYWJCRS" IS '其他业务检验人次';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_STAT_LIS_Report"."YLYL2" IS '预留二';
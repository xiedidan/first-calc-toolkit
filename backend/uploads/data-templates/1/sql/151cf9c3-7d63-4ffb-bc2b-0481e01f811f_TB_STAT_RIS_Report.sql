DROP TABLE IF EXISTS "TB_STAT_RIS_Report";
CREATE TABLE "TB_STAT_RIS_Report" (
    "YLJGDM" varchar(33),
    "YWRQ" varchar(12),
    "JCLX" varchar(24),
    "BGDZFS" numeric,
    "MZBGDFS" numeric,
    "ZYBGDFS" numeric,
    "QTYWBGDFS" numeric,
    "JCRC" numeric,
    "MZJCRC" numeric,
    "ZYJCRC" numeric,
    "QTYWJCRS" numeric,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_STAT_RIS_Report" IS '医学影像检查报告数量日汇总';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."YWRQ" IS '业务日期';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."JCLX" IS '检查类型名称';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."BGDZFS" IS '报告单总份数';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."MZBGDFS" IS '门诊报告单份数';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."ZYBGDFS" IS '住院报告单份数';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."QTYWBGDFS" IS '其他业务报告单份数';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."JCRC" IS '检查人次';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."MZJCRC" IS '门诊检查人次';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."ZYJCRC" IS '住院检查人次';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."QTYWJCRS" IS '其他业务检查人次';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_STAT_RIS_Report"."YLYL2" IS '预留二';
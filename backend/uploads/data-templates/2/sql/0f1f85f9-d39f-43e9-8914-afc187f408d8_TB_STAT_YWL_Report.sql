DROP TABLE IF EXISTS "TB_STAT_YWL_Report";
CREATE TABLE "TB_STAT_YWL_Report" (
    "YLJGDM" varchar(33),
    "YWSJ" varchar(12),
    "MZRC" numeric(15),
    "JZRC" numeric(15),
    "FRMZRC" numeric(15),
    "FXMZRC" numeric(15),
    "TJRC" numeric(15),
    "JCRC" numeric(15),
    "JYRC" numeric(15),
    "RYRC" numeric(15),
    "QNJSCYRC" numeric(15),
    "GCSRGBLS" numeric(15),
    "ZYRS" numeric(15),
    "ZYCWS" numeric(15),
    "SJZYCWS" numeric(15),
    "KCW" numeric(15),
    "SSJCZLS" numeric(15),
    "MJZYLFY" numeric(15,4),
    "ZYYLFY" numeric(15,4),
    "MJZYPFY" numeric(15,4),
    "ZYYPFY" numeric(15,4),
    "MJZYBYLFY" numeric(15,4),
    "ZYYBYLFY" numeric(15,4),
    "MJZYBYPFY" numeric(15,4),
    "ZYYBYPFY" numeric(15,4),
    "ZYSJFSFY" numeric(15,4),
    "CYHZYLSR" numeric(15,4),
    "CYHZYPSR" numeric(15,4),
    "CYHZYBYLSR" numeric(15,4),
    "CYHZYBYPSR" numeric(15,4),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_STAT_YWL_Report" IS '业务量、收入统计表';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."YWSJ" IS '业务时间';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."MZRC" IS '门诊人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."JZRC" IS '急诊人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."FRMZRC" IS '发热门诊人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."FXMZRC" IS '腹泻门诊人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."TJRC" IS '体检人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."JCRC" IS '检查人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."JYRC" IS '检验人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."RYRC" IS '入院人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."QNJSCYRC" IS '出院人次';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."GCSRGBLS" IS '观察室入观病例数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYRS" IS '在院人数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYCWS" IS '实有床位数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."SJZYCWS" IS '实际占用床位数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."KCW" IS '空床数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."SSJCZLS" IS '手术及操作例数';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."MJZYLFY" IS '门急诊医疗费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYYLFY" IS '住院医疗费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."MJZYPFY" IS '门急诊药品费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYYPFY" IS '住院药品费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."MJZYBYLFY" IS '门急诊医保医疗费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYYBYLFY" IS '住院医保医疗费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."MJZYBYPFY" IS '门急诊医保药品费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYYBYPFY" IS '住院医保药品费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."ZYSJFSFY" IS '住院实际发生费用';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."CYHZYLSR" IS '出院患者医疗收入';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."CYHZYPSR" IS '出院患者药品收入';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."CYHZYBYLSR" IS '出院患者医保医疗收入';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."CYHZYBYPSR" IS '出院患者医保药品收入';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_STAT_YWL_Report"."YLYL2" IS '预留二';
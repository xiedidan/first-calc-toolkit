DROP TABLE IF EXISTS "TB_EMR_SXJL";
CREATE TABLE "TB_EMR_SXJL" (
    "YLJGDM" varchar(33),
    "SXJLLSH" varchar(96),
    "BRZSY" varchar(96),
    "MZZYBZ" varchar(2),
    "JZLSH" varchar(75),
    "ZYH" varchar(27),
    "MJZH" varchar(27),
    "DZSQDBH" varchar(150),
    "KSMC" varchar(75),
    "KSDM" varchar(45),
    "NYS" numeric,
    "NLY" varchar(12),
    "NLXS" varchar(48),
    "BQMC" varchar(75),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "ABOXXDM" varchar(2),
    "RHXXDM" varchar(2),
    "SXSBSDM" varchar(2),
    "SXXZDM" varchar(2),
    "JBZDBM" varchar(96),
    "JBZDMC" varchar(768),
    "SQABOXXDM" varchar(2),
    "SQPHXXDM" varchar(2),
    "SXABOXXDM" varchar(2),
    "SXRHXXDM" varchar(2),
    "SXZZ" varchar(750),
    "SXGCJL" varchar(3000),
    "SXPZDM" varchar(15),
    "SXPZMC" varchar(192),
    "XDBM" varchar(150),
    "SXL" varchar(15),
    "SXLJLDW" varchar(15),
    "SXFYBZ" varchar(2),
    "SXFYLXDM" varchar(2),
    "SXCS" numeric,
    "SXKSRQSJ" timestamp,
    "SXJSRQSJ" timestamp,
    "SXYY" varchar(150),
    "ZYYSXM" varchar(108),
    "ZYYSBM" varchar(27),
    "QMRQSJ" timestamp,
    "JLRQSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_EMR_SXJL" IS '输血记录';
COMMENT ON COLUMN "TB_EMR_SXJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXJLLSH" IS '输血记录流水号';
COMMENT ON COLUMN "TB_EMR_SXJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_EMR_SXJL"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_EMR_SXJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_EMR_SXJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_EMR_SXJL"."MJZH" IS '门（急）诊号';
COMMENT ON COLUMN "TB_EMR_SXJL"."DZSQDBH" IS '电子申请单编号';
COMMENT ON COLUMN "TB_EMR_SXJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_EMR_SXJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."NYS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_EMR_SXJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_EMR_SXJL"."NLXS" IS '年龄（小时）';
COMMENT ON COLUMN "TB_EMR_SXJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_EMR_SXJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_EMR_SXJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_EMR_SXJL"."ABOXXDM" IS 'ABO 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."RHXXDM" IS 'Rh 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXSBSDM" IS '输血史标识代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXXZDM" IS '输血性质代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."JBZDBM" IS '疾病诊断编码';
COMMENT ON COLUMN "TB_EMR_SXJL"."JBZDMC" IS '疾病诊断名称';
COMMENT ON COLUMN "TB_EMR_SXJL"."SQABOXXDM" IS '申请 ABO 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SQPHXXDM" IS '申请 Rh 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXABOXXDM" IS '输血 ABO 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXRHXXDM" IS '输血 Rh 血型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXZZ" IS '输血指征';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXGCJL" IS '输血过程记录';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXPZDM" IS '输血品种代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXPZMC" IS '输血品种名称';
COMMENT ON COLUMN "TB_EMR_SXJL"."XDBM" IS '血袋编码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXL" IS '输血量';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXLJLDW" IS '输血量计量单位';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXFYBZ" IS '输血反应标志';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXFYLXDM" IS '输血反应类型代码';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXCS" IS '输血次数';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXKSRQSJ" IS '输血开始日期时间';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXJSRQSJ" IS '输血结束日期时间';
COMMENT ON COLUMN "TB_EMR_SXJL"."SXYY" IS '输血原因';
COMMENT ON COLUMN "TB_EMR_SXJL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_EMR_SXJL"."ZYYSBM" IS '住院医师编号';
COMMENT ON COLUMN "TB_EMR_SXJL"."QMRQSJ" IS '签名日期时间';
COMMENT ON COLUMN "TB_EMR_SXJL"."JLRQSJ" IS '记录日期时间';
COMMENT ON COLUMN "TB_EMR_SXJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_EMR_SXJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_EMR_SXJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_EMR_SXJL"."YLYL2" IS '预留二';
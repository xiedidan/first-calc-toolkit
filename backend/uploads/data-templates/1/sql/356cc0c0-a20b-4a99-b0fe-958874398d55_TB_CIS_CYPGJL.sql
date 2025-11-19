DROP TABLE IF EXISTS "TB_CIS_CYPGJL";
CREATE TABLE "TB_CIS_CYPGJL" (
    "YLJGDM" varchar(33),
    "CYPGJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "ZYH" varchar(27),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "CYZDBM" varchar(750),
    "CYZDMC" varchar(1500),
    "CYRQSJ" timestamp,
    "YSQKDM" varchar(2),
    "ZLNLDM" varchar(2),
    "CYQK" varchar(3000),
    "LYFSDM" varchar(2),
    "YYZD" varchar(150),
    "YSZDDM" varchar(3),
    "SHFSZD" varchar(75),
    "XJNR" varchar(750),
    "FZZD" varchar(750),
    "HSXM" varchar(108),
    "HSGH" varchar(54),
    "HSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_CYPGJL" IS '出院评估记录';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."CYPGJLLSH" IS '出院评估记录流水号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."CYZDBM" IS '出院诊断编码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."CYZDMC" IS '出院诊断名称';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."CYRQSJ" IS '出院日期时间';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YSQKDM" IS '饮食情况代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."ZLNLDM" IS '自理能力代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."CYQK" IS '出院情况';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."LYFSDM" IS '离院方式代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YYZD" IS '用药指导';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YSZDDM" IS '饮食指导代码';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."SHFSZD" IS '生活方式指导';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."XJNR" IS '宣教内容';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."FZZD" IS '复诊指导';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."HSXM" IS '护士姓名';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."HSGH" IS '护士编号';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."HSQMRQSJ" IS '护士签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_CYPGJL"."YLYL2" IS '预留二';
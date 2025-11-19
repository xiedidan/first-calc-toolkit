DROP TABLE IF EXISTS "TB_CIS_CRLJL";
CREATE TABLE "TB_CIS_CRLJL" (
    "YLJGDM" varchar(33),
    "CRLJLLSH" varchar(96),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "JZLSH" varchar(96),
    "MZZYBZ" varchar(2),
    "MZZYH" varchar(27),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "TZ" numeric(6,2),
    "JBZDBM" varchar(750),
    "JBZDMC" varchar(1500),
    "HLDJDM" varchar(2),
    "HLLXDM" varchar(2),
    "HLGCXMMC" varchar(300),
    "HLGCJG" varchar(1500),
    "HLCZMC" varchar(150),
    "HLCZXMLMMC" varchar(150),
    "HLCZJG" varchar(1500),
    "OTBZ" varchar(2),
    "PNKNBZ" varchar(2),
    "ZYSYLBDM" varchar(2),
    "HSXM" varchar(108),
    "HSGH" varchar(54),
    "QMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_CRLJL" IS '出入量记录';
COMMENT ON COLUMN "TB_CIS_CRLJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."CRLJLLSH" IS '出入量记录流水号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_CRLJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_CRLJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_CRLJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_CRLJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_CIS_CRLJL"."MZZYH" IS '门诊/住院号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."TZ" IS '体重(kg)';
COMMENT ON COLUMN "TB_CIS_CRLJL"."JBZDBM" IS '疾病诊断编码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."JBZDMC" IS '疾病诊断名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLDJDM" IS '护理等级代码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLLXDM" IS '护理类型代码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLGCXMMC" IS '护理观察项目名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLGCJG" IS '护理观察结果';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLCZMC" IS '护理操作名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLCZXMLMMC" IS '护理操作项目类目名称';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HLCZJG" IS '护理操作结果';
COMMENT ON COLUMN "TB_CIS_CRLJL"."OTBZ" IS '呕吐标志';
COMMENT ON COLUMN "TB_CIS_CRLJL"."PNKNBZ" IS '排尿困难标志';
COMMENT ON COLUMN "TB_CIS_CRLJL"."ZYSYLBDM" IS '中药使用类别代码';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HSXM" IS '护士姓名';
COMMENT ON COLUMN "TB_CIS_CRLJL"."HSGH" IS '护士编号';
COMMENT ON COLUMN "TB_CIS_CRLJL"."QMRQSJ" IS '签名日期时间';
COMMENT ON COLUMN "TB_CIS_CRLJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_CRLJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_CRLJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_CRLJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_CRLJL"."YLYL2" IS '预留二';
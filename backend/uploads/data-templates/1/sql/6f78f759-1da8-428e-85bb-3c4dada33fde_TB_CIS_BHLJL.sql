DROP TABLE IF EXISTS "TB_CIS_BHLJL";
CREATE TABLE "TB_CIS_BHLJL" (
    "YLJGDM" varchar(33),
    "YBHLJLLSH" varchar(96),
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
    "JBZDBM" varchar(750),
    "JBZDMC" varchar(1500),
    "GMS" varchar(1500),
    "TW" numeric,
    "SSY" numeric,
    "SZY" numeric,
    "TZ" numeric,
    "HXP" numeric,
    "ML" numeric,
    "XYBHD" numeric,
    "ZBDMBDZ" varchar(2),
    "YSQKDM" varchar(2),
    "YSZDDM" varchar(3),
    "JYBQ" varchar(3000),
    "FCSSAQH" varchar(2),
    "SHSSAQH" varchar(2),
    "FCSSFXP" varchar(2),
    "SHSSFXP" varchar(2),
    "GLBZ" varchar(2),
    "GLZLDM" varchar(2),
    "HSXM" varchar(108),
    "HSGH" varchar(54),
    "QMRQSJ" timestamp,
    "HLDJDM" varchar(2),
    "HLLXDM" varchar(2),
    "DGHLMS" varchar(1500),
    "QGHLDM" varchar(2),
    "TWHL" varchar(45),
    "PFHL" varchar(75),
    "YYHL" varchar(150),
    "XLHLDM" varchar(2),
    "AQHLDM" varchar(2),
    "HLGCXMMC" varchar(300),
    "HLGCJG" varchar(1500),
    "HLCZMC" varchar(150),
    "HLCZXMMMC" varchar(150),
    "HLCZJG" varchar(1500),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_BHLJL" IS '一般护理记录';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YBHLJLLSH" IS '一般护理记录流水号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_BHLJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_BHLJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_BHLJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_BHLJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."MZZYH" IS '门诊/住院号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."JBZDBM" IS '疾病诊断编码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."JBZDMC" IS '疾病诊断名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."GMS" IS '过敏史';
COMMENT ON COLUMN "TB_CIS_BHLJL"."TW" IS '体温(℃)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."SSY" IS '收缩压（mmHg)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."SZY" IS '舒张压(mmHg)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."TZ" IS '体重（kg)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HXP" IS '呼吸频率(次/min)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."ML" IS '脉率(次/min)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."XYBHD" IS '血氧饱和度（％)';
COMMENT ON COLUMN "TB_CIS_BHLJL"."ZBDMBDZ" IS '足背动脉搏动标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YSQKDM" IS '饮食情况代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YSZDDM" IS '饮食指导代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."JYBQ" IS '简要病情';
COMMENT ON COLUMN "TB_CIS_BHLJL"."FCSSAQH" IS '发出手术安全核对表标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."SHSSAQH" IS '收回手术安全核对表标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."FCSSFXP" IS '发出手术风险评估表标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."SHSSFXP" IS '收回手术风险评估表标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."GLBZ" IS '隔离标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."GLZLDM" IS '隔离种类代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HSXM" IS '护士姓名';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HSGH" IS '护士编号';
COMMENT ON COLUMN "TB_CIS_BHLJL"."QMRQSJ" IS '签名日期时间';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLDJDM" IS '护理等级代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLLXDM" IS '护理类型代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."DGHLMS" IS '导管护理描述';
COMMENT ON COLUMN "TB_CIS_BHLJL"."QGHLDM" IS '气管护理代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."TWHL" IS '体位护理';
COMMENT ON COLUMN "TB_CIS_BHLJL"."PFHL" IS '皮肤护理';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YYHL" IS '营养护理';
COMMENT ON COLUMN "TB_CIS_BHLJL"."XLHLDM" IS '心理护理代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."AQHLDM" IS '安全护理代码';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLGCXMMC" IS '护理观察项目名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLGCJG" IS '护理观察结果';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLCZMC" IS '护理操作名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLCZXMMMC" IS '护理操作项目类目名称';
COMMENT ON COLUMN "TB_CIS_BHLJL"."HLCZJG" IS '护理操作结果';
COMMENT ON COLUMN "TB_CIS_BHLJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_BHLJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_BHLJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_BHLJL"."YLYL2" IS '预留二';
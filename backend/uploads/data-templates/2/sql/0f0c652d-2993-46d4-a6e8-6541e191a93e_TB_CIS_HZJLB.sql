DROP TABLE IF EXISTS "TB_CIS_HZJLB";
CREATE TABLE "TB_CIS_HZJLB" (
    "YLJGDM" varchar(33),
    "HZJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "MZZYBZ" varchar(2),
    "MZZYH" varchar(27),
    "HZLX" varchar(48),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "HZDAH" varchar(96),
    "XM" varchar(108),
    "DZSQD" varchar(108),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "BLZY" varchar(3000),
    "FZJCJG" varchar(6000),
    "ZYSZGCJG" varchar(1500),
    "ZZZF" varchar(150),
    "XYZDBM" varchar(750),
    "XYZDMC" varchar(1500),
    "ZYBMDM" varchar(750),
    "ZYBMMC" varchar(1500),
    "ZYZHDM" varchar(750),
    "ZYZHMC" varchar(1500),
    "ZLGCMC" varchar(1500),
    "ZLGCMS" varchar(3000),
    "HZYY" varchar(1500),
    "HZMD" varchar(75),
    "HZSQYSXM" varchar(108),
    "HZSQYSGH" varchar(54),
    "HZSQKS" varchar(108),
    "HZSQKSDM" varchar(54),
    "HZSQYLJGMC" varchar(108),
    "HZJG" varchar(6000),
    "JLRQSJ" timestamp,
    "JLRGH" varchar(54),
    "JLRXM" varchar(108),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_HZJLB" IS '会诊记录表';
COMMENT ON COLUMN "TB_CIS_HZJLB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZJLLSH" IS '会诊记录流水号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_CIS_HZJLB"."MZZYH" IS '门诊/住院号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZLX" IS '会诊类型';
COMMENT ON COLUMN "TB_CIS_HZJLB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_HZJLB"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_HZJLB"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_HZJLB"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZDAH" IS '患者档案号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."XM" IS '患者姓名';
COMMENT ON COLUMN "TB_CIS_HZJLB"."DZSQD" IS '电子申请单';
COMMENT ON COLUMN "TB_CIS_HZJLB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."BLZY" IS '病历摘要';
COMMENT ON COLUMN "TB_CIS_HZJLB"."FZJCJG" IS '辅助检查结果';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZYSZGCJG" IS '中医"四诊"观察结果';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_HZJLB"."XYZDBM" IS '西医诊断编码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."XYZDMC" IS '西医诊断名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZYBMDM" IS '中医病名代码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZYBMMC" IS '中医病名名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZYZHDM" IS '中医证候代码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZYZHMC" IS '中医证候名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZLGCMC" IS '诊疗过程名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZYY" IS '会诊原因';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZMD" IS '会诊目的';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZSQYSXM" IS '会诊申请医师姓名';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZSQYSGH" IS '会诊申请医师编号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZSQKS" IS '会诊申请科室';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZSQKSDM" IS '会诊申请科室代码';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZSQYLJGMC" IS '会诊申请医疗机构名称';
COMMENT ON COLUMN "TB_CIS_HZJLB"."HZJG" IS '会诊(意见)结果';
COMMENT ON COLUMN "TB_CIS_HZJLB"."JLRQSJ" IS '记录日期时间';
COMMENT ON COLUMN "TB_CIS_HZJLB"."JLRGH" IS '记录人工号';
COMMENT ON COLUMN "TB_CIS_HZJLB"."JLRXM" IS '记录人姓名';
COMMENT ON COLUMN "TB_CIS_HZJLB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_HZJLB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_HZJLB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_HZJLB"."YLYL2" IS '预留二';
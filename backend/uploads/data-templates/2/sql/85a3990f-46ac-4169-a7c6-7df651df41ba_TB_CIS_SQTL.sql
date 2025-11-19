DROP TABLE IF EXISTS "TB_CIS_SQTL";
CREATE TABLE "TB_CIS_SQTL" (
    "YLJGDM" varchar(33),
    "SQTLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "TLRQSJ" timestamp,
    "TLDD" varchar(750),
    "ZCRXM" varchar(108),
    "ZCRGH" varchar(54),
    "ZCRZYJSZWD" varchar(2),
    "ZCRZYJSZWM" varchar(15),
    "CJTLRYGHLB" varchar(300),
    "CJTLRYXMLB" varchar(300),
    "CJTLZYJSZWLBDM" varchar(30),
    "CJTLRYZYJSZWMC" varchar(192),
    "RYRQSJ" timestamp,
    "SQZDBM" varchar(750),
    "SQZDMC" varchar(1500),
    "DZSQDBH" varchar(150),
    "NSSSSJCZMC" varchar(120),
    "NSSSSJCZBM" varchar(75),
    "NSSSSMBBWMC" varchar(75),
    "NSSSSJCZRQSJ" timestamp,
    "NSSMZFFDM" varchar(30),
    "SSYD" varchar(768),
    "SQZB" varchar(1500),
    "SSZZ" varchar(750),
    "SSFA" varchar(1500),
    "ZYSX" varchar(1500),
    "TLYJ" varchar(6000),
    "TLJL" varchar(6000),
    "SSZXM" varchar(108),
    "SSZGH" varchar(54),
    "MZYSXM" varchar(108),
    "MZYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZYYSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_SQTL" IS '术前讨论';
COMMENT ON COLUMN "TB_CIS_SQTL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_SQTL"."SQTLLSH" IS '术前讨论流水号';
COMMENT ON COLUMN "TB_CIS_SQTL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_SQTL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_SQTL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_SQTL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_SQTL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_SQTL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_SQTL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_SQTL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_SQTL"."TLRQSJ" IS '讨论日期时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."TLDD" IS '讨论地点';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZCRXM" IS '主持人姓名';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZCRGH" IS '主持人工号';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZCRZYJSZWD" IS '主持人专业技术职务代码';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZCRZYJSZWM" IS '主持人专业技术职务名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."CJTLRYGHLB" IS '参加讨论人员工号列表';
COMMENT ON COLUMN "TB_CIS_SQTL"."CJTLRYXMLB" IS '参加讨论人员姓名列表';
COMMENT ON COLUMN "TB_CIS_SQTL"."CJTLZYJSZWLBDM" IS '参加讨论专业技术职务类别代码';
COMMENT ON COLUMN "TB_CIS_SQTL"."CJTLRYZYJSZWMC" IS '参加讨论人员专业技术职务名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."SQZDBM" IS '术前诊断编码';
COMMENT ON COLUMN "TB_CIS_SQTL"."SQZDMC" IS '术前诊断名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."DZSQDBH" IS '电子申请单编号';
COMMENT ON COLUMN "TB_CIS_SQTL"."NSSSSJCZMC" IS '拟实施手术及操作名称';
COMMENT ON COLUMN "TB_CIS_SQTL"."NSSSSJCZBM" IS '拟实施手术及操';
COMMENT ON COLUMN "TB_CIS_SQTL"."NSSSSMBBWMC" IS '拟实施手术目标';
COMMENT ON COLUMN "TB_CIS_SQTL"."NSSSSJCZRQSJ" IS '拟实施手术及操作日期时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."NSSMZFFDM" IS '拟实施麻醉方法代码';
COMMENT ON COLUMN "TB_CIS_SQTL"."SSYD" IS '手术要点';
COMMENT ON COLUMN "TB_CIS_SQTL"."SQZB" IS '术前准备';
COMMENT ON COLUMN "TB_CIS_SQTL"."SSZZ" IS '手术指征';
COMMENT ON COLUMN "TB_CIS_SQTL"."SSFA" IS '手术方案';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZYSX" IS '注意事项';
COMMENT ON COLUMN "TB_CIS_SQTL"."TLYJ" IS '讨论意见';
COMMENT ON COLUMN "TB_CIS_SQTL"."TLJL" IS '讨论结论';
COMMENT ON COLUMN "TB_CIS_SQTL"."SSZXM" IS '手术者姓名';
COMMENT ON COLUMN "TB_CIS_SQTL"."SSZGH" IS '手术者编号';
COMMENT ON COLUMN "TB_CIS_SQTL"."MZYSXM" IS '麻醉医师姓名';
COMMENT ON COLUMN "TB_CIS_SQTL"."MZYSGH" IS '麻醉医师编号';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_SQTL"."ZYYSQMRQSJ" IS '住院医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_SQTL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_SQTL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_SQTL"."YLYL2" IS '预留二';
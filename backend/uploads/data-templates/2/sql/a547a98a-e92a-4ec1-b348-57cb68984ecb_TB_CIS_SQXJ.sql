DROP TABLE IF EXISTS "TB_CIS_SQXJ";
CREATE TABLE "TB_CIS_SQXJ" (
    "YLJGDM" varchar(33),
    "SQXJLSH" varchar(96),
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
    "XJRQSJ" timestamp,
    "BLZY" varchar(6000),
    "SQZDBM" varchar(750),
    "SQZDMC" varchar(1500),
    "ZDYJ" varchar(1920),
    "GMSBZ" varchar(2),
    "GMS" varchar(1500),
    "FZJCJG" varchar(6000),
    "SSSYZ" varchar(750),
    "SSJJZ" varchar(750),
    "SSZZ" varchar(750),
    "HZYJ" varchar(6000),
    "NSSSSJCZBM" varchar(75),
    "NSSSSJCZMC" varchar(120),
    "NSSSSMBBWM" varchar(75),
    "NSSSSJCZRQ" timestamp,
    "NSSMZFFDM" varchar(30),
    "NSSMZFFMC" varchar(150),
    "ZYSX" varchar(1500),
    "SSYD" varchar(768),
    "SQZB" varchar(1500),
    "SSZXM" varchar(108),
    "SSZGH" varchar(54),
    "ZZYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZYYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZYYSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_SQXJ" IS '术前小结';
COMMENT ON COLUMN "TB_CIS_SQXJ"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SQXJLSH" IS '术前小结流水号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_SQXJ"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."XJRQSJ" IS '小结日期时间';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BLZY" IS '病历摘要';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SQZDBM" IS '术前诊断编码';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SQZDMC" IS '术前诊断名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZDYJ" IS '诊断依据';
COMMENT ON COLUMN "TB_CIS_SQXJ"."GMSBZ" IS '过敏史标志';
COMMENT ON COLUMN "TB_CIS_SQXJ"."GMS" IS '过敏史';
COMMENT ON COLUMN "TB_CIS_SQXJ"."FZJCJG" IS '辅助检查结果';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSSYZ" IS '手术适应证';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSJJZ" IS '手术禁忌症';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSZZ" IS '手术指征';
COMMENT ON COLUMN "TB_CIS_SQXJ"."HZYJ" IS '会诊意见';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSSSJCZBM" IS '拟实施手术及操作编码';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSSSJCZMC" IS '拟实施手术及操作名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSSSMBBWM" IS '拟实施手术目标部位名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSSSJCZRQ" IS '拟实施手术及操作日期时间';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSMZFFDM" IS '拟实施麻醉方法代码';
COMMENT ON COLUMN "TB_CIS_SQXJ"."NSSMZFFMC" IS '拟实施麻醉方法名称';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZYSX" IS '注意事项';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSYD" IS '手术要点';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SQZB" IS '术前准备';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSZXM" IS '手术者姓名';
COMMENT ON COLUMN "TB_CIS_SQXJ"."SSZGH" IS '手术者编号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_SQXJ"."ZYYSQMRQSJ" IS '住院医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_SQXJ"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_SQXJ"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_SQXJ"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_SQXJ"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_SQXJ"."YLYL2" IS '预留二';
DROP TABLE IF EXISTS "TB_CIS_JDXJ";
CREATE TABLE "TB_CIS_JDXJ" (
    "YLJGDM" varchar(33),
    "JDXJLSH" varchar(96),
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
    "RYRQSJ" timestamp,
    "XJRQSJ" timestamp,
    "ZS" varchar(3000),
    "RYQK" varchar(6000),
    "YZNR" varchar(1500),
    "ZLGCMS" varchar(6000),
    "MQQK" varchar(6000),
    "JHZLFA" varchar(1500),
    "ZZYSXM" varchar(108),
    "ZZYSGH" varchar(54),
    "ZZQMRQSJ" timestamp,
    "RYZD_XYZDBM" varchar(750),
    "RYZD_XYZDMC" varchar(1500),
    "RYZD_ZYBMDM" varchar(750),
    "RYZD_ZYBMMC" varchar(1500),
    "RYZD_ZYZHDM" varchar(750),
    "RYZD_ZYZHMC" varchar(1500),
    "MQZD_XYZDBM" varchar(750),
    "MQZD_XYZDMC" varchar(1500),
    "MQZD_ZYBMDM" varchar(750),
    "MQZD_ZYBMMC" varchar(1500),
    "MQZD_ZYZHDM" varchar(750),
    "MQZD_ZYZHMC" varchar(1500),
    "ZYSZGCJG" varchar(1500),
    "ZZZF" varchar(150),
    "ZYJZFF" varchar(150),
    "ZYYYFF" varchar(150),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_JDXJ" IS '阶段小结';
COMMENT ON COLUMN "TB_CIS_JDXJ"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."JDXJLSH" IS '阶段小结流水号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_JDXJ"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_JDXJ"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_JDXJ"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_JDXJ"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_JDXJ"."XJRQSJ" IS '小结日期时间';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_JDXJ"."YZNR" IS '医嘱内容';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQQK" IS '目前情况';
COMMENT ON COLUMN "TB_CIS_JDXJ"."JHZLFA" IS '今后治疗方案';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZZQMRQSJ" IS '主治签名日期时间';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_XYZDBM" IS '入院诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_XYZDMC" IS '入院诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_ZYBMDM" IS '入院诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_ZYBMMC" IS '入院诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_ZYZHDM" IS '入院诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."RYZD_ZYZHMC" IS '入院诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_XYZDBM" IS '目前诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_XYZDMC" IS '目前诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_ZYBMDM" IS '目前诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_ZYBMMC" IS '目前诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_ZYZHDM" IS '目前诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_JDXJ"."MQZD_ZYZHMC" IS '目前诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZYSZGCJG" IS '中医"四诊"观察结果';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZYJZFF" IS '中药煎煮方法';
COMMENT ON COLUMN "TB_CIS_JDXJ"."ZYYYFF" IS '中药用药方法';
COMMENT ON COLUMN "TB_CIS_JDXJ"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_JDXJ"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_JDXJ"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_JDXJ"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_JDXJ"."YLYL2" IS '预留二';
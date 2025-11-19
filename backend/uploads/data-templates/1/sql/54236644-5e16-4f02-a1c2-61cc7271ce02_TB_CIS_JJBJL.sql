DROP TABLE IF EXISTS "TB_CIS_JJBJL";
CREATE TABLE "TB_CIS_JJBJL" (
    "YLJGDM" varchar(33),
    "JJBJLLSH" varchar(96),
    "JJBJLLX" numeric,
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "JZLSH" varchar(108),
    "ZYH" varchar(27),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "RYRQSJ" timestamp,
    "ZS" varchar(3000),
    "RYQK" varchar(6000),
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
    "ZLGCMS" varchar(6000),
    "MQQK" varchar(6000),
    "ZYSX" varchar(1500),
    "JBZLJH" varchar(6000),
    "JBRQSJ" timestamp,
    "JBZXM" varchar(108),
    "JBZGH" varchar(54),
    "JIEBRQSJ" timestamp,
    "JIEBZXM" varchar(108),
    "JIEBZGH" varchar(54),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_JJBJL" IS '交接班记录';
COMMENT ON COLUMN "TB_CIS_JJBJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JJBJLLSH" IS '交接班记录流水号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JJBJLLX" IS '交接班记录类型';
COMMENT ON COLUMN "TB_CIS_JJBJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_JJBJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_JJBJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_JJBJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_XYZDBM" IS '入院诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_XYZDMC" IS '入院诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_ZYBMDM" IS '入院诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_ZYBMMC" IS '入院诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_ZYZHDM" IS '入院诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."RYZD_ZYZHMC" IS '入院诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_XYZDBM" IS '目前诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_XYZDMC" IS '目前诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_ZYBMDM" IS '目前诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_ZYBMMC" IS '目前诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_ZYZHDM" IS '目前诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQZD_ZYZHMC" IS '目前诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZYSZGCJG" IS '中医"四诊"观察结果';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_JJBJL"."MQQK" IS '目前情况';
COMMENT ON COLUMN "TB_CIS_JJBJL"."ZYSX" IS '注意事项';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JBZLJH" IS '接班诊疗计划';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JBRQSJ" IS '交班日期时间';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JBZXM" IS '交班者姓名';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JBZGH" IS '交班者编号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JIEBRQSJ" IS '接班日期时间';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JIEBZXM" IS '接班者姓名';
COMMENT ON COLUMN "TB_CIS_JJBJL"."JIEBZGH" IS '接班者编号';
COMMENT ON COLUMN "TB_CIS_JJBJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_JJBJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_JJBJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_JJBJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_JJBJL"."YLYL2" IS '预留二';
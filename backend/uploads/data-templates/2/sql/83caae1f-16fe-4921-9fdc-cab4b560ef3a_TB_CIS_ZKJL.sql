DROP TABLE IF EXISTS "TB_CIS_ZKJL";
CREATE TABLE "TB_CIS_ZKJL" (
    "YLJGDM" varchar(33),
    "ZKJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BQDM" varchar(54),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "ZYYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "RYRQSJ" timestamp,
    "ZS" varchar(3000),
    "RYQK" varchar(3000),
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
    "ZYCFYZNR" varchar(1500),
    "ZLGCMS" varchar(6000),
    "MQQK" varchar(6000),
    "ZKMD" varchar(768),
    "ZRZLJH" varchar(6000),
    "ZYSX" varchar(1500),
    "ZKJLLX" varchar(2),
    "ZCRQSJ" timestamp,
    "ZCKSMC" varchar(108),
    "ZCKSDM" varchar(54),
    "ZCYSXM" varchar(108),
    "ZCYSGH" varchar(54),
    "ZRRQSJ" timestamp,
    "ZRKSMC" varchar(108),
    "ZRKSDM" varchar(54),
    "ZRYSXM" varchar(108),
    "ZRYSGH" varchar(54),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_ZKJL" IS '转科记录';
COMMENT ON COLUMN "TB_CIS_ZKJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZKJLLSH" IS '转科记录流水号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_ZKJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_ZKJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_ZKJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_ZKJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BQDM" IS '病区代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_XYZDBM" IS '入院诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_XYZDMC" IS '入院诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_ZYBMDM" IS '入院诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_ZYBMMC" IS '入院诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_ZYZHDM" IS '入院诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."RYZD_ZYZHMC" IS '入院诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_XYZDBM" IS '目前诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_XYZDMC" IS '目前诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_ZYBMDM" IS '目前诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_ZYBMMC" IS '目前诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_ZYZHDM" IS '目前诊断-中医证候';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQZD_ZYZHMC" IS '目前诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYSZGCJG" IS '中医"四诊"观察结果';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYJZFF" IS '中药煎煮方法';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYYYFF" IS '中药用药方法';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYCFYZNR" IS '中药处方医嘱内容';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_ZKJL"."MQQK" IS '目前情况';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZKMD" IS '转科目的';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRZLJH" IS '转入诊疗计划';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZYSX" IS '注意事项';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZKJLLX" IS '转科记录类型';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZCRQSJ" IS '转出日期时间';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZCKSMC" IS '转出科室名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZCKSDM" IS '转出科室代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZCYSXM" IS '转出医师姓名';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZCYSGH" IS '转出医师编号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRRQSJ" IS '转入日期时间';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRKSMC" IS '转入科室名称';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRKSDM" IS '转入科室代码';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRYSXM" IS '转入医师姓名';
COMMENT ON COLUMN "TB_CIS_ZKJL"."ZRYSGH" IS '转入医师编号';
COMMENT ON COLUMN "TB_CIS_ZKJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_ZKJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_ZKJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_ZKJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_ZKJL"."YLYL2" IS '预留二';
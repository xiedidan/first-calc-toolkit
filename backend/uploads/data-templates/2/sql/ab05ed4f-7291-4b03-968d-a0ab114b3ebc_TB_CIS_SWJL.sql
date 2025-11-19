DROP TABLE IF EXISTS "TB_CIS_SWJL";
CREATE TABLE "TB_CIS_SWJL" (
    "YLJGDM" varchar(33),
    "ZYSWJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "KSDM" varchar(54),
    "KSMC" varchar(108),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "SJZYTS" numeric,
    "RYRQSJ" timestamp,
    "RYZDBM" varchar(750),
    "RYZDMC" varchar(1500),
    "RYQK" varchar(3000),
    "ZLGCMS" varchar(3000),
    "SWRQSJ" timestamp,
    "ZJSWYYBM" varchar(96),
    "ZJSWYYMC" varchar(768),
    "SWZDBM" varchar(750),
    "SWZDMC" varchar(1500),
    "JSSFTYSTJPBZ" varchar(2),
    "ZYYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZZYSGH" varchar(54),
    "ZRYSXM" varchar(108),
    "ZRYSGH" varchar(54),
    "ZYYSQMRQSJ" timestamp,
    "ZZYSQMRQSJ" timestamp,
    "ZRYSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_SWJL" IS '死亡记录';
COMMENT ON COLUMN "TB_CIS_SWJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZYSWJLLSH" IS '住院死亡记录流水号';
COMMENT ON COLUMN "TB_CIS_SWJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_SWJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_SWJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_SWJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_SWJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_SWJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_SWJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_SWJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_SWJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_SWJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_SWJL"."SJZYTS" IS '实际住院天数';
COMMENT ON COLUMN "TB_CIS_SWJL"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."RYZDBM" IS '入院诊断编码';
COMMENT ON COLUMN "TB_CIS_SWJL"."RYZDMC" IS '入院诊断名称';
COMMENT ON COLUMN "TB_CIS_SWJL"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_SWJL"."SWRQSJ" IS '死亡日期时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZJSWYYBM" IS '直接死亡原因编码';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZJSWYYMC" IS '直接死亡原因名称';
COMMENT ON COLUMN "TB_CIS_SWJL"."SWZDBM" IS '死亡诊断编码';
COMMENT ON COLUMN "TB_CIS_SWJL"."SWZDMC" IS '死亡诊断名称';
COMMENT ON COLUMN "TB_CIS_SWJL"."JSSFTYSTJPBZ" IS '家属是否同意尸体解剖标志';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZRYSXM" IS '主任医师姓名';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZRYSGH" IS '主任医师编号';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZYYSQMRQSJ" IS '住院医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZZYSQMRQSJ" IS '主治医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."ZRYSQMRQSJ" IS '主任医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_SWJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_SWJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_SWJL"."YLYL2" IS '预留二';
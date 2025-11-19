DROP TABLE IF EXISTS "TB_BA_ICU";
CREATE TABLE "TB_BA_ICU" (
    "YLJGDM" varchar(33),
    "ZZJHJLLSH" varchar(75),
    "BRZSY" varchar(96),
    "BAH" varchar(27),
    "JZLSH" varchar(75),
    "ZYH" varchar(27),
    "ZYCS" numeric,
    "JHSJRRQSJ" timestamp,
    "JHSTCRQSJ" timestamp,
    "ZZJHSDM" varchar(24),
    "ZZJHSLBDM" varchar(3),
    "ZZJHYY" varchar(3000),
    "HLDJDM" varchar(2),
    "HLDJMC" varchar(30),
    "HLTS" numeric,
    "SFCFZZJHS" varchar(2),
    "JLRQSJ" timestamp,
    "JLRGH" varchar(27),
    "JLRXM" varchar(75),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_ICU" IS '住院病案首页重症监护信息';
COMMENT ON COLUMN "TB_BA_ICU"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_ICU"."ZZJHJLLSH" IS '重症监护记录流水号';
COMMENT ON COLUMN "TB_BA_ICU"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_ICU"."BAH" IS '病案号';
COMMENT ON COLUMN "TB_BA_ICU"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_ICU"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_BA_ICU"."ZYCS" IS '住院次数';
COMMENT ON COLUMN "TB_BA_ICU"."JHSJRRQSJ" IS '监护室进入日期时间';
COMMENT ON COLUMN "TB_BA_ICU"."JHSTCRQSJ" IS '监护室退出日期时间';
COMMENT ON COLUMN "TB_BA_ICU"."ZZJHSDM" IS '重症监护室代码';
COMMENT ON COLUMN "TB_BA_ICU"."ZZJHSLBDM" IS '重症监护室类别代码';
COMMENT ON COLUMN "TB_BA_ICU"."ZZJHYY" IS '重症监护原因';
COMMENT ON COLUMN "TB_BA_ICU"."HLDJDM" IS '护理等级代码';
COMMENT ON COLUMN "TB_BA_ICU"."HLDJMC" IS '护理等级名称';
COMMENT ON COLUMN "TB_BA_ICU"."HLTS" IS '护理天数';
COMMENT ON COLUMN "TB_BA_ICU"."SFCFZZJHS" IS '是否重返重症监护室';
COMMENT ON COLUMN "TB_BA_ICU"."JLRQSJ" IS '记录日期时间';
COMMENT ON COLUMN "TB_BA_ICU"."JLRGH" IS '记录人工号';
COMMENT ON COLUMN "TB_BA_ICU"."JLRXM" IS '记录人姓名';
COMMENT ON COLUMN "TB_BA_ICU"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_ICU"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_ICU"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_ICU"."YLYL2" IS '预留二';
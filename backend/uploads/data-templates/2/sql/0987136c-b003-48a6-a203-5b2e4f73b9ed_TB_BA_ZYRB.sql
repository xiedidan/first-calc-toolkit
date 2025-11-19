DROP TABLE IF EXISTS "TB_BA_ZYRB";
CREATE TABLE "TB_BA_ZYRB" (
    "YLJGDM" varchar(33),
    "ZYRBLSH" varchar(33),
    "SJRQ" timestamp,
    "KSBM" varchar(54),
    "KSMC" varchar(108),
    "KFCWS" numeric,
    "BRKCS" numeric,
    "JTBCS" numeric,
    "GGBCS" numeric,
    "YRS" numeric,
    "RYS" numeric,
    "ZRS" numeric,
    "CYS" numeric,
    "QZSWS" numeric,
    "ZCS" numeric,
    "XRS" numeric,
    "WZRC" numeric,
    "PBRC" numeric,
    "YLSGS" numeric,
    "CMI" numeric,
    "BZ" varchar(384),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_ZYRB" IS '住院日报数据';
COMMENT ON COLUMN "TB_BA_ZYRB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_ZYRB"."ZYRBLSH" IS '住院日报流水号';
COMMENT ON COLUMN "TB_BA_ZYRB"."SJRQ" IS '数据日期';
COMMENT ON COLUMN "TB_BA_ZYRB"."KSBM" IS '科室编码';
COMMENT ON COLUMN "TB_BA_ZYRB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_BA_ZYRB"."KFCWS" IS '开放床位数';
COMMENT ON COLUMN "TB_BA_ZYRB"."BRKCS" IS '本日空床数';
COMMENT ON COLUMN "TB_BA_ZYRB"."JTBCS" IS '家庭病床数';
COMMENT ON COLUMN "TB_BA_ZYRB"."GGBCS" IS '公共病床数';
COMMENT ON COLUMN "TB_BA_ZYRB"."YRS" IS '原人数';
COMMENT ON COLUMN "TB_BA_ZYRB"."RYS" IS '入院数';
COMMENT ON COLUMN "TB_BA_ZYRB"."ZRS" IS '转入数';
COMMENT ON COLUMN "TB_BA_ZYRB"."CYS" IS '出院数';
COMMENT ON COLUMN "TB_BA_ZYRB"."QZSWS" IS '其中死亡数';
COMMENT ON COLUMN "TB_BA_ZYRB"."ZCS" IS '转出数';
COMMENT ON COLUMN "TB_BA_ZYRB"."XRS" IS '现人数';
COMMENT ON COLUMN "TB_BA_ZYRB"."WZRC" IS '危重人次';
COMMENT ON COLUMN "TB_BA_ZYRB"."PBRC" IS '陪伴人次';
COMMENT ON COLUMN "TB_BA_ZYRB"."YLSGS" IS '医疗事故数';
COMMENT ON COLUMN "TB_BA_ZYRB"."CMI" IS 'CMI';
COMMENT ON COLUMN "TB_BA_ZYRB"."BZ" IS '说明';
COMMENT ON COLUMN "TB_BA_ZYRB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_ZYRB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_ZYRB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_ZYRB"."YLYL2" IS '预留二';
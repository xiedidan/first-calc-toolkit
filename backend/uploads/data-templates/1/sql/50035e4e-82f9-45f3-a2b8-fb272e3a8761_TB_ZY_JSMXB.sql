DROP TABLE IF EXISTS "TB_ZY_JSMXB";
CREATE TABLE "TB_ZY_JSMXB" (
    "YLJGDM" varchar(33),
    "JSMXID" varchar(54),
    "BRZSY" varchar(96),
    "SFMXID" varchar(54),
    "TFBZ" varchar(2),
    "JZLSH" varchar(75),
    "JSJLID" varchar(54),
    "SFJSSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_JSMXB" IS '住院结算明细表';
COMMENT ON COLUMN "TB_ZY_JSMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_JSMXB"."JSMXID" IS '结算明细 ID';
COMMENT ON COLUMN "TB_ZY_JSMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_JSMXB"."SFMXID" IS '收费明细 ID';
COMMENT ON COLUMN "TB_ZY_JSMXB"."TFBZ" IS '退费标志';
COMMENT ON COLUMN "TB_ZY_JSMXB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_JSMXB"."JSJLID" IS '结算记录 ID';
COMMENT ON COLUMN "TB_ZY_JSMXB"."SFJSSJ" IS '费用结算时间';
COMMENT ON COLUMN "TB_ZY_JSMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_JSMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_JSMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_JSMXB"."YLYL2" IS '预留二';
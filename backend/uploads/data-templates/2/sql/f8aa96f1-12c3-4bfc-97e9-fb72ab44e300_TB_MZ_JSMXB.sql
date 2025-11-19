DROP TABLE IF EXISTS "TB_MZ_JSMXB";
CREATE TABLE "TB_MZ_JSMXB" (
    "YLJGDM" varchar(33),
    "JSJLID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "JSFPH" varchar(300),
    "SFCJBM" varchar(2),
    "JLSFZT" varchar(2),
    "FYJSSJ" timestamp,
    "HZLYSX" varchar(9),
    "FYJSZJE" numeric(10,4),
    "JSRYGH" varchar(54),
    "JSRYXM" varchar(108),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_JSMXB" IS '门诊结算明细表';
COMMENT ON COLUMN "TB_MZ_JSMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JSJLID" IS '结算记录 ID';
COMMENT ON COLUMN "TB_MZ_JSMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JSFPH" IS '结算发票号';
COMMENT ON COLUMN "TB_MZ_JSMXB"."SFCJBM" IS '收费场景编码';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JLSFZT" IS '记录收费状态';
COMMENT ON COLUMN "TB_MZ_JSMXB"."FYJSSJ" IS '费用结算时间';
COMMENT ON COLUMN "TB_MZ_JSMXB"."HZLYSX" IS '患者来源属性';
COMMENT ON COLUMN "TB_MZ_JSMXB"."FYJSZJE" IS '费用结算总金额';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JSRYGH" IS '结算人员编号';
COMMENT ON COLUMN "TB_MZ_JSMXB"."JSRYXM" IS '结算人员姓名';
COMMENT ON COLUMN "TB_MZ_JSMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_JSMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_JSMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_JSMXB"."YLYL2" IS '预留二';
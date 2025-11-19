DROP TABLE IF EXISTS "TB_ZY_JSJLB";
CREATE TABLE "TB_ZY_JSJLB" (
    "YLJGDM" varchar(33),
    "JSJLID" varchar(54),
    "BRZSY" varchar(96),
    "YBKKH" varchar(45),
    "JZLSH" varchar(54),
    "JLSFZT" varchar(2),
    "JSFPH" varchar(300),
    "SFCJBM" varchar(2),
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
COMMENT ON TABLE "TB_ZY_JSJLB" IS '住院结算记录表';
COMMENT ON COLUMN "TB_ZY_JSJLB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JSJLID" IS '结算记录 ID';
COMMENT ON COLUMN "TB_ZY_JSJLB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_JSJLB"."YBKKH" IS '医保卡号';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JLSFZT" IS '记录收费状态';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JSFPH" IS '结算发票号';
COMMENT ON COLUMN "TB_ZY_JSJLB"."SFCJBM" IS '结算场景编码';
COMMENT ON COLUMN "TB_ZY_JSJLB"."FYJSSJ" IS '费用结算时间';
COMMENT ON COLUMN "TB_ZY_JSJLB"."HZLYSX" IS '患者来源属性';
COMMENT ON COLUMN "TB_ZY_JSJLB"."FYJSZJE" IS '费用结算总金额';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JSRYGH" IS '结算人员编号';
COMMENT ON COLUMN "TB_ZY_JSJLB"."JSRYXM" IS '结算人员姓名';
COMMENT ON COLUMN "TB_ZY_JSJLB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_JSJLB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_JSJLB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_JSJLB"."YLYL2" IS '预留二';
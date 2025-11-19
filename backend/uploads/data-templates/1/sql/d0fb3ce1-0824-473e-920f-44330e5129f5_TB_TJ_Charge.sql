DROP TABLE IF EXISTS "TB_TJ_Charge";
CREATE TABLE "TB_TJ_Charge" (
    "YLJGDM" varchar(33),
    "STFBH" varchar(75),
    "TFBZ" varchar(2),
    "BRZSY" varchar(96),
    "TJLBDM" varchar(2),
    "TJLSH" varchar(75),
    "TJDWBM" varchar(75),
    "TJDWMC" varchar(192),
    "STFRQSJ" timestamp,
    "STFZE" numeric(15,3),
    "SSJE" numeric(15,3),
    "YHJE" numeric(15,3),
    "FPH" varchar(96),
    "FPDYRQSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_TJ_Charge" IS '体检收费表';
COMMENT ON COLUMN "TB_TJ_Charge"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_TJ_Charge"."STFBH" IS '收/退费编号';
COMMENT ON COLUMN "TB_TJ_Charge"."TFBZ" IS '退费标志';
COMMENT ON COLUMN "TB_TJ_Charge"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_TJ_Charge"."TJLBDM" IS '体检类别代码';
COMMENT ON COLUMN "TB_TJ_Charge"."TJLSH" IS '体检流水号';
COMMENT ON COLUMN "TB_TJ_Charge"."TJDWBM" IS '体检单位编码';
COMMENT ON COLUMN "TB_TJ_Charge"."TJDWMC" IS '体检单位名称';
COMMENT ON COLUMN "TB_TJ_Charge"."STFRQSJ" IS '收/退费日期时间';
COMMENT ON COLUMN "TB_TJ_Charge"."STFZE" IS '收/退费总额';
COMMENT ON COLUMN "TB_TJ_Charge"."SSJE" IS '实收金额';
COMMENT ON COLUMN "TB_TJ_Charge"."YHJE" IS '优惠金额';
COMMENT ON COLUMN "TB_TJ_Charge"."FPH" IS '发票号';
COMMENT ON COLUMN "TB_TJ_Charge"."FPDYRQSJ" IS '发票打印日期时间';
COMMENT ON COLUMN "TB_TJ_Charge"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_TJ_Charge"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_TJ_Charge"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_TJ_Charge"."YLYL2" IS '预留二';
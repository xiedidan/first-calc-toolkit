DROP TABLE IF EXISTS "TB_YL_TJBG";
CREATE TABLE "TB_YL_TJBG" (
    "YLJGDM" varchar(33),
    "BGLSH" varchar(75),
    "TJBH" varchar(75),
    "KSBM" varchar(96),
    "KSMC" varchar(114),
    "ZHMC" varchar(75),
    "TJXJ" varchar(1536),
    "BGRQ" timestamp,
    "BGYSGH" varchar(54),
    "BGYSXM" varchar(108),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YL_TJBG" IS '体检分科（分组）报告';
COMMENT ON COLUMN "TB_YL_TJBG"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_YL_TJBG"."BGLSH" IS '分科报告流水号';
COMMENT ON COLUMN "TB_YL_TJBG"."TJBH" IS '体检编号';
COMMENT ON COLUMN "TB_YL_TJBG"."KSBM" IS '科室编码';
COMMENT ON COLUMN "TB_YL_TJBG"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_YL_TJBG"."ZHMC" IS '组合名称';
COMMENT ON COLUMN "TB_YL_TJBG"."TJXJ" IS '体检小结';
COMMENT ON COLUMN "TB_YL_TJBG"."BGRQ" IS '报告日期';
COMMENT ON COLUMN "TB_YL_TJBG"."BGYSGH" IS '报告医师编号';
COMMENT ON COLUMN "TB_YL_TJBG"."BGYSXM" IS '报告医师姓名';
COMMENT ON COLUMN "TB_YL_TJBG"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YL_TJBG"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YL_TJBG"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YL_TJBG"."YLYL2" IS '预留二';
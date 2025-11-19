DROP TABLE IF EXISTS "TB_YL_TJMX";
CREATE TABLE "TB_YL_TJMX" (
    "YLJGDM" varchar(33),
    "XMMXID" varchar(30),
    "BGLSH" varchar(75),
    "XMDM" varchar(30),
    "XMMC" varchar(60),
    "XMJCJG" varchar(150),
    "JCYCBZ" varchar(2),
    "YCSM" varchar(300),
    "CKZFW" varchar(192),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YL_TJMX" IS '体检明细表';
COMMENT ON COLUMN "TB_YL_TJMX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_YL_TJMX"."XMMXID" IS '项目明细 ID';
COMMENT ON COLUMN "TB_YL_TJMX"."BGLSH" IS '分科报告流水号';
COMMENT ON COLUMN "TB_YL_TJMX"."XMDM" IS '项目代码';
COMMENT ON COLUMN "TB_YL_TJMX"."XMMC" IS '项目名称';
COMMENT ON COLUMN "TB_YL_TJMX"."XMJCJG" IS '项目检查结果';
COMMENT ON COLUMN "TB_YL_TJMX"."JCYCBZ" IS '检查异常标志';
COMMENT ON COLUMN "TB_YL_TJMX"."YCSM" IS '异常说明';
COMMENT ON COLUMN "TB_YL_TJMX"."CKZFW" IS '参考值范围';
COMMENT ON COLUMN "TB_YL_TJMX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YL_TJMX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YL_TJMX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YL_TJMX"."YLYL2" IS '预留二';
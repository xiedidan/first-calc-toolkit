DROP TABLE IF EXISTS "TB_LIS_Allergy_Result";
CREATE TABLE "TB_LIS_Allergy_Result" (
    "YLJGDM" varchar(33),
    "YMJGLSH" varchar(75),
    "BGDH" varchar(96),
    "BGRQ" timestamp,
    "XJDH" varchar(48),
    "DYXH" numeric,
    "YMDM" varchar(60),
    "YMMC" varchar(60),
    "JCJG" varchar(768),
    "ZPHYL" varchar(24),
    "YJND" varchar(15),
    "YJHZJ" varchar(15),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_LIS_Allergy_Result" IS '药敏结果';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YMJGLSH" IS '药敏结果流水号';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."BGDH" IS '检验报告单号';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."BGRQ" IS '报告日期';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."XJDH" IS '细菌代号';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."DYXH" IS '打印序号';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YMDM" IS '药敏代码';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YMMC" IS '药敏名称';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."JCJG" IS '检测结果描述';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."ZPHYL" IS '纸片含药量';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YJND" IS '抑菌浓度';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YJHZJ" IS '抑菌环直径';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_LIS_Allergy_Result"."YLYL2" IS '预留二';
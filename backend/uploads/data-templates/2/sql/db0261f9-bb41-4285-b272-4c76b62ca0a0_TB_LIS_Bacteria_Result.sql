DROP TABLE IF EXISTS "TB_LIS_Bacteria_Result";
CREATE TABLE "TB_LIS_Bacteria_Result" (
    "YLJGDM" varchar(33),
    "XJJGLSH" varchar(75),
    "BGDH" varchar(96),
    "BGRQ" timestamp,
    "XJDH" varchar(48),
    "XJMC" varchar(192),
    "JLJS" varchar(24),
    "BYJ" varchar(60),
    "BYSJ" varchar(24),
    "PYTJ" varchar(96),
    "FXFS" varchar(96),
    "JCJG" varchar(105),
    "JCJGWZ" varchar(1536),
    "SBBM" varchar(30),
    "YQBH" varchar(30),
    "YQMC" varchar(150),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_LIS_Bacteria_Result" IS '细菌结果';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."XJJGLSH" IS '细菌结果流水号';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."BGDH" IS '检验报告单号';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."BGRQ" IS '报告日期';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."XJDH" IS '细菌代号';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."XJMC" IS '细菌名称';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."JLJS" IS '菌落计数';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."BYJ" IS '培养基';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."BYSJ" IS '培养时间';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."PYTJ" IS '培养条件';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."FXFS" IS '发现方式';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."JCJG" IS '检测结果';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."JCJGWZ" IS '检测结果文字描述';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."SBBM" IS '设备编码';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."YQBH" IS '仪器编号';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."YQMC" IS '仪器名称';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_LIS_Bacteria_Result"."YLYL2" IS '预留二';
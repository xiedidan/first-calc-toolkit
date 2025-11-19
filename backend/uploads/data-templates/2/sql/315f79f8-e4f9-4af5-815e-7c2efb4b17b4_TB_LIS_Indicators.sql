DROP TABLE IF EXISTS "TB_LIS_Indicators";
CREATE TABLE "TB_LIS_Indicators" (
    "YLJGDM" varchar(33),
    "JYZBLSH" varchar(75),
    "BGDH" varchar(96),
    "BGRQ" timestamp,
    "YBSFDM" varchar(30),
    "JCZBDM" varchar(48),
    "JCFF" varchar(48),
    "JCZBMC" varchar(150),
    "JCZBJG" varchar(600),
    "LOINC" varchar(15),
    "CKZ" varchar(192),
    "WJZBS" varchar(2),
    "WJZBGRQ" timestamp,
    "JLDW" varchar(30),
    "SBBM" varchar(30),
    "YQBH" varchar(30),
    "YQMC" varchar(150),
    "YCTS" varchar(3),
    "YZID" varchar(54),
    "DYXH" numeric,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_LIS_Indicators" IS '检验结果指标表';
COMMENT ON COLUMN "TB_LIS_Indicators"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_LIS_Indicators"."JYZBLSH" IS '检验指标流水号';
COMMENT ON COLUMN "TB_LIS_Indicators"."BGDH" IS '检验报告单号';
COMMENT ON COLUMN "TB_LIS_Indicators"."BGRQ" IS '报告日期';
COMMENT ON COLUMN "TB_LIS_Indicators"."YBSFDM" IS '检测收费代码';
COMMENT ON COLUMN "TB_LIS_Indicators"."JCZBDM" IS '检测指标代码';
COMMENT ON COLUMN "TB_LIS_Indicators"."JCFF" IS '检测方法名称';
COMMENT ON COLUMN "TB_LIS_Indicators"."JCZBMC" IS '检测指标名称';
COMMENT ON COLUMN "TB_LIS_Indicators"."JCZBJG" IS '检测指标结果';
COMMENT ON COLUMN "TB_LIS_Indicators"."LOINC" IS 'LOINC 编码';
COMMENT ON COLUMN "TB_LIS_Indicators"."CKZ" IS '参考值范围';
COMMENT ON COLUMN "TB_LIS_Indicators"."WJZBS" IS '危急值标识';
COMMENT ON COLUMN "TB_LIS_Indicators"."WJZBGRQ" IS '危急值报告日期';
COMMENT ON COLUMN "TB_LIS_Indicators"."JLDW" IS '计量单位';
COMMENT ON COLUMN "TB_LIS_Indicators"."SBBM" IS '设备编码';
COMMENT ON COLUMN "TB_LIS_Indicators"."YQBH" IS '仪器编号';
COMMENT ON COLUMN "TB_LIS_Indicators"."YQMC" IS '仪器名称';
COMMENT ON COLUMN "TB_LIS_Indicators"."YCTS" IS '异常提示';
COMMENT ON COLUMN "TB_LIS_Indicators"."YZID" IS '相关医嘱 ID 或处方项目明细编号';
COMMENT ON COLUMN "TB_LIS_Indicators"."DYXH" IS '打印序号';
COMMENT ON COLUMN "TB_LIS_Indicators"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_LIS_Indicators"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_LIS_Indicators"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_LIS_Indicators"."YLYL2" IS '预留二';
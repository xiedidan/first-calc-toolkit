DROP TABLE IF EXISTS "TB_YP_RRK";
CREATE TABLE "TB_YP_RRK" (
    "YLJGDM" varchar(33),
    "RKDH" varchar(33),
    "XH" varchar(33),
    "KCGLDW" varchar(75),
    "RKRQ" timestamp,
    "GHF" varchar(75),
    "RKLB" varchar(15),
    "CFKF" varchar(150),
    "JZBZ" varchar(225),
    "LRZ" varchar(75),
    "SZRQ" timestamp,
    "SZR" varchar(75),
    "PZH" varchar(75),
    "SZBZ" varchar(75),
    "JBYWBZ" varchar(75),
    "ZBYWBZ" varchar(75),
    "KJYWBZ" varchar(75),
    "YPLX" varchar(75),
    "YPDM" varchar(75),
    "GG" varchar(75),
    "DW" varchar(75),
    "PH" varchar(75),
    "YXQ" timestamp,
    "CJBS" varchar(75),
    "JHJ" numeric(18,4),
    "ZK" numeric(18,4),
    "LSJ" numeric(18,4),
    "BZGG" varchar(75),
    "SL" numeric(18,4),
    "BZDW" varchar(75),
    "NHBZ1" numeric(18,4),
    "NHBZ1DW" varchar(75),
    "NHBZ1GG" varchar(75),
    "NHBZ2" numeric(18,4),
    "NHBZ2DW" varchar(75),
    "NHBZ2GG" varchar(75),
    "FPH" varchar(75),
    "FPRQ" varchar(150),
    "FPFKBZ" varchar(75),
    "PFJ" numeric(18,4),
    "RKHCS" numeric(18,4),
    "BZ" varchar(150),
    "ZBPH" varchar(150),
    "ZBXH" varchar(150),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YP_RRK" IS '药品入库记录';
COMMENT ON COLUMN "TB_YP_RRK"."YLJGDM" IS '医疗机构组代码';
COMMENT ON COLUMN "TB_YP_RRK"."RKDH" IS '入库单号';
COMMENT ON COLUMN "TB_YP_RRK"."XH" IS '项目序号';
COMMENT ON COLUMN "TB_YP_RRK"."KCGLDW" IS '库存管理单位';
COMMENT ON COLUMN "TB_YP_RRK"."RKRQ" IS '入库日期';
COMMENT ON COLUMN "TB_YP_RRK"."GHF" IS '供货方';
COMMENT ON COLUMN "TB_YP_RRK"."RKLB" IS '入库类别';
COMMENT ON COLUMN "TB_YP_RRK"."CFKF" IS '存放库房';
COMMENT ON COLUMN "TB_YP_RRK"."JZBZ" IS '记帐标志';
COMMENT ON COLUMN "TB_YP_RRK"."LRZ" IS '录入者';
COMMENT ON COLUMN "TB_YP_RRK"."SZRQ" IS '上账日期';
COMMENT ON COLUMN "TB_YP_RRK"."SZR" IS '上帐人';
COMMENT ON COLUMN "TB_YP_RRK"."PZH" IS '凭证号';
COMMENT ON COLUMN "TB_YP_RRK"."SZBZ" IS '上账标志';
COMMENT ON COLUMN "TB_YP_RRK"."JBYWBZ" IS '基本药物标志';
COMMENT ON COLUMN "TB_YP_RRK"."ZBYWBZ" IS '中标药物标志';
COMMENT ON COLUMN "TB_YP_RRK"."KJYWBZ" IS '抗菌药物标志';
COMMENT ON COLUMN "TB_YP_RRK"."YPLX" IS '药品类型';
COMMENT ON COLUMN "TB_YP_RRK"."YPDM" IS '药品代码';
COMMENT ON COLUMN "TB_YP_RRK"."GG" IS '规格';
COMMENT ON COLUMN "TB_YP_RRK"."DW" IS '单位';
COMMENT ON COLUMN "TB_YP_RRK"."PH" IS '批号';
COMMENT ON COLUMN "TB_YP_RRK"."YXQ" IS '有效期';
COMMENT ON COLUMN "TB_YP_RRK"."CJBS" IS '厂家标识';
COMMENT ON COLUMN "TB_YP_RRK"."JHJ" IS '进货价';
COMMENT ON COLUMN "TB_YP_RRK"."ZK" IS '折扣';
COMMENT ON COLUMN "TB_YP_RRK"."LSJ" IS '零售价';
COMMENT ON COLUMN "TB_YP_RRK"."BZGG" IS '包装规格';
COMMENT ON COLUMN "TB_YP_RRK"."SL" IS '数量';
COMMENT ON COLUMN "TB_YP_RRK"."BZDW" IS '包装单位';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ1" IS '内含包装 1';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ1DW" IS '内含包装 1 单位';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ1GG" IS '内含包装 1 规格';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ2" IS '内含包装 2';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ2DW" IS '内含包装 2 单位';
COMMENT ON COLUMN "TB_YP_RRK"."NHBZ2GG" IS '内含包装 2 规格';
COMMENT ON COLUMN "TB_YP_RRK"."FPH" IS '发票号';
COMMENT ON COLUMN "TB_YP_RRK"."FPRQ" IS '发票日期';
COMMENT ON COLUMN "TB_YP_RRK"."FPFKBZ" IS '发票付款标志';
COMMENT ON COLUMN "TB_YP_RRK"."PFJ" IS '批发价';
COMMENT ON COLUMN "TB_YP_RRK"."RKHCS" IS '入库后库存数';
COMMENT ON COLUMN "TB_YP_RRK"."BZ" IS '备注';
COMMENT ON COLUMN "TB_YP_RRK"."ZBPH" IS '招标批号';
COMMENT ON COLUMN "TB_YP_RRK"."ZBXH" IS '中标序号';
COMMENT ON COLUMN "TB_YP_RRK"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YP_RRK"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YP_RRK"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YP_RRK"."YLYL2" IS '预留二';
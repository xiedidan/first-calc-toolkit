DROP TABLE IF EXISTS "TB_JC_YPML";
CREATE TABLE "TB_JC_YPML" (
    "YLJGDM" varchar(33),
    "YYZBDM" varchar(48),
    "YPMC" varchar(150),
    "GJMLBM" varchar(48),
    "YBMLBM" varchar(48),
    "TYMC" varchar(150),
    "SPM" varchar(75),
    "YWMC" varchar(150),
    "ZYCFTYM" varchar(75),
    "ZYCFHXM" varchar(75),
    "YPGG" varchar(96),
    "BZ" varchar(383),
    "YPDW" varchar(96),
    "YNJXDM" varchar(30),
    "YNJXMC" varchar(60),
    "JL" numeric(15,4),
    "JLDW" varchar(96),
    "YPDJ" numeric(15,4),
    "SYBZ" varchar(2),
    "TSBZ" varchar(2),
    "KSSJBDM" varchar(2),
    "KSSBZ" varchar(2),
    "DDDZ" numeric(15,4),
    "DDDDW" varchar(96),
    "KJYWSYDJDM" varchar(2),
    "KJYWPL" varchar(75),
    "YPPZWH" varchar(150),
    "YPBWM" varchar(21),
    "YPJGM" varchar(48),
    "SCCJDM" varchar(48),
    "SCCJMC" varchar(105),
    "YWGHSMC" varchar(300),
    "YPLX" varchar(2),
    "YNZJBZ" varchar(2),
    "YWLXBMBZ" varchar(75),
    "YWLXMCBZ" varchar(383),
    "JKGCBZ" varchar(2),
    "GJYBZ" varchar(2),
    "SJYBZ" varchar(2),
    "SHJYBZ" varchar(2),
    "QJYBZ" varchar(2),
    "SFQXYPJC" varchar(2),
    "QXYPJCRQ" timestamp,
    "TBSM" varchar(150),
    "CFYBZ" varchar(2),
    "ZBYP" varchar(2),
    "FZYYBZ" varchar(2),
    "YN_FL_CODE" varchar(75),
    "SJ_FL_CODE" varchar(75),
    "SY_FL_CODE" varchar(75),
    "KJ_FL_CODE" varchar(75),
    "HS_FL_CODE" varchar(75),
    "BZSM" varchar(750),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_JC_YPML" IS '药品目录表';
COMMENT ON COLUMN "TB_JC_YPML"."YLJGDM" IS '医疗机构组织机构代码';
COMMENT ON COLUMN "TB_JC_YPML"."YYZBDM" IS '医院自编代码';
COMMENT ON COLUMN "TB_JC_YPML"."YPMC" IS '药品名称';
COMMENT ON COLUMN "TB_JC_YPML"."GJMLBM" IS '药品标准代码（国家药品编码）';
COMMENT ON COLUMN "TB_JC_YPML"."YBMLBM" IS '药品标准代码（医保药品编码）';
COMMENT ON COLUMN "TB_JC_YPML"."TYMC" IS '药品注册通用名';
COMMENT ON COLUMN "TB_JC_YPML"."SPM" IS '商品名';
COMMENT ON COLUMN "TB_JC_YPML"."YWMC" IS '英文名称';
COMMENT ON COLUMN "TB_JC_YPML"."ZYCFTYM" IS '主要成份通用名';
COMMENT ON COLUMN "TB_JC_YPML"."ZYCFHXM" IS '主要成份化学名';
COMMENT ON COLUMN "TB_JC_YPML"."YPGG" IS '药品规格';
COMMENT ON COLUMN "TB_JC_YPML"."BZ" IS '包装规格';
COMMENT ON COLUMN "TB_JC_YPML"."YPDW" IS '药品基础单位';
COMMENT ON COLUMN "TB_JC_YPML"."YNJXDM" IS '院内剂型代码';
COMMENT ON COLUMN "TB_JC_YPML"."YNJXMC" IS '院内剂型名称';
COMMENT ON COLUMN "TB_JC_YPML"."JL" IS '剂量';
COMMENT ON COLUMN "TB_JC_YPML"."JLDW" IS '剂量单位';
COMMENT ON COLUMN "TB_JC_YPML"."YPDJ" IS '药品单价';
COMMENT ON COLUMN "TB_JC_YPML"."SYBZ" IS '使用标志';
COMMENT ON COLUMN "TB_JC_YPML"."TSBZ" IS '特殊标志';
COMMENT ON COLUMN "TB_JC_YPML"."KSSJBDM" IS '抗生素级别代码';
COMMENT ON COLUMN "TB_JC_YPML"."KSSBZ" IS '抗菌药物标识';
COMMENT ON COLUMN "TB_JC_YPML"."DDDZ" IS 'DDD 值';
COMMENT ON COLUMN "TB_JC_YPML"."DDDDW" IS 'DDD 单位';
COMMENT ON COLUMN "TB_JC_YPML"."KJYWSYDJDM" IS '抗菌药物使用等级';
COMMENT ON COLUMN "TB_JC_YPML"."KJYWPL" IS '抗菌药物品类';
COMMENT ON COLUMN "TB_JC_YPML"."YPPZWH" IS '批准文号';
COMMENT ON COLUMN "TB_JC_YPML"."YPBWM" IS '本位码';
COMMENT ON COLUMN "TB_JC_YPML"."YPJGM" IS '监管码';
COMMENT ON COLUMN "TB_JC_YPML"."SCCJDM" IS '生产厂家代码';
COMMENT ON COLUMN "TB_JC_YPML"."SCCJMC" IS '生产厂家名称';
COMMENT ON COLUMN "TB_JC_YPML"."YWGHSMC" IS '药物供货厂商名称';
COMMENT ON COLUMN "TB_JC_YPML"."YPLX" IS '药品类型';
COMMENT ON COLUMN "TB_JC_YPML"."YNZJBZ" IS '院内制剂标志';
COMMENT ON COLUMN "TB_JC_YPML"."YWLXBMBZ" IS '药物类型编码标准';
COMMENT ON COLUMN "TB_JC_YPML"."YWLXMCBZ" IS '药物类型名称标准';
COMMENT ON COLUMN "TB_JC_YPML"."JKGCBZ" IS '进口还是国产';
COMMENT ON COLUMN "TB_JC_YPML"."GJYBZ" IS '是否国家基本药物';
COMMENT ON COLUMN "TB_JC_YPML"."SJYBZ" IS '是否省基本药物';
COMMENT ON COLUMN "TB_JC_YPML"."SHJYBZ" IS '是否市基本药物';
COMMENT ON COLUMN "TB_JC_YPML"."QJYBZ" IS '是否区基本药物';
COMMENT ON COLUMN "TB_JC_YPML"."SFQXYPJC" IS '是否取消药品加成';
COMMENT ON COLUMN "TB_JC_YPML"."QXYPJCRQ" IS '取消药品加成日期';
COMMENT ON COLUMN "TB_JC_YPML"."TBSM" IS '药品特别说明';
COMMENT ON COLUMN "TB_JC_YPML"."CFYBZ" IS '处方药标志';
COMMENT ON COLUMN "TB_JC_YPML"."ZBYP" IS '中标药品';
COMMENT ON COLUMN "TB_JC_YPML"."FZYYBZ" IS '辅助用药标志';
COMMENT ON COLUMN "TB_JC_YPML"."YN_FL_CODE" IS '院内费用分类编码';
COMMENT ON COLUMN "TB_JC_YPML"."SJ_FL_CODE" IS '收据分类编码';
COMMENT ON COLUMN "TB_JC_YPML"."SY_FL_CODE" IS '首页分类编码';
COMMENT ON COLUMN "TB_JC_YPML"."KJ_FL_CODE" IS '会计科目分类编码';
COMMENT ON COLUMN "TB_JC_YPML"."HS_FL_CODE" IS '核算科目分类编码';
COMMENT ON COLUMN "TB_JC_YPML"."BZSM" IS '备注说明';
COMMENT ON COLUMN "TB_JC_YPML"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_JC_YPML"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_JC_YPML"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_JC_YPML"."YLYL2" IS '预留二';
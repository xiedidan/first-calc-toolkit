DROP TABLE IF EXISTS "TB_MZ_GHMXB";
CREATE TABLE "TB_MZ_GHMXB" (
    "YLJGDM" varchar(33),
    "GHJLID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "GTHBZ" varchar(2),
    "STFBH" varchar(75),
    "GTHSJ" timestamp,
    "GHLB" varchar(5),
    "SFJZ" varchar(2),
    "JZXZ" varchar(6),
    "GHTJBM" varchar(6),
    "BXLX" varchar(30),
    "KSBM" varchar(96),
    "KSMC" varchar(114),
    "LCYXLXBM" varchar(3),
    "GHYSGH" varchar(54),
    "GHYSXM" varchar(108),
    "GHYSSFZHM" varchar(27),
    "TXBZ" varchar(2),
    "WDBZ" varchar(2),
    "GHZFY" numeric(10,4),
    "SFSQ" varchar(2),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_GHMXB" IS '挂号明细表';
COMMENT ON COLUMN "TB_MZ_GHMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHJLID" IS '挂号记录 ID';
COMMENT ON COLUMN "TB_MZ_GHMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_GHMXB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GTHBZ" IS '退号标志';
COMMENT ON COLUMN "TB_MZ_GHMXB"."STFBH" IS '收/退费编号';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GTHSJ" IS '挂/退号时间';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHLB" IS '挂号类别';
COMMENT ON COLUMN "TB_MZ_GHMXB"."SFJZ" IS '是否急诊';
COMMENT ON COLUMN "TB_MZ_GHMXB"."JZXZ" IS '就诊性质';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHTJBM" IS '挂号途径编码';
COMMENT ON COLUMN "TB_MZ_GHMXB"."BXLX" IS '保险类型（患者属性）';
COMMENT ON COLUMN "TB_MZ_GHMXB"."KSBM" IS '科室编码';
COMMENT ON COLUMN "TB_MZ_GHMXB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_MZ_GHMXB"."LCYXLXBM" IS '临床医学类型编码';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHYSGH" IS '挂号医生编号';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHYSXM" IS '挂号医生姓名';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHYSSFZHM" IS '挂号医生身份证号码';
COMMENT ON COLUMN "TB_MZ_GHMXB"."TXBZ" IS '特需标志';
COMMENT ON COLUMN "TB_MZ_GHMXB"."WDBZ" IS '外地标志';
COMMENT ON COLUMN "TB_MZ_GHMXB"."GHZFY" IS '挂号总费用';
COMMENT ON COLUMN "TB_MZ_GHMXB"."SFSQ" IS '是否授权';
COMMENT ON COLUMN "TB_MZ_GHMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_GHMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_GHMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_GHMXB"."YLYL2" IS '预留二';
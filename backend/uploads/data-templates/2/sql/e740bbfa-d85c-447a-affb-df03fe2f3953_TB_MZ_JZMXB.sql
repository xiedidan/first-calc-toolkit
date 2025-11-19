DROP TABLE IF EXISTS "TB_MZ_JZMXB";
CREATE TABLE "TB_MZ_JZMXB" (
    "YLJGDM" varchar(33),
    "JZMXID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "SFFZ" varchar(2),
    "LCYXLXBM" varchar(3),
    "MZH" varchar(54),
    "HZXM" varchar(108),
    "HZSX" varchar(30),
    "JZLX" varchar(5),
    "SFJZ" varchar(2),
    "JZXZ" varchar(6),
    "JZKSBM" varchar(96),
    "JZKSMC" varchar(114),
    "JZKSRQ" varchar(12),
    "JZSJ" timestamp,
    "WCJZSJ" timestamp,
    "ZZYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZZYSSFZHM" varchar(27),
    "JZZDBM" varchar(750),
    "JZZDMC" varchar(1500),
    "ZXBM" varchar(750),
    "ZXMC" varchar(1500),
    "ZFMC" varchar(96),
    "BMLX" varchar(3),
    "JZZDSM" varchar(1536),
    "ZS" varchar(3000),
    "MZZZMC" varchar(1500),
    "MZZZZDDM" varchar(750),
    "LGGC" varchar(3),
    "ZZMS" varchar(3000),
    "FBRQSJ" timestamp,
    "SSY" numeric,
    "SZY" numeric,
    "TW" numeric,
    "ZZCXSJ" varchar(5),
    "ZXWT" varchar(1500),
    "WSFWYQ" varchar(1500),
    "CZJH" varchar(3000),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_JZMXB" IS '门诊就诊明细表';
COMMENT ON COLUMN "TB_MZ_JZMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZMXID" IS '就诊明细 ID';
COMMENT ON COLUMN "TB_MZ_JZMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_JZMXB"."SFFZ" IS '是否复诊';
COMMENT ON COLUMN "TB_MZ_JZMXB"."LCYXLXBM" IS '临床医学类型编码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."MZH" IS '门诊号';
COMMENT ON COLUMN "TB_MZ_JZMXB"."HZXM" IS '患者姓名';
COMMENT ON COLUMN "TB_MZ_JZMXB"."HZSX" IS '患者属性';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZLX" IS '就诊类型';
COMMENT ON COLUMN "TB_MZ_JZMXB"."SFJZ" IS '是否急诊';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZXZ" IS '就诊性质';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZKSBM" IS '就诊科室编码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZKSMC" IS '就诊科室名称';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZKSRQ" IS '门诊就诊日期';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZSJ" IS '接诊时间';
COMMENT ON COLUMN "TB_MZ_JZMXB"."WCJZSJ" IS '完成就诊时间';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZZYSGH" IS '主诊医生编号';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZZYSXM" IS '主诊医生姓名';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZZYSSFZHM" IS '主诊医生身份证号码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZZDBM" IS '门诊诊断编码（主要诊断)';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZZDMC" IS '门诊诊断名称（主要诊断）';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZXBM" IS '证型编码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZXMC" IS '证型名称';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZFMC" IS '治法名称';
COMMENT ON COLUMN "TB_MZ_JZMXB"."BMLX" IS '编码类型';
COMMENT ON COLUMN "TB_MZ_JZMXB"."JZZDSM" IS '门诊诊断说明';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_MZ_JZMXB"."MZZZMC" IS '门诊症状-名称';
COMMENT ON COLUMN "TB_MZ_JZMXB"."MZZZZDDM" IS '门诊症状-诊断代码';
COMMENT ON COLUMN "TB_MZ_JZMXB"."LGGC" IS '留观观察';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZZMS" IS '症状描述';
COMMENT ON COLUMN "TB_MZ_JZMXB"."FBRQSJ" IS '发病日期时间';
COMMENT ON COLUMN "TB_MZ_JZMXB"."SSY" IS '收缩压(mmHg)';
COMMENT ON COLUMN "TB_MZ_JZMXB"."SZY" IS '舒张压(mmHg)';
COMMENT ON COLUMN "TB_MZ_JZMXB"."TW" IS '体温(℃)';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZZCXSJ" IS '症状持续时间';
COMMENT ON COLUMN "TB_MZ_JZMXB"."ZXWT" IS '咨询问题';
COMMENT ON COLUMN "TB_MZ_JZMXB"."WSFWYQ" IS '卫生服务要求';
COMMENT ON COLUMN "TB_MZ_JZMXB"."CZJH" IS '处置计划';
COMMENT ON COLUMN "TB_MZ_JZMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_JZMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_JZMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_JZMXB"."YLYL2" IS '预留二';
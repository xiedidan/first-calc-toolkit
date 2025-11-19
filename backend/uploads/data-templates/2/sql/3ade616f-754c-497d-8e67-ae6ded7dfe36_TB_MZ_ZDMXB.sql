DROP TABLE IF EXISTS "TB_MZ_ZDMXB";
CREATE TABLE "TB_MZ_ZDMXB" (
    "YLJGDM" varchar(33),
    "ZDID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "ZDRQSJ" timestamp,
    "ZDFFBM" varchar(3),
    "ZDBZBM" varchar(3),
    "ZDLBBM" varchar(3),
    "BZQBDM" varchar(3),
    "ZDYBID" varchar(54),
    "ZDZCBM" varchar(3),
    "ZDSX" numeric,
    "ZDBM" varchar(750),
    "ZDMC" varchar(1500),
    "SFYZ" varchar(3),
    "HZQXDM" varchar(2),
    "ZDLX" varchar(2),
    "JLSJ_YWK" timestamp,
    "CXSJ_YWK" timestamp,
    "BJSJ_YWK" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_ZDMXB" IS '门诊诊断明细表';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDID" IS '诊断 ID';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDRQSJ" IS '诊断日期时间';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDFFBM" IS '诊断方法代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDBZBM" IS '诊断标准代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDLBBM" IS '诊断类别代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."BZQBDM" IS '病证区别代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDYBID" IS '证对应病 ID';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDZCBM" IS '诊断主次代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDSX" IS '诊断顺序';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDBM" IS '诊断代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDMC" IS '诊断名称';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."SFYZ" IS '是否疑诊';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."HZQXDM" IS '患者去向代码';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."ZDLX" IS '诊断类型';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."JLSJ_YWK" IS '记录时间';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."CXSJ_YWK" IS '撤销时间';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."BJSJ_YWK" IS '编辑时间';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_ZDMXB"."YLYL2" IS '预留二';
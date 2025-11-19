DROP TABLE IF EXISTS "TB_ZY_ZDMXB";
CREATE TABLE "TB_ZY_ZDMXB" (
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
    "CYQKBM" varchar(6),
    "JLSJ_YWK" timestamp,
    "BJSJ_YWK" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_ZDMXB" IS '住院诊断明细表';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDID" IS '诊断 ID';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDRQSJ" IS '诊断日期时间';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDFFBM" IS '诊断方法编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDBZBM" IS '诊断标准编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDLBBM" IS '诊断类别编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."BZQBDM" IS '病证区别编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDYBID" IS '证对应病 ID';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDZCBM" IS '诊断主次编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDSX" IS '诊断顺序';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDBM" IS '诊断编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."ZDMC" IS '诊断名称';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."SFYZ" IS '是否疑诊';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."CYQKBM" IS '出院情况编码';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."JLSJ_YWK" IS '记录时间';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."BJSJ_YWK" IS '编辑时间';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_ZDMXB"."YLYL2" IS '预留二';
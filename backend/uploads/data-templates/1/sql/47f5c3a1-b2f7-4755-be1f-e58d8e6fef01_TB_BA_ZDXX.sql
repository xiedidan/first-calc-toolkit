DROP TABLE IF EXISTS "TB_BA_ZDXX";
CREATE TABLE "TB_BA_ZDXX" (
    "YLJGDM" varchar(33),
    "ZDID" varchar(54),
    "BRZSY" varchar(96),
    "ZYH" varchar(48),
    "ZYJZLSH" varchar(54),
    "ZYBAH" varchar(27),
    "BLH" varchar(384),
    "ZDFFBM" varchar(3),
    "ZDBZBM" varchar(3),
    "ZDLBBM" varchar(3),
    "BZQBDM" varchar(3),
    "BDYZID" varchar(54),
    "ZDZCBM" varchar(3),
    "ZDSX" numeric,
    "ZDBM" varchar(48),
    "ZDMC" varchar(108),
    "SFYZ" varchar(3),
    "RYJBBQDM" varchar(2),
    "RYJBBQMC" varchar(15),
    "CYQKBM" varchar(6),
    "ZDYJDM" varchar(48),
    "ZDYJMC" varchar(300),
    "ZGZDYJDM" varchar(2),
    "FHCDDM" varchar(2),
    "FHCDMC" varchar(30),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_ZDXX" IS '住院病案诊断信息';
COMMENT ON COLUMN "TB_BA_ZDXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDID" IS '诊断 ID';
COMMENT ON COLUMN "TB_BA_ZDXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZYJZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZYBAH" IS '住院病案号';
COMMENT ON COLUMN "TB_BA_ZDXX"."BLH" IS '病理号';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDFFBM" IS '诊断方法编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDBZBM" IS '诊断标准编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDLBBM" IS '诊断类别编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."BZQBDM" IS '病证区别编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."BDYZID" IS '病对应证 ID';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDZCBM" IS '诊断主次编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDSX" IS '诊断顺序';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDBM" IS '诊断编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDMC" IS '诊断名称';
COMMENT ON COLUMN "TB_BA_ZDXX"."SFYZ" IS '是否疑诊';
COMMENT ON COLUMN "TB_BA_ZDXX"."RYJBBQDM" IS '入院疾病病情代码';
COMMENT ON COLUMN "TB_BA_ZDXX"."RYJBBQMC" IS '入院疾病病情名称';
COMMENT ON COLUMN "TB_BA_ZDXX"."CYQKBM" IS '出院情况编码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDYJDM" IS '诊断依据代码';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZDYJMC" IS '诊断依据名称';
COMMENT ON COLUMN "TB_BA_ZDXX"."ZGZDYJDM" IS '最高诊断依据代码';
COMMENT ON COLUMN "TB_BA_ZDXX"."FHCDDM" IS '分化程度代码';
COMMENT ON COLUMN "TB_BA_ZDXX"."FHCDMC" IS '分化程度名称';
COMMENT ON COLUMN "TB_BA_ZDXX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_ZDXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_ZDXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_ZDXX"."YLYL2" IS '预留二';
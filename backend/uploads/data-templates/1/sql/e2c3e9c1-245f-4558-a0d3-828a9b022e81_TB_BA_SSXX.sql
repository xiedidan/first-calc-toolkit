DROP TABLE IF EXISTS "TB_BA_SSXX";
CREATE TABLE "TB_BA_SSXX" (
    "YLJGDM" varchar(33),
    "SSID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "ZYBAH" varchar(27),
    "SSJCZBM" varchar(48),
    "SSJCZRQ" timestamp,
    "SSJB" varchar(2),
    "SSCXSJ" numeric,
    "SSHZLXDM" varchar(2),
    "SSHZLXMC" varchar(75),
    "SSZXM" varchar(108),
    "SSJCZMC" varchar(48),
    "SSSZ" varchar(48),
    "SSYZ" varchar(48),
    "SSEZ" varchar(48),
    "QKLBDM" varchar(2),
    "QKLBMC" varchar(24),
    "QKYHDJDM" varchar(2),
    "QKYHDJMC" varchar(24),
    "MZFFDM" varchar(30),
    "MZFFMC" varchar(150),
    "MZYWMC" varchar(768),
    "MZYWBM" varchar(300),
    "MZYYJL" varchar(150),
    "MZYYJLDW" varchar(150),
    "MZKSRQ" timestamp,
    "MZJSRQ" timestamp,
    "MZHBZDM" varchar(96),
    "MZHBZMC" varchar(768),
    "MZHBZMS" varchar(1536),
    "RFSSRQ" timestamp,
    "CFSSRQ" timestamp,
    "MZYSXM" varchar(108),
    "MZFJDM" varchar(2),
    "MZFJMC" varchar(48),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_SSXX" IS '住院病案手术信息';
COMMENT ON COLUMN "TB_BA_SSXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_SSXX"."SSID" IS '手术 ID';
COMMENT ON COLUMN "TB_BA_SSXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_SSXX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_SSXX"."ZYBAH" IS '住院病案号';
COMMENT ON COLUMN "TB_BA_SSXX"."SSJCZBM" IS '手术及操作编码';
COMMENT ON COLUMN "TB_BA_SSXX"."SSJCZRQ" IS '手术及操作日期';
COMMENT ON COLUMN "TB_BA_SSXX"."SSJB" IS '手术级别';
COMMENT ON COLUMN "TB_BA_SSXX"."SSCXSJ" IS '手术持续时间';
COMMENT ON COLUMN "TB_BA_SSXX"."SSHZLXDM" IS '手术患者类型代码';
COMMENT ON COLUMN "TB_BA_SSXX"."SSHZLXMC" IS '手术患者类型名称';
COMMENT ON COLUMN "TB_BA_SSXX"."SSZXM" IS '手术者姓名';
COMMENT ON COLUMN "TB_BA_SSXX"."SSJCZMC" IS '手术及操作名称';
COMMENT ON COLUMN "TB_BA_SSXX"."SSSZ" IS '手术术者';
COMMENT ON COLUMN "TB_BA_SSXX"."SSYZ" IS '手术 Ⅰ助';
COMMENT ON COLUMN "TB_BA_SSXX"."SSEZ" IS '手术Ⅱ助';
COMMENT ON COLUMN "TB_BA_SSXX"."QKLBDM" IS '手术切口类别代码';
COMMENT ON COLUMN "TB_BA_SSXX"."QKLBMC" IS '手术切口类别名称';
COMMENT ON COLUMN "TB_BA_SSXX"."QKYHDJDM" IS '手术切口愈合等级代码';
COMMENT ON COLUMN "TB_BA_SSXX"."QKYHDJMC" IS '手术切口愈合等级名称';
COMMENT ON COLUMN "TB_BA_SSXX"."MZFFDM" IS '麻醉方法代码';
COMMENT ON COLUMN "TB_BA_SSXX"."MZFFMC" IS '麻醉方法名称';
COMMENT ON COLUMN "TB_BA_SSXX"."MZYWMC" IS '麻醉药物名称';
COMMENT ON COLUMN "TB_BA_SSXX"."MZYWBM" IS '麻醉药物编码';
COMMENT ON COLUMN "TB_BA_SSXX"."MZYYJL" IS '麻醉用药剂量';
COMMENT ON COLUMN "TB_BA_SSXX"."MZYYJLDW" IS '麻醉用药剂量单位';
COMMENT ON COLUMN "TB_BA_SSXX"."MZKSRQ" IS '麻醉开始日期时间';
COMMENT ON COLUMN "TB_BA_SSXX"."MZJSRQ" IS '麻醉结束日期时间';
COMMENT ON COLUMN "TB_BA_SSXX"."MZHBZDM" IS '麻醉合并症代码';
COMMENT ON COLUMN "TB_BA_SSXX"."MZHBZMC" IS '麻醉合并症名称';
COMMENT ON COLUMN "TB_BA_SSXX"."MZHBZMS" IS '麻醉合并症描述';
COMMENT ON COLUMN "TB_BA_SSXX"."RFSSRQ" IS '入复苏室日期时间';
COMMENT ON COLUMN "TB_BA_SSXX"."CFSSRQ" IS '出复苏室日期时间';
COMMENT ON COLUMN "TB_BA_SSXX"."MZYSXM" IS '麻醉医师姓名';
COMMENT ON COLUMN "TB_BA_SSXX"."MZFJDM" IS '美国麻醉医师协会 (ASA)分级标准代码';
COMMENT ON COLUMN "TB_BA_SSXX"."MZFJMC" IS '美国麻醉医师协会 (ASA)分级标准名称';
COMMENT ON COLUMN "TB_BA_SSXX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_SSXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_SSXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_SSXX"."YLYL2" IS '预留二';
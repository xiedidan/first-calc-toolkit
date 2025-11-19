DROP TABLE IF EXISTS "TB_ZY_SFMXB";
CREATE TABLE "TB_ZY_SFMXB" (
    "YLJGDM" varchar(33),
    "SFMXID" varchar(54),
    "TFBZ" varchar(2),
    "JZLSH" varchar(75),
    "BRZSY" varchar(96),
    "YZMXID" varchar(54),
    "KDKSBM" varchar(54),
    "KDKSMC" varchar(108),
    "KDYSBH" varchar(54),
    "KDYSXM" varchar(108),
    "ZXKSBM" varchar(54),
    "ZXKSMC" varchar(108),
    "ZXRYBH" varchar(54),
    "ZXRYXM" varchar(108),
    "SFXMLBBM" varchar(6),
    "FYSRGLBM" varchar(6),
    "FYFSSJ" timestamp,
    "SFXMBZBM" varchar(3),
    "MXXMBM" varchar(54),
    "MXXMMC" varchar(96),
    "XMFLBM" varchar(48),
    "XMFLMC" varchar(96),
    "MXXMDW" varchar(18),
    "MXXMDJ" numeric(10,4),
    "MXXMSL" numeric(9),
    "MXXMYSJE" numeric(10,4),
    "MXXMSSJE" numeric(10,4),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_SFMXB" IS '住院收费明细表';
COMMENT ON COLUMN "TB_ZY_SFMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."SFMXID" IS '收费明细 ID';
COMMENT ON COLUMN "TB_ZY_SFMXB"."TFBZ" IS '退费标志';
COMMENT ON COLUMN "TB_ZY_SFMXB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_SFMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_SFMXB"."YZMXID" IS '医嘱明细 ID';
COMMENT ON COLUMN "TB_ZY_SFMXB"."KDKSBM" IS '开单科室编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."KDKSMC" IS '开单科室名称';
COMMENT ON COLUMN "TB_ZY_SFMXB"."KDYSBH" IS '开单医生编号';
COMMENT ON COLUMN "TB_ZY_SFMXB"."KDYSXM" IS '开单医生姓名';
COMMENT ON COLUMN "TB_ZY_SFMXB"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_ZY_SFMXB"."ZXRYBH" IS '执行人员编号';
COMMENT ON COLUMN "TB_ZY_SFMXB"."ZXRYXM" IS '执行人员姓名';
COMMENT ON COLUMN "TB_ZY_SFMXB"."SFXMLBBM" IS '收费项目类别编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."FYSRGLBM" IS '费用收入归类编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."FYFSSJ" IS '费用发生时间';
COMMENT ON COLUMN "TB_ZY_SFMXB"."SFXMBZBM" IS '收费项目标准编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMBM" IS '明细项目编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMMC" IS '明细项目名称';
COMMENT ON COLUMN "TB_ZY_SFMXB"."XMFLBM" IS '项目分类编码';
COMMENT ON COLUMN "TB_ZY_SFMXB"."XMFLMC" IS '项目分类名称';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMDW" IS '明细项目单位';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMDJ" IS '明细项目单价';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMSL" IS '明细项目数量';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMYSJE" IS '明细项目应收金额';
COMMENT ON COLUMN "TB_ZY_SFMXB"."MXXMSSJE" IS '明细项目实收金额';
COMMENT ON COLUMN "TB_ZY_SFMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_SFMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_SFMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_SFMXB"."YLYL2" IS '预留二';
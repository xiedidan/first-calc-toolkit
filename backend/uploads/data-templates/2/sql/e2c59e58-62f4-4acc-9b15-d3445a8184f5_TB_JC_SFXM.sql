DROP TABLE IF EXISTS "TB_JC_SFXM";
CREATE TABLE "TB_JC_SFXM" (
    "YLJGDM" varchar(33),
    "XMDM" varchar(48),
    "XMMC" varchar(768),
    "QGYLFWXMBM" varchar(48),
    "QGYLFWXMMC" varchar(383),
    "SFXZXM" varchar(2),
    "XMGG" varchar(96),
    "SFDW" varchar(96),
    "SFDJ" numeric(15,4),
    "SYBZ" varchar(2),
    "TBSM" varchar(1500),
    "XMNH" varchar(1500),
    "CWNR" varchar(1500),
    "BZSM" varchar(750),
    "YN_FL_CODE" varchar(75),
    "SJ_FL_CODE" varchar(75),
    "SY_FL_CODE" varchar(75),
    "KJ_FL_CODE" varchar(75),
    "HS_FL_CODE" varchar(75),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_JC_SFXM" IS '收费项目表';
COMMENT ON COLUMN "TB_JC_SFXM"."YLJGDM" IS '医疗机构组织机构代码';
COMMENT ON COLUMN "TB_JC_SFXM"."XMDM" IS '院内项目代码';
COMMENT ON COLUMN "TB_JC_SFXM"."XMMC" IS '院内项目名称';
COMMENT ON COLUMN "TB_JC_SFXM"."QGYLFWXMBM" IS '医疗服务价格项目编码';
COMMENT ON COLUMN "TB_JC_SFXM"."QGYLFWXMMC" IS '医疗服务价格项目名称';
COMMENT ON COLUMN "TB_JC_SFXM"."SFXZXM" IS '是否院内或地方新增项目';
COMMENT ON COLUMN "TB_JC_SFXM"."XMGG" IS '诊疗项目规格';
COMMENT ON COLUMN "TB_JC_SFXM"."SFDW" IS '收费单位';
COMMENT ON COLUMN "TB_JC_SFXM"."SFDJ" IS '收费单价';
COMMENT ON COLUMN "TB_JC_SFXM"."SYBZ" IS '使用标志';
COMMENT ON COLUMN "TB_JC_SFXM"."TBSM" IS '分类上或使用上的特别说明';
COMMENT ON COLUMN "TB_JC_SFXM"."XMNH" IS '项目内涵';
COMMENT ON COLUMN "TB_JC_SFXM"."CWNR" IS '除外内容';
COMMENT ON COLUMN "TB_JC_SFXM"."BZSM" IS '备注说明';
COMMENT ON COLUMN "TB_JC_SFXM"."YN_FL_CODE" IS '院内费用分类编码';
COMMENT ON COLUMN "TB_JC_SFXM"."SJ_FL_CODE" IS '收据分类编码';
COMMENT ON COLUMN "TB_JC_SFXM"."SY_FL_CODE" IS '首页分类编码';
COMMENT ON COLUMN "TB_JC_SFXM"."KJ_FL_CODE" IS '会计科目分类编码';
COMMENT ON COLUMN "TB_JC_SFXM"."HS_FL_CODE" IS '核算科目分类编码';
COMMENT ON COLUMN "TB_JC_SFXM"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_JC_SFXM"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_JC_SFXM"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_JC_SFXM"."YLYL2" IS '预留二';
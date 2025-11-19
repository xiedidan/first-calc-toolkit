DROP TABLE IF EXISTS "TB_CIS_MJZDZBL";
CREATE TABLE "TB_CIS_MJZDZBL" (
    "YLJGDM" varchar(33),
    "MJZBLLSH" varchar(96),
    "JZLSH" varchar(96),
    "BRZSY" varchar(96),
    "KSBM" varchar(54),
    "KSMC" varchar(108),
    "YSBH" varchar(54),
    "YSXM" varchar(108),
    "XM" varchar(48),
    "XB" varchar(30),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "ZS" varchar(750),
    "XBS" varchar(450),
    "JZLX" varchar(5),
    "JZSJ" timestamp,
    "MJZH" varchar(27),
    "CZBZDM" varchar(2),
    "SFBZ" varchar(2),
    "BMLX" varchar(3),
    "MZZDBM" varchar(750),
    "MZZDMC" varchar(1500),
    "JWBS" varchar(450),
    "GMSBZ" varchar(2),
    "GMS" varchar(1500),
    "GMYDM" varchar(75),
    "CJQKDM" varchar(75),
    "ZZMS" varchar(3000),
    "ZZDM" varchar(75),
    "TGJC" varchar(750),
    "ZYSZGC" varchar(1500),
    "FZJCXM" varchar(1500),
    "FZJCJG" varchar(6000),
    "BZYJ" varchar(1500),
    "FZZF" varchar(150),
    "ZYZDBM" varchar(750),
    "ZYZDMC" varchar(1500),
    "ZYZHDM" varchar(750),
    "ZYZHMC" varchar(1500),
    "CZYJ" varchar(6000),
    "BW" varchar(384),
    "BX" varchar(750),
    "GJ" varchar(750),
    "FJMC" varchar(750),
    "FJZC" varchar(750),
    "YF" varchar(750),
    "SXRQ" timestamp,
    "BLLY" varchar(2),
    "QTYXCZ" varchar(3000),
    "BZ" varchar(750),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_MJZDZBL" IS '门（急）诊电子病历';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."MJZBLLSH" IS '门急诊病历流水号';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."KSBM" IS '科室编码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YSBH" IS '医生编号';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YSXM" IS '医生姓名';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."XM" IS '姓名';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."XB" IS '性别';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."XBS" IS '现病史';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."JZLX" IS '就诊类型';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."JZSJ" IS '就诊时间';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."MJZH" IS '门（急)诊号';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."CZBZDM" IS '初诊标志代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."SFBZ" IS '随访标志';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BMLX" IS '编码类型';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."MZZDBM" IS '门诊诊断编码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."MZZDMC" IS '门诊诊断名称';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."JWBS" IS '既往病史';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."GMSBZ" IS '过敏史标志';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."GMS" IS '过敏史';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."GMYDM" IS '过敏源代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."CJQKDM" IS '残疾情况代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZZMS" IS '症状描述';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZZDM" IS '症状代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."TGJC" IS '体格检查';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZYSZGC" IS '中医“ 四诊 ”观察结果';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."FZJCXM" IS '辅助检查项目';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."FZJCJG" IS '辅助检查结果';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BZYJ" IS '辨证依据';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."FZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZYZDBM" IS '初步诊断--中医病名代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZYZDMC" IS '初步诊断--中医病名名称';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZYZHDM" IS '初步诊断--中医证候代码';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."ZYZHMC" IS '初步诊断--中医证候名称';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."CZYJ" IS '处置意见';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BW" IS '病位';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BX" IS '病性';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."GJ" IS '归经';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."FJMC" IS '方剂名称';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."FJZC" IS '方剂组成（中药）';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YF" IS '用法';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."SXRQ" IS '病历书写日期时间';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BLLY" IS '病历来源';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."QTYXCZ" IS '其他医学处置';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."BZ" IS '说明';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_MJZDZBL"."YLYL2" IS '预留二';
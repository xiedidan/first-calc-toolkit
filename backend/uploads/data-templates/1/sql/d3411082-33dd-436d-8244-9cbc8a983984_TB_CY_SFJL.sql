DROP TABLE IF EXISTS "TB_CY_SFJL";
CREATE TABLE "TB_CY_SFJL" (
    "YLJGDM" varchar(33),
    "SFJLBH" varchar(27),
    "BRZSY" varchar(96),
    "XM" varchar(108),
    "SFZJLBDM" varchar(3),
    "SFJZHM" varchar(75),
    "XBDM" varchar(2),
    "NYS" numeric,
    "NLY" varchar(12),
    "NLXS" varchar(48),
    "SFDH" varchar(30),
    "SFDZXXDZ" varchar(300),
    "SFDZSBM" varchar(30),
    "SFDZSMC" varchar(105),
    "SFDZSHIBM" varchar(30),
    "SFDZSHIMC" varchar(105),
    "SFDZXBM" varchar(30),
    "SFDZXMC" varchar(105),
    "SFDZXZBM" varchar(30),
    "SFDZXZMC" varchar(105),
    "SFDZJCBM" varchar(30),
    "SFDZJCMC" varchar(105),
    "SFDZCLJ" varchar(105),
    "SFDZMPH" varchar(105),
    "CYYLJGMC" varchar(105),
    "CYRQSJ" timestamp,
    "JBRQSJ" timestamp,
    "CYZDMS" varchar(3000),
    "ZZYSXM" varchar(108),
    "JSZTZCBZ" varchar(2),
    "HDZT" varchar(1500),
    "SHNLMS" varchar(1500),
    "YSQKDM" varchar(2),
    "TSYS" varchar(1500),
    "SMQK" varchar(2),
    "SSY" numeric,
    "SZY" numeric,
    "XLL" numeric,
    "XL" varchar(150),
    "ZKZYTJ" varchar(1500),
    "YYYCX" varchar(2),
    "SFPGJJY" varchar(1500),
    "SFZG" varchar(1500),
    "SFRQ" timestamp,
    "SFYYBM" varchar(27),
    "SFYYXM" varchar(108),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CY_SFJL" IS '出院随访记录';
COMMENT ON COLUMN "TB_CY_SFJL"."YLJGDM" IS '随访医疗机构代码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFJLBH" IS '随访记录编号';
COMMENT ON COLUMN "TB_CY_SFJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CY_SFJL"."XM" IS '姓名';
COMMENT ON COLUMN "TB_CY_SFJL"."SFZJLBDM" IS '身份证件类别代码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFJZHM" IS '身份证件号码';
COMMENT ON COLUMN "TB_CY_SFJL"."XBDM" IS '性别代码';
COMMENT ON COLUMN "TB_CY_SFJL"."NYS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CY_SFJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CY_SFJL"."NLXS" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDH" IS '随访电话';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZXXDZ" IS '随访地址详细地址';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZSBM" IS '随访地址-省（自治区、直辖市）编码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZSMC" IS '随访地址-省（自治区、直辖市）名称';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZSHIBM" IS '随访地址-市（地区）编码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZSHIMC" IS '随访地址-市（地区）名称';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZXBM" IS '随访地址-县（区）编码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZXMC" IS '随访地址-县（区）名称';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZXZBM" IS '随访地址-乡（镇、街道）编码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZXZMC" IS '随访地址-乡（镇、街道）名称';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZJCBM" IS '随访地址-(居委会、村)编码';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZJCMC" IS '随访地址-(居委会、村)名称';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZCLJ" IS '随访地址-村（路、街、弄）';
COMMENT ON COLUMN "TB_CY_SFJL"."SFDZMPH" IS '随访地址-门牌号(包括“室”)';
COMMENT ON COLUMN "TB_CY_SFJL"."CYYLJGMC" IS '出院医疗机构名称';
COMMENT ON COLUMN "TB_CY_SFJL"."CYRQSJ" IS '出院日期时间';
COMMENT ON COLUMN "TB_CY_SFJL"."JBRQSJ" IS '接报日期时间';
COMMENT ON COLUMN "TB_CY_SFJL"."CYZDMS" IS '出院诊断描述';
COMMENT ON COLUMN "TB_CY_SFJL"."ZZYSXM" IS '主治医生姓名';
COMMENT ON COLUMN "TB_CY_SFJL"."JSZTZCBZ" IS '精神状态正常标志';
COMMENT ON COLUMN "TB_CY_SFJL"."HDZT" IS '活动状态';
COMMENT ON COLUMN "TB_CY_SFJL"."SHNLMS" IS '生活能力描述';
COMMENT ON COLUMN "TB_CY_SFJL"."YSQKDM" IS '饮食情况代码';
COMMENT ON COLUMN "TB_CY_SFJL"."TSYS" IS '特殊饮食';
COMMENT ON COLUMN "TB_CY_SFJL"."SMQK" IS '睡眠情况';
COMMENT ON COLUMN "TB_CY_SFJL"."SSY" IS '收缩压';
COMMENT ON COLUMN "TB_CY_SFJL"."SZY" IS '舒张压';
COMMENT ON COLUMN "TB_CY_SFJL"."XLL" IS '心率';
COMMENT ON COLUMN "TB_CY_SFJL"."XL" IS '心律';
COMMENT ON COLUMN "TB_CY_SFJL"."ZKZYTJ" IS '专科主要体检';
COMMENT ON COLUMN "TB_CY_SFJL"."YYYCX" IS '用药依从性';
COMMENT ON COLUMN "TB_CY_SFJL"."SFPGJJY" IS '随访评估及建议';
COMMENT ON COLUMN "TB_CY_SFJL"."SFZG" IS '随访转归';
COMMENT ON COLUMN "TB_CY_SFJL"."SFRQ" IS '随访日期';
COMMENT ON COLUMN "TB_CY_SFJL"."SFYYBM" IS '随访医师编号';
COMMENT ON COLUMN "TB_CY_SFJL"."SFYYXM" IS '随访医师姓名';
COMMENT ON COLUMN "TB_CY_SFJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CY_SFJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CY_SFJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CY_SFJL"."YLYL2" IS '预留二';
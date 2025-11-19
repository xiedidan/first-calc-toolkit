DROP TABLE IF EXISTS "TB_HZJBXX";
CREATE TABLE "TB_HZJBXX" (
    "YLJGDM" varchar(33),
    "BRZSY" varchar(96),
    "ZJHM" varchar(27),
    "ZJLX" varchar(3),
    "XB" varchar(2),
    "XM" varchar(108),
    "NLS" varchar(12),
    "NLY" varchar(12),
    "NLT" varchar(24),
    "HZLY" varchar(2),
    "HZLX" varchar(2),
    "HYZK" varchar(3),
    "CSRQ" varchar(12),
    "CSD" varchar(9),
    "MZ" varchar(3),
    "GJ" varchar(15),
    "DHHM" varchar(36),
    "SJHM" varchar(36),
    "GZDWYB" varchar(9),
    "GZDWMC" varchar(192),
    "GZDWDZ" varchar(192),
    "JZDZ" varchar(192),
    "HKD_SHE_NM" varchar(105),
    "HKD_SHI_NM" varchar(105),
    "HKD_XIA_NM" varchar(105),
    "HKD_XNG_NM" varchar(105),
    "HKD_VLG_NM" varchar(105),
    "HKD_CUN" varchar(105),
    "HKD_MPH" varchar(105),
    "HKDZYB" varchar(9),
    "LXRXM" varchar(108),
    "LXRGX" varchar(6),
    "LXRDZ" varchar(192),
    "LXRYB" varchar(9),
    "LXRDH" varchar(36),
    "CJGZRQ" timestamp,
    "DZYJDZ" varchar(60),
    "LXDH_LBDM" varchar(3),
    "LXDH_LB" varchar(30),
    "XGBZ" varchar(2),
    "TBRQ" timestamp,
    "YYDAH" varchar(96),
    "JKKH" varchar(30),
    "YBKKH" varchar(45),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_HZJBXX" IS '患者基本信息';
COMMENT ON COLUMN "TB_HZJBXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_HZJBXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_HZJBXX"."ZJHM" IS '证件号码';
COMMENT ON COLUMN "TB_HZJBXX"."ZJLX" IS '证件类型';
COMMENT ON COLUMN "TB_HZJBXX"."XB" IS '性别';
COMMENT ON COLUMN "TB_HZJBXX"."XM" IS '姓名';
COMMENT ON COLUMN "TB_HZJBXX"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_HZJBXX"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_HZJBXX"."NLT" IS '年龄（天）';
COMMENT ON COLUMN "TB_HZJBXX"."HZLY" IS '患者来源';
COMMENT ON COLUMN "TB_HZJBXX"."HZLX" IS '患者类型';
COMMENT ON COLUMN "TB_HZJBXX"."HYZK" IS '婚姻状况';
COMMENT ON COLUMN "TB_HZJBXX"."CSRQ" IS '出生日期';
COMMENT ON COLUMN "TB_HZJBXX"."CSD" IS '出生地';
COMMENT ON COLUMN "TB_HZJBXX"."MZ" IS '民族';
COMMENT ON COLUMN "TB_HZJBXX"."GJ" IS '国籍';
COMMENT ON COLUMN "TB_HZJBXX"."DHHM" IS '电话号码';
COMMENT ON COLUMN "TB_HZJBXX"."SJHM" IS '手机号码';
COMMENT ON COLUMN "TB_HZJBXX"."GZDWYB" IS '工作单位邮编';
COMMENT ON COLUMN "TB_HZJBXX"."GZDWMC" IS '工作单位名称';
COMMENT ON COLUMN "TB_HZJBXX"."GZDWDZ" IS '工作单位地址';
COMMENT ON COLUMN "TB_HZJBXX"."JZDZ" IS '居住地址';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_SHE_NM" IS '户口地-省（自治区 、 直辖市 ） 名称';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_SHI_NM" IS '户口地-市（地区）名称';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_XIA_NM" IS '户口地-县（区）名称';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_XNG_NM" IS '户口地-乡（镇、街道）名称';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_VLG_NM" IS '户口地-(居委会、村)名称';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_CUN" IS '户口地-村（路、街、弄）';
COMMENT ON COLUMN "TB_HZJBXX"."HKD_MPH" IS '户口地-门牌号(包括“室”)';
COMMENT ON COLUMN "TB_HZJBXX"."HKDZYB" IS '户口地址邮编';
COMMENT ON COLUMN "TB_HZJBXX"."LXRXM" IS '联系人姓名';
COMMENT ON COLUMN "TB_HZJBXX"."LXRGX" IS '联系人关系';
COMMENT ON COLUMN "TB_HZJBXX"."LXRDZ" IS '联系人地址';
COMMENT ON COLUMN "TB_HZJBXX"."LXRYB" IS '联系人邮编';
COMMENT ON COLUMN "TB_HZJBXX"."LXRDH" IS '联系人电话';
COMMENT ON COLUMN "TB_HZJBXX"."CJGZRQ" IS '参加工作日期';
COMMENT ON COLUMN "TB_HZJBXX"."DZYJDZ" IS '电子邮件地址';
COMMENT ON COLUMN "TB_HZJBXX"."LXDH_LBDM" IS '联系电话-类别代码';
COMMENT ON COLUMN "TB_HZJBXX"."LXDH_LB" IS '联系电话-类别';
COMMENT ON COLUMN "TB_HZJBXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_HZJBXX"."TBRQ" IS '数据生成时间';
COMMENT ON COLUMN "TB_HZJBXX"."YYDAH" IS '医疗机构内部档案号';
COMMENT ON COLUMN "TB_HZJBXX"."JKKH" IS '健康卡号';
COMMENT ON COLUMN "TB_HZJBXX"."YBKKH" IS '医保卡号';
COMMENT ON COLUMN "TB_HZJBXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_HZJBXX"."YLYL2" IS '预留二';
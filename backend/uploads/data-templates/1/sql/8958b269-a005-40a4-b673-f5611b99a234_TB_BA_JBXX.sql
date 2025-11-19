DROP TABLE IF EXISTS "TB_BA_JBXX";
CREATE TABLE "TB_BA_JBXX" (
    "YLJGDM" varchar(33),
    "JZLSH" varchar(75),
    "BRZSY" varchar(96),
    "ZYBABZ" varchar(2),
    "SJLY" varchar(2),
    "NDJD" varchar(30),
    "YXQZ" varchar(30),
    "RYLX" varchar(3),
    "RYLXMC" varchar(45),
    "ZLLB" varchar(3),
    "ZLLBMC" varchar(15),
    "BXLX" varchar(30),
    "JKKH" varchar(30),
    "YLFFFS" varchar(6),
    "ZYCS" numeric,
    "BAH" varchar(48),
    "XM" varchar(108),
    "XB" varchar(2),
    "XBMC" varchar(30),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "CH" varchar(24),
    "CSNY" varchar(12),
    "XSECSTZ" numeric,
    "XSERYTZ" numeric,
    "HYZK" varchar(3),
    "MZ" varchar(3),
    "GJ" varchar(48),
    "JG" varchar(24),
    "HYZKMC" varchar(30),
    "MZMC" varchar(45),
    "GJDM" varchar(5),
    "JGDM" varchar(3),
    "CSD" varchar(30),
    "XSE_XB" varchar(2),
    "XSE_TZ" numeric,
    "SFZ" varchar(27),
    "LXDH" varchar(30),
    "GZDW" varchar(48),
    "GZDWDH" varchar(24),
    "GZDWYB" varchar(9),
    "ZYLBDM" varchar(9),
    "ZYMC" varchar(300),
    "JZD" varchar(300),
    "JZD_SSBM" varchar(30),
    "JZD_SSMC" varchar(105),
    "JZD_SBM" varchar(30),
    "JZD_SMC" varchar(105),
    "JZD_XBM" varchar(30),
    "JZD_XMC" varchar(105),
    "JZD_XZBM" varchar(30),
    "JZD_XZMC" varchar(105),
    "JZD_JWHBM" varchar(30),
    "JZD_JWHMC" varchar(105),
    "JZD_CDZ" varchar(105),
    "JZD_MPH" varchar(105),
    "HKD_SSBM" varchar(30),
    "HKD_SSMC" varchar(105),
    "HKD_SBM" varchar(30),
    "HKD_SMC" varchar(105),
    "HKD_XBM" varchar(30),
    "HKD_XMC" varchar(105),
    "HKD_XZBM" varchar(30),
    "HKD_XZMC" varchar(105),
    "HKD_JWHBM" varchar(30),
    "HKD_JWHMC" varchar(105),
    "HKD_CDZ" varchar(105),
    "HKD_MPH" varchar(105),
    "XZZDH" varchar(24),
    "XZZYB" varchar(9),
    "HKDZ" varchar(75),
    "HKDH" varchar(48),
    "HKYB" varchar(9),
    "LXRXM" varchar(108),
    "LXRGX" varchar(6),
    "LXRDZ" varchar(192),
    "LXRDH" varchar(30),
    "RYSJ" timestamp,
    "RYKSBM" varchar(30),
    "RYKSMC" varchar(30),
    "RYBQ" varchar(48),
    "ZKKSBM1" varchar(30),
    "ZKKSBM2" varchar(30),
    "ZKKSBM3" varchar(30),
    "SZBQMC" varchar(192),
    "CYSJ" timestamp,
    "CYKSBM" varchar(30),
    "CYKSMC" varchar(75),
    "CYBQ" varchar(48),
    "SJZYTS" numeric,
    "MJZZDBM" varchar(30),
    "MJZZDMC" varchar(150),
    "CYFSDM" varchar(2),
    "RYSQKDM" varchar(2),
    "WYZZBZ" varchar(2),
    "ZYZDQZRQ" timestamp,
    "ZYQJSFGZBWHBZ" varchar(2),
    "BZ" varchar(384),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_JBXX" IS '住院病案基本信息';
COMMENT ON COLUMN "TB_BA_JBXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_JBXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYBABZ" IS '中医病案首页标志';
COMMENT ON COLUMN "TB_BA_JBXX"."SJLY" IS '数据来源';
COMMENT ON COLUMN "TB_BA_JBXX"."NDJD" IS '年度季度';
COMMENT ON COLUMN "TB_BA_JBXX"."YXQZ" IS '有效期至';
COMMENT ON COLUMN "TB_BA_JBXX"."RYLX" IS '入院类型（途径）代码';
COMMENT ON COLUMN "TB_BA_JBXX"."RYLXMC" IS '入院类型（途径）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."ZLLB" IS '治疗类别';
COMMENT ON COLUMN "TB_BA_JBXX"."ZLLBMC" IS '治疗类别名称';
COMMENT ON COLUMN "TB_BA_JBXX"."BXLX" IS '保险类型';
COMMENT ON COLUMN "TB_BA_JBXX"."JKKH" IS '健康卡号';
COMMENT ON COLUMN "TB_BA_JBXX"."YLFFFS" IS '医疗付费方式';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYCS" IS '住院次数';
COMMENT ON COLUMN "TB_BA_JBXX"."BAH" IS '病案号';
COMMENT ON COLUMN "TB_BA_JBXX"."XM" IS '姓名';
COMMENT ON COLUMN "TB_BA_JBXX"."XB" IS '性别代码';
COMMENT ON COLUMN "TB_BA_JBXX"."XBMC" IS '性别名称';
COMMENT ON COLUMN "TB_BA_JBXX"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_BA_JBXX"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_BA_JBXX"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_BA_JBXX"."CH" IS '床号';
COMMENT ON COLUMN "TB_BA_JBXX"."CSNY" IS '出生日期';
COMMENT ON COLUMN "TB_BA_JBXX"."XSECSTZ" IS '新生儿出生体重';
COMMENT ON COLUMN "TB_BA_JBXX"."XSERYTZ" IS '新生儿入院体重';
COMMENT ON COLUMN "TB_BA_JBXX"."HYZK" IS '婚姻状况';
COMMENT ON COLUMN "TB_BA_JBXX"."MZ" IS '民族';
COMMENT ON COLUMN "TB_BA_JBXX"."GJ" IS '国籍';
COMMENT ON COLUMN "TB_BA_JBXX"."JG" IS '籍贯';
COMMENT ON COLUMN "TB_BA_JBXX"."HYZKMC" IS '婚姻状况名称';
COMMENT ON COLUMN "TB_BA_JBXX"."MZMC" IS '民族名称';
COMMENT ON COLUMN "TB_BA_JBXX"."GJDM" IS '国籍代码';
COMMENT ON COLUMN "TB_BA_JBXX"."JGDM" IS '籍贯代码';
COMMENT ON COLUMN "TB_BA_JBXX"."CSD" IS '出生地';
COMMENT ON COLUMN "TB_BA_JBXX"."XSE_XB" IS '新生儿性别';
COMMENT ON COLUMN "TB_BA_JBXX"."XSE_TZ" IS '新生儿体重';
COMMENT ON COLUMN "TB_BA_JBXX"."SFZ" IS '身份证号';
COMMENT ON COLUMN "TB_BA_JBXX"."LXDH" IS '联系电话';
COMMENT ON COLUMN "TB_BA_JBXX"."GZDW" IS '工作单位及地址';
COMMENT ON COLUMN "TB_BA_JBXX"."GZDWDH" IS '工作单位电话';
COMMENT ON COLUMN "TB_BA_JBXX"."GZDWYB" IS '工作单位邮编';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYLBDM" IS '职业类别代码';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYMC" IS '职业名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD" IS '居住地（现住址，长地址）';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_SSBM" IS '居住地-省（ 自治区、直辖市）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_SSMC" IS '居住地-省（自治区、直辖市）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_SBM" IS '居住地-市（地区）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_SMC" IS '居住地-市（地区）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_XBM" IS '居住地-县（区）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_XMC" IS '居住地-县（区）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_XZBM" IS '居住地-乡（镇、街道）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_XZMC" IS '居住地-乡（镇、街道）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_JWHBM" IS '居住地-(居委会、村)编码';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_JWHMC" IS '居住地-(居委会、村)名称';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_CDZ" IS '居住地-村（路、街）';
COMMENT ON COLUMN "TB_BA_JBXX"."JZD_MPH" IS '居住地-门牌号(包括“室”)';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_SSBM" IS '户 口地-省（自治区、直辖市）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_SSMC" IS '户 口地-省（自治区、直辖市）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_SBM" IS '户口地-市（地区）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_SMC" IS '户口地-市（地区）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_XBM" IS '户口地-县（区）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_XMC" IS '户口地-县（区）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_XZBM" IS '户口地-乡（镇、街道）编码';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_XZMC" IS '户口地-乡（镇、街道）名称';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_JWHBM" IS '户口地-(居委会、村)编码';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_JWHMC" IS '户口地-(居委会、村)名称';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_CDZ" IS '户口地-村（路、街）';
COMMENT ON COLUMN "TB_BA_JBXX"."HKD_MPH" IS '户口地-门牌号(包括“室”)';
COMMENT ON COLUMN "TB_BA_JBXX"."XZZDH" IS '现住址电话';
COMMENT ON COLUMN "TB_BA_JBXX"."XZZYB" IS '现住址邮编';
COMMENT ON COLUMN "TB_BA_JBXX"."HKDZ" IS '户口地址';
COMMENT ON COLUMN "TB_BA_JBXX"."HKDH" IS '户口电话';
COMMENT ON COLUMN "TB_BA_JBXX"."HKYB" IS '户口邮编';
COMMENT ON COLUMN "TB_BA_JBXX"."LXRXM" IS '联系人姓名';
COMMENT ON COLUMN "TB_BA_JBXX"."LXRGX" IS '联系人关系';
COMMENT ON COLUMN "TB_BA_JBXX"."LXRDZ" IS '联系人地址';
COMMENT ON COLUMN "TB_BA_JBXX"."LXRDH" IS '联系人电话';
COMMENT ON COLUMN "TB_BA_JBXX"."RYSJ" IS '入院时间';
COMMENT ON COLUMN "TB_BA_JBXX"."RYKSBM" IS '入院科室编码';
COMMENT ON COLUMN "TB_BA_JBXX"."RYKSMC" IS '入院科室名称';
COMMENT ON COLUMN "TB_BA_JBXX"."RYBQ" IS '入院病区（房）';
COMMENT ON COLUMN "TB_BA_JBXX"."ZKKSBM1" IS '转科科室编码 1';
COMMENT ON COLUMN "TB_BA_JBXX"."ZKKSBM2" IS '转科科室编码 2';
COMMENT ON COLUMN "TB_BA_JBXX"."ZKKSBM3" IS '转科科室编码 3';
COMMENT ON COLUMN "TB_BA_JBXX"."SZBQMC" IS '所转病区名称';
COMMENT ON COLUMN "TB_BA_JBXX"."CYSJ" IS '出院时间';
COMMENT ON COLUMN "TB_BA_JBXX"."CYKSBM" IS '出院科室编码';
COMMENT ON COLUMN "TB_BA_JBXX"."CYKSMC" IS '出院科室名称';
COMMENT ON COLUMN "TB_BA_JBXX"."CYBQ" IS '出院病区（房）';
COMMENT ON COLUMN "TB_BA_JBXX"."SJZYTS" IS '实际住院天数';
COMMENT ON COLUMN "TB_BA_JBXX"."MJZZDBM" IS '门（急）诊诊断编码';
COMMENT ON COLUMN "TB_BA_JBXX"."MJZZDMC" IS '门（急）诊诊断名称';
COMMENT ON COLUMN "TB_BA_JBXX"."CYFSDM" IS '出院方式代码';
COMMENT ON COLUMN "TB_BA_JBXX"."RYSQKDM" IS '入院时情况代码';
COMMENT ON COLUMN "TB_BA_JBXX"."WYZZBZ" IS '入院前经外院诊治标志';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYZDQZRQ" IS '主要诊断确诊日期';
COMMENT ON COLUMN "TB_BA_JBXX"."ZYQJSFGZBWHBZ" IS '住院期间是否告知病危或病重';
COMMENT ON COLUMN "TB_BA_JBXX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_BA_JBXX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_JBXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_JBXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_JBXX"."YLYL2" IS '预留二';
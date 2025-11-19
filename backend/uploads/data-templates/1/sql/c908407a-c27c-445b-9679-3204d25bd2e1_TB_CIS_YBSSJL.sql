DROP TABLE IF EXISTS "TB_CIS_YBSSJL";
CREATE TABLE "TB_CIS_YBSSJL" (
    "YLJGDM" varchar(33),
    "SSMXLSH" varchar(75),
    "BRZSY" varchar(96),
    "ZYYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "XM" varchar(108),
    "XBDM" varchar(2),
    "XBMC" varchar(30),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "MZZYH" varchar(27),
    "JZLX" varchar(5),
    "JZLSH" varchar(96),
    "MZZYBZ" varchar(2),
    "SSJCZBM" varchar(75),
    "SSJCZMC" varchar(120),
    "SSQZDBM" varchar(750),
    "SSQZDMC" varchar(1500),
    "SSHZDBM" varchar(750),
    "SSHZDMC" varchar(1500),
    "SSQSSJ" timestamp,
    "SSJSSJ" timestamp,
    "SSJBDM" varchar(3),
    "SSJBMC" varchar(30),
    "SSYSGH" varchar(54),
    "SSYSXM" varchar(108),
    "SSYSYZGH" varchar(54),
    "SSYSYZXM" varchar(108),
    "SSYSEZGH" varchar(54),
    "SSYSEZXM" varchar(108),
    "MZYSGH" varchar(54),
    "MZYSXM" varchar(108),
    "MZFFDM" varchar(30),
    "MZFFMC" varchar(150),
    "DZSQDBH" varchar(30),
    "JZKSMC" varchar(108),
    "JZKSDM" varchar(54),
    "BQDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "SSJBH" varchar(15),
    "JRWMC" varchar(150),
    "SSTWDM" varchar(30),
    "PFXDMS" varchar(300),
    "SSGCMS" varchar(3000),
    "SSSSJCZDXX" varchar(1500),
    "SSSBZ" varchar(2),
    "SSQKMS" varchar(300),
    "CXL" numeric,
    "SYL" numeric,
    "SXL" numeric,
    "NL" numeric,
    "SQYY" varchar(150),
    "SZYY" varchar(150),
    "SXFYBZ" varchar(2),
    "QXHSXM" varchar(108),
    "QXHSGH" varchar(54),
    "XTHSXM" varchar(108),
    "XTHSGH" varchar(54),
    "SSJCZMBBWMC" varchar(75),
    "SSJCZMBBWDM" varchar(3),
    "YLBZ" varchar(2),
    "YLCLMC" varchar(300),
    "YLCLSM" varchar(300),
    "FZBW" varchar(75),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_YBSSJL" IS '一般手术记录';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSMXLSH" IS '手术明细流水号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XM" IS '患者姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XBDM" IS '性别代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XBMC" IS '性别名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZZYH" IS '门诊/住院号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."JZLX" IS '就诊类型';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJCZBM" IS '手术及操作编码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJCZMC" IS '手术及操作名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSQZDBM" IS '手术前诊断编码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSQZDMC" IS '手术前诊断名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSHZDBM" IS '手术后诊断编码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSHZDMC" IS '手术后诊断名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSQSSJ" IS '手术起始时间';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJSSJ" IS '手术结束时间';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJBDM" IS '手术级别代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJBMC" IS '手术级别名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSGH" IS '手术医生工号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSXM" IS '手术医生姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSYZGH" IS '手术医生 I 助工号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSYZXM" IS '手术医生 I 助姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSEZGH" IS '手术医生 II 助工号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSYSEZXM" IS '手术医生 II 助姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZYSGH" IS '麻醉医师编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZYSXM" IS '麻醉医师姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZFFDM" IS '麻醉方法代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."MZFFMC" IS '麻醉方法名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."DZSQDBH" IS '电子申请单编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."JZKSMC" IS '就诊科室名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."JZKSDM" IS '就诊科室代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BQDM" IS '病区代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJBH" IS '手术间编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."JRWMC" IS '介入物名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSTWDM" IS '手术体位代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."PFXDMS" IS '皮肤消毒描述';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSGCMS" IS '手术过程描述';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSSSJCZDXX" IS '实施手术及操作的详细描述';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSSBZ" IS '手术史标志';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSQKMS" IS '手术切口描述';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."CXL" IS '出血量（mL)';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SYL" IS '输液量(mL)';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SXL" IS '输血量(mL)';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."NL" IS '尿量(mL)';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SQYY" IS '术前用药';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SZYY" IS '术中用药';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SXFYBZ" IS '输血反应标志';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."QXHSXM" IS '器械护士姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."QXHSGH" IS '器械护士编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XTHSXM" IS '巡台护士姓名';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XTHSGH" IS '巡台护士编号';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJCZMBBWMC" IS '手术及操作目标部位名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."SSJCZMBBWDM" IS '手术及操作目标部位代码';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLBZ" IS '引流标志';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLCLMC" IS '引流材料名称';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLCLSM" IS '引流材料数目';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."FZBW" IS '放置部位';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_YBSSJL"."YLYL2" IS '预留二';
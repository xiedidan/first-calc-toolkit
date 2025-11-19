DROP TABLE IF EXISTS "TB_LIS_Report";
CREATE TABLE "TB_LIS_Report" (
    "YLJGDM" varchar(33),
    "BGDH" varchar(96),
    "BGRQ" timestamp,
    "JZLSH" varchar(75),
    "MZZYBZ" varchar(3),
    "BRZSY" varchar(96),
    "MJZH" varchar(54),
    "ZYH" varchar(54),
    "HZLXDM" varchar(2),
    "BRXM" varchar(108),
    "BRXB" varchar(2),
    "BRNL" varchar(24),
    "SQRGH" varchar(54),
    "SQRXM" varchar(108),
    "SQRSFZHM" varchar(27),
    "SQDBH" varchar(30),
    "SQJGDM" varchar(33),
    "SQJGMC" varchar(105),
    "SQKS" varchar(96),
    "SQKSMC" varchar(114),
    "HZKSDM" varchar(54),
    "HZKSMC" varchar(75),
    "BQ" varchar(48),
    "CH" varchar(30),
    "CJRQ" timestamp,
    "JYRQ" timestamp,
    "XYZDDM" varchar(750),
    "XYZDMC" varchar(1500),
    "ZDJGDM" varchar(33),
    "ZDJGMC" varchar(105),
    "ZDRQ" timestamp,
    "JYXMDM" varchar(1500),
    "JYXMMC" varchar(3000),
    "JYJSBM" varchar(30),
    "JYJSXM" varchar(108),
    "JYJSSFZH" varchar(27),
    "JYKSBM" varchar(30),
    "BGKSMC" varchar(75),
    "BGBZ" varchar(1536),
    "BGRGH" varchar(54),
    "BGRXM" varchar(108),
    "BGYSSFZHM" varchar(27),
    "SHRGH" varchar(54),
    "SHRXM" varchar(108),
    "SHYSSFZHM" varchar(27),
    "DYRQ" timestamp,
    "SQRQ" timestamp,
    "JCFY" numeric(12,4),
    "BBDM" varchar(6),
    "BBMC" varchar(96),
    "BGDLBBM" varchar(6),
    "BGDLB" varchar(384),
    "WJLJ" varchar(384),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_LIS_Report" IS '实验室检验报告表头';
COMMENT ON COLUMN "TB_LIS_Report"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_LIS_Report"."BGDH" IS '检验报告单号';
COMMENT ON COLUMN "TB_LIS_Report"."BGRQ" IS '检验报告日期';
COMMENT ON COLUMN "TB_LIS_Report"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_LIS_Report"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_LIS_Report"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_LIS_Report"."MJZH" IS '门（急）诊号';
COMMENT ON COLUMN "TB_LIS_Report"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_LIS_Report"."HZLXDM" IS '患者类型代码';
COMMENT ON COLUMN "TB_LIS_Report"."BRXM" IS '病人姓名';
COMMENT ON COLUMN "TB_LIS_Report"."BRXB" IS '性别';
COMMENT ON COLUMN "TB_LIS_Report"."BRNL" IS '年龄';
COMMENT ON COLUMN "TB_LIS_Report"."SQRGH" IS '申请人编号';
COMMENT ON COLUMN "TB_LIS_Report"."SQRXM" IS '申请人姓名';
COMMENT ON COLUMN "TB_LIS_Report"."SQRSFZHM" IS '申请人身份证号码';
COMMENT ON COLUMN "TB_LIS_Report"."SQDBH" IS '申请单编号';
COMMENT ON COLUMN "TB_LIS_Report"."SQJGDM" IS '申请机构代码';
COMMENT ON COLUMN "TB_LIS_Report"."SQJGMC" IS '申请机构名称';
COMMENT ON COLUMN "TB_LIS_Report"."SQKS" IS '申请科室编码';
COMMENT ON COLUMN "TB_LIS_Report"."SQKSMC" IS '申请科室名称';
COMMENT ON COLUMN "TB_LIS_Report"."HZKSDM" IS '患者科室代码';
COMMENT ON COLUMN "TB_LIS_Report"."HZKSMC" IS '患者科室名称';
COMMENT ON COLUMN "TB_LIS_Report"."BQ" IS '患者病区';
COMMENT ON COLUMN "TB_LIS_Report"."CH" IS '患者床号';
COMMENT ON COLUMN "TB_LIS_Report"."CJRQ" IS '采集日期';
COMMENT ON COLUMN "TB_LIS_Report"."JYRQ" IS '检验日期';
COMMENT ON COLUMN "TB_LIS_Report"."XYZDDM" IS '西医诊断代码';
COMMENT ON COLUMN "TB_LIS_Report"."XYZDMC" IS '西医诊断名称';
COMMENT ON COLUMN "TB_LIS_Report"."ZDJGDM" IS '诊断机构代码';
COMMENT ON COLUMN "TB_LIS_Report"."ZDJGMC" IS '诊断机构名称';
COMMENT ON COLUMN "TB_LIS_Report"."ZDRQ" IS '诊断日期';
COMMENT ON COLUMN "TB_LIS_Report"."JYXMDM" IS '检验项目代码';
COMMENT ON COLUMN "TB_LIS_Report"."JYXMMC" IS '检验项目名称';
COMMENT ON COLUMN "TB_LIS_Report"."JYJSBM" IS '检验技师编码';
COMMENT ON COLUMN "TB_LIS_Report"."JYJSXM" IS '检验技师姓名';
COMMENT ON COLUMN "TB_LIS_Report"."JYJSSFZH" IS '检验技师身份证号';
COMMENT ON COLUMN "TB_LIS_Report"."JYKSBM" IS '报告科室编码';
COMMENT ON COLUMN "TB_LIS_Report"."BGKSMC" IS '报告科室名称';
COMMENT ON COLUMN "TB_LIS_Report"."BGBZ" IS '报告备注';
COMMENT ON COLUMN "TB_LIS_Report"."BGRGH" IS '报告人编号';
COMMENT ON COLUMN "TB_LIS_Report"."BGRXM" IS '报告人姓名';
COMMENT ON COLUMN "TB_LIS_Report"."BGYSSFZHM" IS '报告医师身份证号码';
COMMENT ON COLUMN "TB_LIS_Report"."SHRGH" IS '审核人编号';
COMMENT ON COLUMN "TB_LIS_Report"."SHRXM" IS '审核人姓名';
COMMENT ON COLUMN "TB_LIS_Report"."SHYSSFZHM" IS '审核医师身份证号码';
COMMENT ON COLUMN "TB_LIS_Report"."DYRQ" IS '打印日期';
COMMENT ON COLUMN "TB_LIS_Report"."SQRQ" IS '申请日期';
COMMENT ON COLUMN "TB_LIS_Report"."JCFY" IS '检查费用';
COMMENT ON COLUMN "TB_LIS_Report"."BBDM" IS '标本代码';
COMMENT ON COLUMN "TB_LIS_Report"."BBMC" IS '标本名称';
COMMENT ON COLUMN "TB_LIS_Report"."BGDLBBM" IS '报告单类别编码';
COMMENT ON COLUMN "TB_LIS_Report"."BGDLB" IS '报告单类别名称';
COMMENT ON COLUMN "TB_LIS_Report"."WJLJ" IS '文件链接';
COMMENT ON COLUMN "TB_LIS_Report"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_LIS_Report"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_LIS_Report"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_LIS_Report"."YLYL2" IS '预留二';
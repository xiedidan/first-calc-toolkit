DROP TABLE IF EXISTS "TB_RIS_Report";
CREATE TABLE "TB_RIS_Report" (
    "YLJGDM" varchar(33),
    "JCWYID" varchar(768),
    "SQDH" varchar(96),
    "PICID" varchar(768),
    "STUDYUID" varchar(768),
    "JZLSH" varchar(75),
    "MZZYBZ" varchar(3),
    "ZYH" varchar(54),
    "HZLXDM" varchar(2),
    "MJZH" varchar(54),
    "BRZSY" varchar(96),
    "BRXM" varchar(108),
    "BRXB" varchar(2),
    "HZKSDM" varchar(54),
    "HZKSMC" varchar(75),
    "HZBQMC" varchar(75),
    "HZBFH" varchar(45),
    "BZBCH" varchar(15),
    "JCXMDM" varchar(300),
    "JCXMMC" varchar(600),
    "KDSJ" timestamp,
    "JYSJ" timestamp,
    "ExamType" varchar(24),
    "SBBM" varchar(96),
    "YQBM" varchar(96),
    "SQJGDM" varchar(33),
    "SQJGMC" varchar(150),
    "SQKS" varchar(96),
    "SQKSMC" varchar(114),
    "SQRGH" varchar(54),
    "SQRXM" varchar(108),
    "SQRSFZHM" varchar(27),
    "XYZDDM" varchar(750),
    "XYZDMC" varchar(1500),
    "ZDJGDM" varchar(33),
    "ZDJGMC" varchar(150),
    "ZDRQ" timestamp,
    "HZZS" varchar(150),
    "ZZMS" varchar(1500),
    "CZBM" varchar(150),
    "CZMC" varchar(150),
    "CZBWDM" varchar(6),
    "JRWMC" varchar(150),
    "CZCS" numeric,
    "CARQSJ" timestamp,
    "MZFFDM" varchar(3),
    "MZGCJG" varchar(1500),
    "MZZYBSDM" varchar(2),
    "MZYSBM" varchar(150),
    "MZYSXM" varchar(108),
    "JCBGDBH" varchar(150),
    "JCKS" varchar(96),
    "JCKSMC" varchar(114),
    "JCYS" varchar(108),
    "JCYSGH" varchar(54),
    "JCYSSFZHM" varchar(27),
    "BGRQ" timestamp,
    "BGSJ" timestamp,
    "BGRGH" varchar(54),
    "BGRXM" varchar(108),
    "BGYSSFZHM" varchar(27),
    "SHRGH" varchar(54),
    "SHRXM" varchar(108),
    "SHYSSFZHM" varchar(27),
    "JCBW" varchar(300),
    "BWACR" varchar(48),
    "YYS" varchar(2),
    "JCJGDM" varchar(2),
    "BGLCZD" varchar(768),
    "JCFY" numeric,
    "YXBX" varchar(6000),
    "YXZD" varchar(6000),
    "BZHJY" varchar(768),
    "SFYYY" varchar(2),
    "WJZBS" varchar(2),
    "WJZBGRQ" timestamp,
    "JLDW" varchar(30),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_RIS_Report" IS '医学影像检查报告表';
COMMENT ON COLUMN "TB_RIS_Report"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_RIS_Report"."JCWYID" IS '检查唯一 ID';
COMMENT ON COLUMN "TB_RIS_Report"."SQDH" IS '申请单号';
COMMENT ON COLUMN "TB_RIS_Report"."PICID" IS '影像号';
COMMENT ON COLUMN "TB_RIS_Report"."STUDYUID" IS '检查号';
COMMENT ON COLUMN "TB_RIS_Report"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_RIS_Report"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_RIS_Report"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_RIS_Report"."HZLXDM" IS '患者类型代码';
COMMENT ON COLUMN "TB_RIS_Report"."MJZH" IS '门（急）诊号';
COMMENT ON COLUMN "TB_RIS_Report"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_RIS_Report"."BRXM" IS '病人姓名';
COMMENT ON COLUMN "TB_RIS_Report"."BRXB" IS '病人性别';
COMMENT ON COLUMN "TB_RIS_Report"."HZKSDM" IS '患者科室代码';
COMMENT ON COLUMN "TB_RIS_Report"."HZKSMC" IS '患者科室名称';
COMMENT ON COLUMN "TB_RIS_Report"."HZBQMC" IS '患者病区名称';
COMMENT ON COLUMN "TB_RIS_Report"."HZBFH" IS '患者病房号';
COMMENT ON COLUMN "TB_RIS_Report"."BZBCH" IS '患者病床号';
COMMENT ON COLUMN "TB_RIS_Report"."JCXMDM" IS '检查项目代码';
COMMENT ON COLUMN "TB_RIS_Report"."JCXMMC" IS '检查项目名称';
COMMENT ON COLUMN "TB_RIS_Report"."KDSJ" IS '开单时间';
COMMENT ON COLUMN "TB_RIS_Report"."JYSJ" IS '检查时间';
COMMENT ON COLUMN "TB_RIS_Report"."ExamType" IS '检查类型';
COMMENT ON COLUMN "TB_RIS_Report"."SBBM" IS '检查设备仪器型号';
COMMENT ON COLUMN "TB_RIS_Report"."YQBM" IS '检查仪器号';
COMMENT ON COLUMN "TB_RIS_Report"."SQJGDM" IS '申请机构代码';
COMMENT ON COLUMN "TB_RIS_Report"."SQJGMC" IS '申请机构名称';
COMMENT ON COLUMN "TB_RIS_Report"."SQKS" IS '申请科室编码';
COMMENT ON COLUMN "TB_RIS_Report"."SQKSMC" IS '申请科室名称';
COMMENT ON COLUMN "TB_RIS_Report"."SQRGH" IS '申请人编号';
COMMENT ON COLUMN "TB_RIS_Report"."SQRXM" IS '申请人姓名';
COMMENT ON COLUMN "TB_RIS_Report"."SQRSFZHM" IS '申请人身份证号码';
COMMENT ON COLUMN "TB_RIS_Report"."XYZDDM" IS '西医诊断代码';
COMMENT ON COLUMN "TB_RIS_Report"."XYZDMC" IS '西医诊断名称';
COMMENT ON COLUMN "TB_RIS_Report"."ZDJGDM" IS '诊断机构代码';
COMMENT ON COLUMN "TB_RIS_Report"."ZDJGMC" IS '诊断机构名称';
COMMENT ON COLUMN "TB_RIS_Report"."ZDRQ" IS '诊断日期';
COMMENT ON COLUMN "TB_RIS_Report"."HZZS" IS '患者主诉';
COMMENT ON COLUMN "TB_RIS_Report"."ZZMS" IS '症状描述';
COMMENT ON COLUMN "TB_RIS_Report"."CZBM" IS '操作编码';
COMMENT ON COLUMN "TB_RIS_Report"."CZMC" IS '操作名称';
COMMENT ON COLUMN "TB_RIS_Report"."CZBWDM" IS '操作部位代码';
COMMENT ON COLUMN "TB_RIS_Report"."JRWMC" IS '介入物名称';
COMMENT ON COLUMN "TB_RIS_Report"."CZCS" IS '操作次数';
COMMENT ON COLUMN "TB_RIS_Report"."CARQSJ" IS '操作日期时间';
COMMENT ON COLUMN "TB_RIS_Report"."MZFFDM" IS '麻醉方法代码';
COMMENT ON COLUMN "TB_RIS_Report"."MZGCJG" IS '麻醉观察结果';
COMMENT ON COLUMN "TB_RIS_Report"."MZZYBSDM" IS '麻醉中医标识代码';
COMMENT ON COLUMN "TB_RIS_Report"."MZYSBM" IS '麻醉医生编码';
COMMENT ON COLUMN "TB_RIS_Report"."MZYSXM" IS '麻醉医生姓名';
COMMENT ON COLUMN "TB_RIS_Report"."JCBGDBH" IS '检查报告单编号';
COMMENT ON COLUMN "TB_RIS_Report"."JCKS" IS '检查科室编码';
COMMENT ON COLUMN "TB_RIS_Report"."JCKSMC" IS '检查科室名称';
COMMENT ON COLUMN "TB_RIS_Report"."JCYS" IS '检查医生姓名';
COMMENT ON COLUMN "TB_RIS_Report"."JCYSGH" IS '检查医生编号';
COMMENT ON COLUMN "TB_RIS_Report"."JCYSSFZHM" IS '检查医生身份证号码';
COMMENT ON COLUMN "TB_RIS_Report"."BGRQ" IS '报告日期';
COMMENT ON COLUMN "TB_RIS_Report"."BGSJ" IS '报告时间';
COMMENT ON COLUMN "TB_RIS_Report"."BGRGH" IS '报告人编号';
COMMENT ON COLUMN "TB_RIS_Report"."BGRXM" IS '报告人姓名';
COMMENT ON COLUMN "TB_RIS_Report"."BGYSSFZHM" IS '报告医师身份证号码';
COMMENT ON COLUMN "TB_RIS_Report"."SHRGH" IS '审核人编号';
COMMENT ON COLUMN "TB_RIS_Report"."SHRXM" IS '审核人姓名';
COMMENT ON COLUMN "TB_RIS_Report"."SHYSSFZHM" IS '审核医师身份号码';
COMMENT ON COLUMN "TB_RIS_Report"."JCBW" IS '检查部位';
COMMENT ON COLUMN "TB_RIS_Report"."BWACR" IS '检查部位 ACR 编码';
COMMENT ON COLUMN "TB_RIS_Report"."YYS" IS '阴阳性';
COMMENT ON COLUMN "TB_RIS_Report"."JCJGDM" IS '检查结果代码';
COMMENT ON COLUMN "TB_RIS_Report"."BGLCZD" IS '报告临床诊断';
COMMENT ON COLUMN "TB_RIS_Report"."JCFY" IS '检查费用';
COMMENT ON COLUMN "TB_RIS_Report"."YXBX" IS '影像表现或检查所见';
COMMENT ON COLUMN "TB_RIS_Report"."YXZD" IS '检查诊断或提示';
COMMENT ON COLUMN "TB_RIS_Report"."BZHJY" IS '说明或建议';
COMMENT ON COLUMN "TB_RIS_Report"."SFYYY" IS '是否有影像';
COMMENT ON COLUMN "TB_RIS_Report"."WJZBS" IS '危急值标识';
COMMENT ON COLUMN "TB_RIS_Report"."WJZBGRQ" IS '危急值报告日期';
COMMENT ON COLUMN "TB_RIS_Report"."JLDW" IS '计量单位';
COMMENT ON COLUMN "TB_RIS_Report"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_RIS_Report"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_RIS_Report"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_RIS_Report"."YLYL2" IS '预留二';
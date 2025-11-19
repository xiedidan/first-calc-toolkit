DROP TABLE IF EXISTS "TB_MZ_YPCFMX";
CREATE TABLE "TB_MZ_YPCFMX" (
    "YLJGDM" varchar(33),
    "CFMXID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "CFZID" varchar(54),
    "YZXH" numeric,
    "YZZH" varchar(75),
    "ZLXMLBBM" varchar(6),
    "XMBZBM" varchar(3),
    "XMBM" varchar(54),
    "XMMC" varchar(96),
    "SYPBM" varchar(54),
    "SYPMC" varchar(96),
    "YNSFXMBM" varchar(75),
    "YNSFXMMC" varchar(300),
    "XMFLBM" varchar(48),
    "XMFLMC" varchar(75),
    "JYLX" varchar(2),
    "CPSD" varchar(9),
    "JXDM" varchar(6),
    "YPGG" varchar(96),
    "YF" varchar(6),
    "YYPCDM" varchar(6),
    "SYPC" varchar(48),
    "SYCJL" numeric,
    "SJYLDW" varchar(24),
    "SYZL" numeric,
    "SYZLDW" varchar(15),
    "YPSL" numeric,
    "YPDW" varchar(15),
    "YYTS" numeric,
    "ZYJZF" varchar(45),
    "YZKSSJ" timestamp,
    "YZTZSJ" timestamp,
    "ZXKSBM" varchar(96),
    "ZXKSMC" varchar(114),
    "ZXRGH" varchar(54),
    "ZXRXM" varchar(108),
    "YZZXSJ" timestamp,
    "BZ" varchar(192),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_YPCFMX" IS '门诊药品处方明细表';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."CFMXID" IS '处方明细 ID';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."CFZID" IS '处方主 ID';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YZXH" IS '医嘱序号';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YZZH" IS '医嘱组号';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZLXMLBBM" IS '诊疗项目类别编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XMBZBM" IS '项目标准编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XMBM" IS '项目编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XMMC" IS '项目名称';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYPBM" IS '省药品编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYPMC" IS '省药品名称';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YNSFXMBM" IS '院内收费项目编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YNSFXMMC" IS '院内收费项目名称';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XMFLBM" IS '项目分类编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XMFLMC" IS '项目分类名称';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."JYLX" IS '基药类型';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."CPSD" IS '产品属地';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."JXDM" IS '剂型代码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YPGG" IS '药品规格';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YF" IS '用药途径代码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YYPCDM" IS '用药频次代码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYPC" IS '用药频次';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYCJL" IS '使用次剂量';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SJYLDW" IS '使用剂量单位';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYZL" IS '使用总量';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."SYZLDW" IS '使用总量单位';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YPSL" IS '发药数量';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YPDW" IS '发药数量单位';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YYTS" IS '用药天数';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZYJZF" IS '中药煎煮法';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YZKSSJ" IS '医嘱开始时间';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YZTZSJ" IS '医嘱停止时间';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZXRGH" IS '医嘱执行人编号';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."ZXRXM" IS '医嘱执行人姓名';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YZZXSJ" IS '医嘱执行时间';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_YPCFMX"."YLYL2" IS '预留二';
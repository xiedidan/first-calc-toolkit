DROP TABLE IF EXISTS "TB_ZY_YPYZMX";
CREATE TABLE "TB_ZY_YPYZMX" (
    "YLJGDM" varchar(33),
    "YZID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "YZZID" varchar(54),
    "CXBZ" varchar(2),
    "YZKSSJ" timestamp,
    "YZJDHSGH" varchar(54),
    "YZJDHSXM" varchar(108),
    "YZJDHSSFZHM" varchar(27),
    "YZJDSJ" timestamp,
    "TZYSGH" varchar(54),
    "TZYSXM" varchar(108),
    "TZYSSFZHM" varchar(27),
    "YSTZSJ" timestamp,
    "QRTZHSGH" varchar(54),
    "QRTZHSXM" varchar(108),
    "QRTZHSSFZHM" varchar(27),
    "HSQRTZSJ" timestamp,
    "ZXKSBM" varchar(96),
    "ZXKSMC" varchar(114),
    "ZXRGH" varchar(54),
    "ZXRXM" varchar(48),
    "ZXRSFZHM" varchar(27),
    "YZZXSJ" timestamp,
    "YZZZSJ" timestamp,
    "YZSM" varchar(750),
    "YZXH" numeric,
    "YZZH" varchar(75),
    "ZLXMBZBM" varchar(3),
    "JXDM" varchar(6),
    "JXMC" varchar(45),
    "YZMXBM" varchar(54),
    "YZMXMC" varchar(384),
    "SMXBM" varchar(54),
    "SMXMC" varchar(384),
    "YNSFXMBM" varchar(75),
    "YNSFXMMC" varchar(300),
    "YZXMFLDM" varchar(48),
    "YZXMFLMC" varchar(384),
    "ZLXMLBBM" varchar(6),
    "JYLX" varchar(2),
    "CPSD" varchar(9),
    "YPGG" varchar(48),
    "YZYF" varchar(48),
    "YYPCDM" varchar(6),
    "YZPD" varchar(48),
    "JL" numeric,
    "DW" varchar(24),
    "YPSL" numeric,
    "YPDW" varchar(30),
    "YYTS" numeric,
    "SFPS" varchar(2),
    "ZYJZF" varchar(45),
    "BZ" varchar(1536),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_YPYZMX" IS '住院药品医嘱明细表';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZID" IS '医嘱明细 ID';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZZID" IS '医嘱主 ID';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."CXBZ" IS '撤销标志';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZKSSJ" IS '医嘱开始时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZJDHSGH" IS '医嘱校对护士编号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZJDHSXM" IS '医嘱校对护士姓名';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZJDHSSFZHM" IS '医嘱校对护士身份证号码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZJDSJ" IS '医嘱校对时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."TZYSGH" IS '停嘱医师编号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."TZYSXM" IS '停嘱医师姓名';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."TZYSSFZHM" IS '停嘱医师身份证号码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YSTZSJ" IS '医师停嘱时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."QRTZHSGH" IS '确认停嘱护士编号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."QRTZHSXM" IS '确认停嘱护士姓名';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."QRTZHSSFZHM" IS '确认停嘱护士身份证号码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."HSQRTZSJ" IS '护士确认停嘱时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZXRGH" IS '医嘱执行人编号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZXRXM" IS '医嘱执行人姓名';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZXRSFZHM" IS '医嘱执行人身份证号码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZZXSJ" IS '医嘱执行时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZZZSJ" IS '医嘱终止时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZSM" IS '医嘱说明';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZXH" IS '医嘱序号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZZH" IS '医嘱组号';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZLXMBZBM" IS '诊疗项目标准编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."JXDM" IS '剂型代码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."JXMC" IS '剂型名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZMXBM" IS '医嘱明细编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZMXMC" IS '医嘱明细名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."SMXBM" IS '省明细编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."SMXMC" IS '省明细名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YNSFXMBM" IS '院内收费项目编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YNSFXMMC" IS '院内收费项目名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZXMFLDM" IS '医嘱项目分类编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZXMFLMC" IS '医嘱项目分类名称';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZLXMLBBM" IS '诊疗项目类别编码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."JYLX" IS '基药类型';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."CPSD" IS '产品属地';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YPGG" IS '药品规格';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZYF" IS '医嘱用法';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YYPCDM" IS '用药频次代码';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YZPD" IS '医嘱频度';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."JL" IS '每次使用剂量';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."DW" IS '每次使用剂量单位';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YPSL" IS '发药数量';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YPDW" IS '发药数量单位';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YYTS" IS '用药天数';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."SFPS" IS '皮试判别';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."ZYJZF" IS '中药煎煮法';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_YPYZMX"."YLYL2" IS '预留二';
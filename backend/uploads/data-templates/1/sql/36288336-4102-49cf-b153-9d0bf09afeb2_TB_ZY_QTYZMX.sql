DROP TABLE IF EXISTS "TB_ZY_QTYZMX";
CREATE TABLE "TB_ZY_QTYZMX" (
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
    "ZXRXM" varchar(108),
    "YZZXRSFZHM" varchar(27),
    "YZZXSJ" timestamp,
    "YZZZSJ" timestamp,
    "YZSM" varchar(750),
    "YZXH" numeric,
    "YZZH" varchar(75),
    "ZLXMBZBM" varchar(3),
    "YZMXBM" varchar(54),
    "YZMXMC" varchar(384),
    "YNMXBM" varchar(54),
    "YNMXMC" varchar(384),
    "YZXMFLDM" varchar(48),
    "YZXMFLMC" varchar(384),
    "ZLXMLBBM" varchar(6),
    "ZXPL" varchar(6),
    "CJFX" varchar(150),
    "CJBB" varchar(150),
    "JCBW" varchar(150),
    "MZFS" varchar(150),
    "BZ" varchar(1536),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_QTYZMX" IS '住院其他医嘱明细表';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZID" IS '医嘱明细 ID';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZZID" IS '医嘱主 ID';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."CXBZ" IS '撤销标志';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZKSSJ" IS '医嘱开始时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZJDHSGH" IS '医嘱校对护士编号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZJDHSXM" IS '医嘱校对护士姓名';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZJDHSSFZHM" IS '医嘱校对护士身份证号码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZJDSJ" IS '医嘱校对时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."TZYSGH" IS '停嘱医师编号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."TZYSXM" IS '停嘱医师姓名';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."TZYSSFZHM" IS '停嘱医师身份证号码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YSTZSJ" IS '医师停嘱时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."QRTZHSGH" IS '确认停嘱护士编号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."QRTZHSXM" IS '确认停嘱护士姓名';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."QRTZHSSFZHM" IS '确认停嘱护士身份证号码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."HSQRTZSJ" IS '护士确认停嘱时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZXRGH" IS '医嘱执行人编号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZXRXM" IS '医嘱执行人姓名';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZZXRSFZHM" IS '医嘱执行人身份证号码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZZXSJ" IS '医嘱执行时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZZZSJ" IS '医嘱终止时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZSM" IS '医嘱说明';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZXH" IS '医嘱序号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZZH" IS '医嘱组号';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZLXMBZBM" IS '诊疗项目标准编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZMXBM" IS '医嘱明细编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZMXMC" IS '医嘱明细名称';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YNMXBM" IS '院内明细编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YNMXMC" IS '院内明细名称';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZXMFLDM" IS '医嘱项目分类编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YZXMFLMC" IS '医嘱项目分类名称';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZLXMLBBM" IS '诊疗项目类别编码';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."ZXPL" IS '执行频率';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."CJFX" IS '采集方式';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."CJBB" IS '采标标本';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."JCBW" IS '检查部位';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."MZFS" IS '麻醉方式';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_QTYZMX"."YLYL2" IS '预留二';
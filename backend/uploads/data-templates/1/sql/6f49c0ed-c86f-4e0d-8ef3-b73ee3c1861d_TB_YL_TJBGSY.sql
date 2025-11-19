DROP TABLE IF EXISTS "TB_YL_TJBGSY";
CREATE TABLE "TB_YL_TJBGSY" (
    "YLJGDM" varchar(33),
    "TJBH" varchar(75),
    "TJLBDM" varchar(2),
    "SCTJSJ" timestamp,
    "BRZSY" varchar(96),
    "XM" varchar(108),
    "XB" varchar(2),
    "NL" varchar(15),
    "CSRQ" timestamp,
    "GRDHHM" varchar(30),
    "HYZK" varchar(3),
    "ZYMC" varchar(150),
    "ZYLBDM" varchar(15),
    "SHXG_GZYD" varchar(768),
    "SHXG_SM" varchar(768),
    "SHXG_YSQK" varchar(768),
    "SHXG_J" varchar(768),
    "CHHZJB" varchar(768),
    "CZGHZSS" varchar(768),
    "WSS" varchar(768),
    "JSCS" varchar(768),
    "NSYJSCC" varchar(768),
    "NSYJSZQ" numeric,
    "NSYJS_BD" varchar(768),
    "NSYJS_JJ" varchar(768),
    "NSYJS_LC" varchar(768),
    "SCS" varchar(768),
    "JTS" varchar(768),
    "GMS" varchar(768),
    "ZZDMJKJC" varchar(60),
    "JKWSYY" varchar(60),
    "QTJKWSYY" varchar(150),
    "ZRYSXM" varchar(108),
    "ZJJG" varchar(1536),
    "JY" varchar(1536),
    "ZJRQ" timestamp,
    "ZJYSGH" varchar(54),
    "ZJYS" varchar(108),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YL_TJBGSY" IS '报告首页';
COMMENT ON COLUMN "TB_YL_TJBGSY"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_YL_TJBGSY"."TJBH" IS '体检编号';
COMMENT ON COLUMN "TB_YL_TJBGSY"."TJLBDM" IS '体检类别代码';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SCTJSJ" IS '上次体检时间';
COMMENT ON COLUMN "TB_YL_TJBGSY"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_YL_TJBGSY"."XM" IS '姓名';
COMMENT ON COLUMN "TB_YL_TJBGSY"."XB" IS '性别';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NL" IS '年龄';
COMMENT ON COLUMN "TB_YL_TJBGSY"."CSRQ" IS '出生日期';
COMMENT ON COLUMN "TB_YL_TJBGSY"."GRDHHM" IS '个人电话号码';
COMMENT ON COLUMN "TB_YL_TJBGSY"."HYZK" IS '婚姻状况';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZYMC" IS '职业名称';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZYLBDM" IS '职业类别代码';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SHXG_GZYD" IS '生活习惯-工作运动';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SHXG_SM" IS '生活习惯-睡眠';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SHXG_YSQK" IS '生活习惯-饮食情况';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SHXG_J" IS '生活习惯-其它';
COMMENT ON COLUMN "TB_YL_TJBGSY"."CHHZJB" IS '曾患何种疾病';
COMMENT ON COLUMN "TB_YL_TJBGSY"."CZGHZSS" IS '曾做过何种手术';
COMMENT ON COLUMN "TB_YL_TJBGSY"."WSS" IS '外伤史';
COMMENT ON COLUMN "TB_YL_TJBGSY"."JSCS" IS '精神创伤史';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NSYJSCC" IS '女士月经初潮';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NSYJSZQ" IS '女士月经周期';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NSYJS_BD" IS '女士月经史-白带';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NSYJS_JJ" IS '女士月经史-绝经';
COMMENT ON COLUMN "TB_YL_TJBGSY"."NSYJS_LC" IS '女士月经史-流产';
COMMENT ON COLUMN "TB_YL_TJBGSY"."SCS" IS '生产史';
COMMENT ON COLUMN "TB_YL_TJBGSY"."JTS" IS '家庭史';
COMMENT ON COLUMN "TB_YL_TJBGSY"."GMS" IS '过敏史';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZZDMJKJC" IS '症状代码(健康检查)';
COMMENT ON COLUMN "TB_YL_TJBGSY"."JKWSYY" IS '健康危险因素';
COMMENT ON COLUMN "TB_YL_TJBGSY"."QTJKWSYY" IS '其他健康危险因素';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZRYSXM" IS '责任医师姓名';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZJJG" IS '总检结果';
COMMENT ON COLUMN "TB_YL_TJBGSY"."JY" IS '建议';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZJRQ" IS '总检日期';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZJYSGH" IS '总检医生编号';
COMMENT ON COLUMN "TB_YL_TJBGSY"."ZJYS" IS '总检医生姓名';
COMMENT ON COLUMN "TB_YL_TJBGSY"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YL_TJBGSY"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YL_TJBGSY"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YL_TJBGSY"."YLYL2" IS '预留二';
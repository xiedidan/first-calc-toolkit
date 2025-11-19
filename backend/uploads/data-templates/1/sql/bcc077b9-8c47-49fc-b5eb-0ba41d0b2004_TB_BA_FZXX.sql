DROP TABLE IF EXISTS "TB_BA_FZXX";
CREATE TABLE "TB_BA_FZXX" (
    "YLJGDM" varchar(33),
    "FZID" varchar(96),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "XX" varchar(3),
    "RH" varchar(2),
    "ILSSQKYFXYYKJ" varchar(2),
    "SYCXSS" numeric,
    "LHYY" varchar(2),
    "SFSSLCLJGL" varchar(2),
    "SFWCLCHL" varchar(2),
    "TCLCLJYY" varchar(384),
    "SFBY" varchar(2),
    "BYYY" varchar(384),
    "ISJGZYZJ" varchar(2),
    "ZYQJSFXGZQGZ" varchar(2),
    "RZZZJHBF" varchar(2),
    "SFBZSYZCY" varchar(2),
    "ISZYZLSB" varchar(2),
    "ISZYZLJS" varchar(2),
    "ISBZSH" varchar(2),
    "SSZD" varchar(1500),
    "SSZDBM" varchar(15),
    "YWGMBZ" numeric,
    "YWGM" varchar(384),
    "BLZD" varchar(48),
    "BLZDJBBM" varchar(48),
    "BLH" varchar(48),
    "TNMFQ" varchar(2),
    "QJCS" numeric,
    "CGCS" numeric,
    "SFCXWJN" varchar(5),
    "HXBSXL" numeric,
    "XXBSXL" numeric,
    "XJSXL" numeric,
    "QXSXL" numeric,
    "QTSXL" numeric,
    "SXFYBZ" varchar(2),
    "SZ" varchar(2),
    "SZQX" numeric,
    "SZQXDW" varchar(2),
    "SJ" varchar(2),
    "RSMDSC" varchar(2),
    "XSEJBSC" varchar(5),
    "RSCX" varchar(2),
    "RSCXL" numeric,
    "KZRXM" varchar(108),
    "KZRGH" varchar(54),
    "ZRYSGH" varchar(54),
    "ZRYSXM" varchar(108),
    "ZZDYSGH" varchar(54),
    "ZZDYSXM" varchar(108),
    "ZZYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "HSZGH" varchar(54),
    "HSZXM" varchar(108),
    "ZRHSGH" varchar(54),
    "ZRHSXM" varchar(108),
    "KZRZSBM" varchar(45),
    "ZRYSZSBM" varchar(45),
    "ZZYSZSBM" varchar(45),
    "ZYYSZSBM" varchar(45),
    "HSZZSBM" varchar(45),
    "ZRHSZSBM" varchar(45),
    "JXYSGH" varchar(54),
    "JXYSXM" varchar(108),
    "SXYSGH" varchar(54),
    "SXYSXM" varchar(108),
    "BMYGH" varchar(54),
    "BMYXM" varchar(108),
    "BAZLDM" varchar(2),
    "BAZLMC" varchar(15),
    "ZKYSGH" varchar(54),
    "ZKYSXM" varchar(108),
    "ZKHSGH" varchar(54),
    "ZKHSZM" varchar(108),
    "ZKRQ" timestamp,
    "LYFSDM" varchar(2),
    "LYFSMC" varchar(48),
    "NJSYYMC" varchar(48),
    "ZZYJH_31" varchar(2),
    "ZZYJHMD" varchar(48),
    "RYQHMSJ" varchar(30),
    "RYHHMSJ" varchar(30),
    "ZYZJF" numeric,
    "KJYWSYQK" varchar(2),
    "SYFY" varchar(2),
    "YFFYYW" varchar(48),
    "SYFYLCBX" varchar(48),
    "ZYDDHZCSH" varchar(2),
    "DDHZCYY" varchar(2),
    "YYGRQK" varchar(2),
    "GRBW" varchar(48),
    "YYGRMC" varchar(48),
    "DWFZRGH" varchar(54),
    "DWFZRXM" varchar(108),
    "TJFZRGH" varchar(54),
    "TJFZRXM" varchar(108),
    "TBRGH" varchar(54),
    "TBRXM" varchar(108),
    "LXDH" varchar(48),
    "BCRQ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_FZXX" IS '住院病案辅助信息';
COMMENT ON COLUMN "TB_BA_FZXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_FZXX"."FZID" IS '辅助 ID';
COMMENT ON COLUMN "TB_BA_FZXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_FZXX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_FZXX"."XX" IS '血型';
COMMENT ON COLUMN "TB_BA_FZXX"."RH" IS 'Rh';
COMMENT ON COLUMN "TB_BA_FZXX"."ILSSQKYFXYYKJ" IS 'I 类手术切口预防性应用抗菌药物';
COMMENT ON COLUMN "TB_BA_FZXX"."SYCXSS" IS '使用持续时间';
COMMENT ON COLUMN "TB_BA_FZXX"."LHYY" IS '联合用药';
COMMENT ON COLUMN "TB_BA_FZXX"."SFSSLCLJGL" IS '是否实施临床路径管理';
COMMENT ON COLUMN "TB_BA_FZXX"."SFWCLCHL" IS '是否完成临床路径';
COMMENT ON COLUMN "TB_BA_FZXX"."TCLCLJYY" IS '推出临床路径原因';
COMMENT ON COLUMN "TB_BA_FZXX"."SFBY" IS '是否变异';
COMMENT ON COLUMN "TB_BA_FZXX"."BYYY" IS '变异原因';
COMMENT ON COLUMN "TB_BA_FZXX"."ISJGZYZJ" IS '使用医疗机构中药制剂';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYQJSFXGZQGZ" IS '住院期间是否相关知情告知';
COMMENT ON COLUMN "TB_BA_FZXX"."RZZZJHBF" IS '入住重症监护病房';
COMMENT ON COLUMN "TB_BA_FZXX"."SFBZSYZCY" IS '是否辩证使用中成药';
COMMENT ON COLUMN "TB_BA_FZXX"."ISZYZLSB" IS '使用中医诊疗设备';
COMMENT ON COLUMN "TB_BA_FZXX"."ISZYZLJS" IS '使用中医诊疗技术';
COMMENT ON COLUMN "TB_BA_FZXX"."ISBZSH" IS '辨证施护';
COMMENT ON COLUMN "TB_BA_FZXX"."SSZD" IS '损伤中毒的外部原因';
COMMENT ON COLUMN "TB_BA_FZXX"."SSZDBM" IS '损伤中毒的外部原因的疾病编码';
COMMENT ON COLUMN "TB_BA_FZXX"."YWGMBZ" IS '药物过敏标志';
COMMENT ON COLUMN "TB_BA_FZXX"."YWGM" IS '药物过敏';
COMMENT ON COLUMN "TB_BA_FZXX"."BLZD" IS '病理诊断';
COMMENT ON COLUMN "TB_BA_FZXX"."BLZDJBBM" IS '病理诊断疾病编码';
COMMENT ON COLUMN "TB_BA_FZXX"."BLH" IS '病理号';
COMMENT ON COLUMN "TB_BA_FZXX"."TNMFQ" IS 'TNM 分期';
COMMENT ON COLUMN "TB_BA_FZXX"."QJCS" IS '抢救次数';
COMMENT ON COLUMN "TB_BA_FZXX"."CGCS" IS '成功次数';
COMMENT ON COLUMN "TB_BA_FZXX"."SFCXWJN" IS '住院是否出现危重、急症、疑难';
COMMENT ON COLUMN "TB_BA_FZXX"."HXBSXL" IS '红细胞输血量';
COMMENT ON COLUMN "TB_BA_FZXX"."XXBSXL" IS '血小板输血量';
COMMENT ON COLUMN "TB_BA_FZXX"."XJSXL" IS '血浆输血量';
COMMENT ON COLUMN "TB_BA_FZXX"."QXSXL" IS '全血输血量';
COMMENT ON COLUMN "TB_BA_FZXX"."QTSXL" IS '其它输血量';
COMMENT ON COLUMN "TB_BA_FZXX"."SXFYBZ" IS '输血反应标志';
COMMENT ON COLUMN "TB_BA_FZXX"."SZ" IS '是否随诊';
COMMENT ON COLUMN "TB_BA_FZXX"."SZQX" IS '随诊期限';
COMMENT ON COLUMN "TB_BA_FZXX"."SZQXDW" IS '随诊期限单位';
COMMENT ON COLUMN "TB_BA_FZXX"."SJ" IS '（死亡患者）是否尸检';
COMMENT ON COLUMN "TB_BA_FZXX"."RSMDSC" IS '是否妊娠梅毒筛查';
COMMENT ON COLUMN "TB_BA_FZXX"."XSEJBSC" IS '新生儿疾病筛查';
COMMENT ON COLUMN "TB_BA_FZXX"."RSCX" IS '妊娠出血';
COMMENT ON COLUMN "TB_BA_FZXX"."RSCXL" IS '妊娠出血量';
COMMENT ON COLUMN "TB_BA_FZXX"."KZRXM" IS '科主任姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."KZRGH" IS '科主任编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRYSGH" IS '主任医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRYSXM" IS '主任医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZDYSGH" IS '主诊医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZDYSXM" IS '主诊医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."HSZGH" IS '护士长编号';
COMMENT ON COLUMN "TB_BA_FZXX"."HSZXM" IS '护士长姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRHSGH" IS '责任护士编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRHSXM" IS '责任护士姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."KZRZSBM" IS '科主任执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRYSZSBM" IS '主任医师执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZYSZSBM" IS '主治医师执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYYSZSBM" IS '住院医师执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."HSZZSBM" IS '护士长执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."ZRHSZSBM" IS '责任护士执业证书编码';
COMMENT ON COLUMN "TB_BA_FZXX"."JXYSGH" IS '进修医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."JXYSXM" IS '进修医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."SXYSGH" IS '实习医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."SXYSXM" IS '实习医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."BMYGH" IS '编码员编号';
COMMENT ON COLUMN "TB_BA_FZXX"."BMYXM" IS '编码员姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."BAZLDM" IS '病案质量代码';
COMMENT ON COLUMN "TB_BA_FZXX"."BAZLMC" IS '病案质量名称';
COMMENT ON COLUMN "TB_BA_FZXX"."ZKYSGH" IS '质控医师编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZKYSXM" IS '质控医师姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZKHSGH" IS '质控护士编号';
COMMENT ON COLUMN "TB_BA_FZXX"."ZKHSZM" IS '质控护士姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."ZKRQ" IS '质控日期';
COMMENT ON COLUMN "TB_BA_FZXX"."LYFSDM" IS '离院方式代码';
COMMENT ON COLUMN "TB_BA_FZXX"."LYFSMC" IS '离院方式名称';
COMMENT ON COLUMN "TB_BA_FZXX"."NJSYYMC" IS '离院后拟接收医疗机构名称';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZYJH_31" IS '是否有出院 31 天内再住院计划';
COMMENT ON COLUMN "TB_BA_FZXX"."ZZYJHMD" IS '再住院计划目的';
COMMENT ON COLUMN "TB_BA_FZXX"."RYQHMSJ" IS '颅脑损伤患者入院前昏迷时间';
COMMENT ON COLUMN "TB_BA_FZXX"."RYHHMSJ" IS '颅脑损伤患者入院后昏迷时间';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYZJF" IS '医疗机构中药制剂费';
COMMENT ON COLUMN "TB_BA_FZXX"."KJYWSYQK" IS '抗菌药物使用情况';
COMMENT ON COLUMN "TB_BA_FZXX"."SYFY" IS '输液反应';
COMMENT ON COLUMN "TB_BA_FZXX"."YFFYYW" IS '引发反应的药物';
COMMENT ON COLUMN "TB_BA_FZXX"."SYFYLCBX" IS '输液反应临床表现';
COMMENT ON COLUMN "TB_BA_FZXX"."ZYDDHZCSH" IS '住院有无跌倒或坠床及伤害程度';
COMMENT ON COLUMN "TB_BA_FZXX"."DDHZCYY" IS '跌倒或坠床原因';
COMMENT ON COLUMN "TB_BA_FZXX"."YYGRQK" IS '医院感染情况';
COMMENT ON COLUMN "TB_BA_FZXX"."GRBW" IS '感染部位';
COMMENT ON COLUMN "TB_BA_FZXX"."YYGRMC" IS '医院感染名称';
COMMENT ON COLUMN "TB_BA_FZXX"."DWFZRGH" IS '单位负责人编号';
COMMENT ON COLUMN "TB_BA_FZXX"."DWFZRXM" IS '单位负责人姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."TJFZRGH" IS '统计负责人编号';
COMMENT ON COLUMN "TB_BA_FZXX"."TJFZRXM" IS '统计负责人姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."TBRGH" IS '填报人编号';
COMMENT ON COLUMN "TB_BA_FZXX"."TBRXM" IS '填报人姓名';
COMMENT ON COLUMN "TB_BA_FZXX"."LXDH" IS '填报人联系电话';
COMMENT ON COLUMN "TB_BA_FZXX"."BCRQ" IS '报出日期';
COMMENT ON COLUMN "TB_BA_FZXX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_FZXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_FZXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_FZXX"."YLYL2" IS '预留二';